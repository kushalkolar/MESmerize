"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import os

# disable tf deprecation warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import tifffile
from matplotlib import pyplot as plt
import skimage.exposure
import skimage.morphology
import numpy as np
import numexpr
from nuset import Nuset
from tqdm import tqdm
from typing import List, Tuple
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from multiprocessing import Pool, cpu_count
from scipy.ndimage import label as label_image, generate_binary_structure
from joblib import Parallel, delayed
import scipy.sparse
from scipy.spatial import cKDTree, ConvexHull
from scipy.spatial.qhull import QhullError

from PyQt5 import QtWidgets, QtCore, QtGui
from qtap import Function
from ..core import ViewerUtils, ViewerWorkEnv
from ...pyqtgraphCore import GraphicsLayoutWidget, ImageItem, ViewBox
from ...pyqtgraphCore.console.Console import ConsoleWidget
from ...common.qdialogs import *
from ...common.configuration import console_history_path
from ...common.utils import HdfTools

cmap_magenta = LinearSegmentedColormap.from_list('magentas', [(0, 0, 0), (0,)*3, (1, 0, 1)])
cmap_cyan = LinearSegmentedColormap.from_list('cyans', [(0, 0, 0), (0,)*3, (0, 1, 1)])


def get_projection(img: np.ndarray, proj: str = 'std') -> np.ndarray:
    func = getattr(np, proj)

    return func(img, axis=2)


def get_preprocess(
        img: np.ndarray,
        do_preprocess: bool = True,
        do_sigmoid: bool = True,
        sigmoid_cutoff: float = 40.0,
        sigmoid_gain: float = 0.10,
        sigmoid_invert: bool = False,
        do_equalize: bool = False,
        equalize_lower: float = -0.1,
        equalize_upper: float = 1.0,
        equalize_kernel: int = 8,
) -> np.ndarray:
    """

    :param img: input image
    :param do_sigmoid: Perform sigmoid correction
    :param sigmoid_cutoff: sigmoid cutoff
    :param sigmoid_gain: sigmoid gain
    :param sigmoid_invert: invert after sigmoid correction (necessary sometimes)
    :param do_equalize: Perform histogram equalization
    :param equalize_kernel: Size of equalization kernel
    :return: preprocessed image
    """
    if not do_preprocess:
        return normalize_image(img, np.float32)

    img = img.astype(np.float32)

    if do_sigmoid:
        img = skimage.exposure.adjust_sigmoid(
            img,
            cutoff=sigmoid_cutoff,
            gain=sigmoid_gain,
            inv=sigmoid_invert
        )

    if do_equalize:
        # equalize_hist need floats that stay in the range of -1 to 1
        rng = (equalize_lower, equalize_upper)  # user specified range

        min_t = np.nanmin(img)
        max_t = np.nanmax(img)
        range_t = max_t - min_t
        nomin = (img - min_t) * (rng[1] - rng[0])
        img = nomin / range_t + rng[0]  # normalized img
        img = skimage.exposure.equalize_adapthist(img, kernel_size=equalize_kernel)

    # float32 is best for GPU I think?
    img = normalize_image(img, np.float32)

    return img


def wrap_preprocess(kwargs):
    return get_preprocess(**kwargs)


# from NuSeT processing cleanimage function
def get_postprocess(
        img: np.ndarray,
        do_postprocess: bool = False,
        abs_obj_threshold: int = -1,
        rel_obj_threshold: int = -1,
        obj_connectivity: int = 2,
        abs_hol_threshold: int = -1,
        rel_hol_threshold: int = 1,
        hol_connectivity: int = 2
    ) -> np.ndarray:

    if not do_postprocess:
        return img

    if not img.size > 0:
        return img

    image = img.astype(np.bool)
    im_label = skimage.morphology.label(image, connectivity=1)
    num_cells = np.max(im_label)
    mean_area = np.sum(image).astype(np.float32) / num_cells

    if rel_obj_threshold != -1:
        min_obj_size = mean_area / rel_obj_threshold
    elif abs_hol_threshold != -1:
        min_obj_size = abs_obj_threshold
    else:
        min_obj_size = 0
    image = skimage.morphology.remove_small_objects(image, min_size=min_obj_size, connectivity=obj_connectivity)

    if abs_hol_threshold == -1:
        min_hol_size = mean_area / rel_hol_threshold
    else:
        min_hol_size = abs_hol_threshold
    image = skimage.morphology.remove_small_holes(image, min_size=min_hol_size, connectivity=hol_connectivity)

    return image.astype(np.uint8)


# adapted from https://github.com/ver228/tierpsy-tracker/blob/master/tierpsy/analysis/compress/compressVideo.py
def normalize_image(img, dtype):
    # normalise image intensities between 0 and the max range of the dtype
    imax = (img.max() + np.abs(img.min())).astype(dtype)
    # we will set the values between 0 and max value of the float/int type
    imin = 0

    # max value of the dtype
    if np.issubdtype(dtype, np.floating):
        factor = (np.finfo(dtype).max - 1) / (imax - imin)
    elif np.issubdtype(dtype, np.integer):
        factor = (np.iinfo(dtype).max - 1) / (imax - imin)

    imgN = numexpr.evaluate('(img-imin)*factor')
    imgN = imgN.astype(dtype)

    return imgN


# adapted from skimage.morphology.remove_small_objects
def remove_large_objects(ar, max_size=128, connectivity=1):
    if max_size == -1:  # shortcut for efficiency
        return ar

    out = ar.copy()

    if out.dtype == bool:
        selem = generate_binary_structure(ar.ndim, connectivity)
        ccs = np.zeros_like(ar, dtype=np.int32)
        label_image(ar, selem, output=ccs)
    else:
        ccs = out

    try:
        component_sizes = np.bincount(ccs.ravel())
    except ValueError:
        raise ValueError("Negative value labels are not supported. Try "
                         "relabeling the input with `scipy.ndimage.label` or "
                         "`skimage.morphology.label`.")

    too_big = component_sizes > max_size
    too_big_mask = too_big[ccs]
    out[too_big_mask] = 0

    return out


def _get_sparse_mask(areas, i, edge_method, selem):
    temp = (areas[0] == i + 1)
    edge_func = getattr(skimage.morphology, edge_method)
    temp = edge_func(temp, selem=selem)

    return scipy.sparse.csr_matrix(temp.flatten('F'))


# adapted from https://github.com/flatironinstitute/CaImAn/blob/master/caiman/base/rois.py#L88
def get_sparse_masks(
        segmented_img: np.ndarray,
        raw_img_shape: tuple,
        edge_method: str,
        selem: int,
        transpose=True
    ) -> np.ndarray:
    # allocate array with same size as the raw input image
    # so that the dims match for CNMF
    img = np.zeros(raw_img_shape, dtype=segmented_img.dtype)

    # fill the allocated array with vals from the NuSeT segmentation
    # sometimes the segmented image has its dims trimmed by a few pixels
    if len(raw_img_shape) == 3:
        img[:, :segmented_img.shape[1], :segmented_img.shape[2]] = segmented_img
        struc = np.array(
            [[[0, 0, 0],
              [0, 0, 0],
              [0, 0, 0]],
             [[1, 1, 1],
              [1, 1, 1],
              [1, 1, 1]],
             [[0, 0, 0],
              [0, 0, 0],
              [0, 0, 0]]]
        )

    else:
        img[:segmented_img.shape[0], :segmented_img.shape[1]] = segmented_img
        struc = None

    areas = label_image(img, structure=struc)
    # A = np.zeros((np.prod(img.shape), areas[1]), dtype=bool)

    selem: np.array = np.ones((selem,)*len(segmented_img.shape))

    if areas[1] < 50:
        print("Less than 50 regions, not parallelizing")
        sparses = []
        for i in tqdm(range(areas[1])):
            sparses.append(
                _get_sparse_mask(areas, i, edge_method, selem)
            )
    else:
        print("Greater than 50 regions, parallelizing with joblib")
        sparses = Parallel(n_jobs=cpu_count(), verbose=5)(
            delayed(_get_sparse_mask)(areas, i, edge_method, selem) for i in range(areas[1])
        )

    if transpose:
        return scipy.sparse.vstack(sparses).T.toarray()
    else:
        return scipy.sparse.vstack(sparses).toarray()


def get_colored_mask(m: np.ndarray, shape: tuple):
    random_colors = np.random.choice(range(24), m.shape[1], replace=True)

    colored_mask = np.zeros(shape, dtype=np.uint16)

    for i in tqdm(range(m.shape[1])):
        colored_mask[m[:, i].reshape(shape)] = random_colors[i]

    return colored_mask


def area_to_vertices(a: np.ndarray) -> np.ndarray:
    """
    Get the vertices of the area in a binary mask
    :param a: binary mask
    :return: 2D array of x-y coordinates for all the vertices of the area in the mask
    """
    xs, ys = np.where(a)

    points = np.array((xs, ys)).T

    kdt = cKDTree(points)
    vertices = []

    for p in points:
        if len(kdt.query_ball_point(p, 1)) < 5:
            vertices.append(p)

    vs = np.vstack(vertices)

    return vs


def area_to_hull(a: np.ndarray) -> np.ndarray:
    """
    Get the vertices of a convex hull generated from an area represented by a binary mask
    :param a: binary mask
    :return: 2D array of x-y coordinates for the hull vertices
    """
    xs, ys = np.where(a)
    points = np.array((xs, ys)).T
    hull = ConvexHull(points, qhull_options='Qs')
    vs = points[hull.vertices]
    return vs


class ModuleGUI(QtWidgets.QMainWindow):
    def __init__(self, parent, viewer_ref):
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('Nuset Segmentation')

        self.resize(1000, 900)
        self.menubar = self.menuBar()
        # self.setMenuBar(self.menubar)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 900))
        # self.menubar.setObjectName("menubar")


        self.widget = NusetWidget(self, viewer_ref)

        self.setCentralWidget(self.widget)

        self.dock_console = QtWidgets.QDockWidget(self)
        self.dock_console.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable
        )
        # self.dockWidgetContents = QtWidgets.QWidget()
        # self.dock_console.setWidget(self.dockWidgetContents)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dock_console)
        self.dock_console.hide()

        histfile = os.path.join(console_history_path, 'nuset_widget.pik')
        self.console_widget = ConsoleWidget(
            parent=self, namespace={'this': self.widget}, historyFile=histfile
        )
        self.dock_console.setWidget(self.console_widget)
        self.dock_console.setWindowTitle("Console")
        self.dock_console.hide()

        self.menu_export = self.menubar.addMenu('&Export')

        self.action_export_options = QtWidgets.QAction(text='Open Exporter')
        self.action_export_options.setToolTip(
            "Export as sparse matrix that can be used for \n"
            "seeding spatial components in Caiman CNMF"
        )
        self.menu_export.addAction(self.action_export_options)

        # self.action_export_cnmf_seeds = QtWidgets.QAction(text='CNMF seeds')
        # self.action_export_cnmf_seeds.setToolTip(
        #     "Export as sparse matrix that can be used for \n"
        #     "seeding spatial components in Caiman CNMF"
        # )
        # self.menu_export.addAction(self.action_export_cnmf_seeds)
        #
        # self.action_export_viewer = QtWidgets.QAction("Manual ROIs - Viewer")
        # self.menu_export.addAction(self.action_export_viewer)
        # self.action_export_viewer.setToolTip(
        #     "Export as Manual ROIs into the Viewer"
        # )

        self.menu_view = self.menubar.addMenu('&View')

        self.action_view_console = QtWidgets.QAction(text="Console")
        self.menu_view.addAction(self.action_view_console)
        self.action_view_console.setText("Console")
        self.action_view_console.setCheckable(True)
        self.action_view_console.setChecked(False)

        self.action_view_console.toggled.connect(
            lambda: self.dock_console.setVisible(
                self.action_view_console.isChecked()
            )
        )

        self.action_export_options.triggered.connect(self.widget.export_widget.show)


class ExportWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self)
        self.resize(600, 850)
        self.setWindowTitle('Nuset Exporter')
        self.nuset_widget: NusetWidget = parent

        self.vlayout = QtWidgets.QVBoxLayout(self)

        hlayout_threshold = QtWidgets.QHBoxLayout(self)
        label_threshold = QtWidgets.QLabel(self)
        label_threshold.setText("separation threshold:")
        hlayout_threshold.addWidget(label_threshold)

        # TODO: I should really use qtap here
        self.spinbox_thr = QtWidgets.QDoubleSpinBox(self)
        self.spinbox_thr.setMaximum(1.0)
        self.spinbox_thr.setMinimum(0.0)
        self.spinbox_thr.setValue(0.5)
        self.spinbox_thr.setSingleStep(0.1)
        self.spinbox_thr.setDecimals(2)
        self.spinbox_thr.setToolTip(
            "Threshold for cell separation"
        )
        hlayout_threshold.addWidget(self.spinbox_thr)
        hlayout_threshold.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        self.vlayout.addLayout(hlayout_threshold)

        # sliders are overrated
        # self.slider_thr = QtWidgets.QSlider(self, orientation=QtCore.Qt.Horizontal)
        # self.slider_thr.setMaximum(100)
        # self.slider_thr.setMinimum(0)
        # self.slider_thr.setValue(50)
        # self.slider_thr.setToolTip(
        #     "Threshold for cell separation"
        # )
        # self.slider_thr.valueChanged.connect(
        #     lambda v: self.spinbox_thr.setValue(float(v) / 100.0)
        # )
        # self.vlayout.addWidget(self.slider_thr)
        #
        # self.spinbox_thr.valueChanged.connect(
        #     lambda v: self.slider_thr.setValue(int(v * 100))
        # )

        hlayout_minmax_size = QtWidgets.QHBoxLayout(self)

        label_minsize = QtWidgets.QLabel(self)
        label_minsize.setText('min size (pixels)')
        label_minsize.setToolTip(
            "Minimum size for accepting an object, in pixels"
        )
        hlayout_minmax_size.addWidget(label_minsize)

        self.spinbox_minsize = QtWidgets.QSpinBox(self)
        self.spinbox_minsize.setMinimum(0)
        self.spinbox_minsize.setMaximum(999)
        self.spinbox_minsize.setValue(1)
        self.spinbox_minsize.setToolTip(
            "Minimum size for accepting an object, in pixels"
        )
        hlayout_minmax_size.addWidget(self.spinbox_minsize)


        label_maxsize = QtWidgets.QLabel(self)
        label_maxsize.setText("max size (pixels)")
        label_maxsize.setToolTip(
            "Maximum size of accepting an object, in pixels"
        )
        hlayout_minmax_size.addWidget(label_maxsize)

        self.spinbox_maxsize = QtWidgets.QSpinBox(self)
        self.spinbox_maxsize.setMinimum(-1)
        self.spinbox_maxsize.setMaximum(999999)
        self.spinbox_maxsize.setValue(-1)
        self.spinbox_maxsize.setToolTip(
            "Maximum size of accepting an object, in pixels.\nSet as -1 to disable."
        )

        hlayout_minmax_size.addWidget(self.spinbox_maxsize)
        hlayout_minmax_size.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        self.vlayout.addLayout(hlayout_minmax_size)

        hlayout_conn_struc = QtWidgets.QHBoxLayout(self)

        label_connectivity = QtWidgets.QLabel(self)
        label_connectivity.setText("connectivity")
        hlayout_conn_struc.addWidget(label_connectivity)

        self.spinbox_connectivity = QtWidgets.QSpinBox(self)
        self.spinbox_connectivity.setMinimum(1)
        self.spinbox_connectivity.setMaximum(99)
        self.spinbox_connectivity.setValue(1)
        self.spinbox_connectivity.setToolTip(
            "Connectivity around each pixel"
        )
        hlayout_conn_struc.addWidget(self.spinbox_connectivity)

        label_selem = QtWidgets.QLabel(self)
        label_selem.setText("structural_element")
        hlayout_conn_struc.addWidget(label_selem)

        self.spinbox_selem = QtWidgets.QSpinBox(self)
        self.spinbox_selem.setMinimum(0)
        self.spinbox_selem.setMaximum(50)
        self.spinbox_selem.setValue(3)
        hlayout_conn_struc.addWidget(self.spinbox_selem)

        hlayout_conn_struc.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        self.vlayout.addLayout(hlayout_conn_struc)

        hlayout_edge_multi_2d = QtWidgets.QHBoxLayout(self)

        label_edge_method = QtWidgets.QLabel(self)
        label_edge_method.setText("Edge method")
        hlayout_edge_multi_2d.addWidget(label_edge_method)

        self.combo_edge_method = QtWidgets.QComboBox(self)
        self.combo_edge_method.addItems(
            ['closing', 'erosion', 'dilation']
        )
        self.combo_edge_method.setToolTip(
            "Method to deal with object edges"
        )
        hlayout_edge_multi_2d.addWidget(self.combo_edge_method)

        self.checkbox_multi2d = QtWidgets.QCheckBox(self)
        self.checkbox_multi2d.setText("Use multi-2D for 3D data")
        self.checkbox_multi2d.setToolTip(
            "Creates a separate sparse array for each z-plane, "
            "instead of a single sparse array for the entire stack."
        )
        hlayout_edge_multi_2d.addWidget(self.checkbox_multi2d)

        hlayout_edge_multi_2d.addItem(
            QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        self.vlayout.addLayout(hlayout_edge_multi_2d)

        button_apply_thr_params = QtWidgets.QPushButton(self)
        button_apply_thr_params.setText("Apply")
        button_apply_thr_params.setStyleSheet("font-weight: bold")
        button_apply_thr_params.clicked.connect(
            lambda: self.apply_threshold()
        )
        self.vlayout.addWidget(button_apply_thr_params)

        hlayout_export_buttons = QtWidgets.QHBoxLayout(self)

        button_export_cnmf_2d = QtWidgets.QPushButton(self)
        button_export_cnmf_2d.setText("Export 2D CNMF Seeds")
        button_export_cnmf_2d.setStyleSheet("font-weight: bold")
        button_export_cnmf_2d.clicked.connect(
            lambda: self.save_masks_cnmf()
        )
        hlayout_export_buttons.addWidget(button_export_cnmf_2d)

        # button_export_cnmf_3d = QtWidgets.QPushButton(self)
        # button_export_cnmf_3d.setText("Export 3D CNMF Seeds")
        # button_export_cnmf_3d.setStyleSheet("font-weight: bold")
        # hlayout_export_buttons.addWidget(button_export_cnmf_3d)

        button_export_viewer_rois = QtWidgets.QPushButton(self)
        button_export_viewer_rois.setText("Export to Viewer as Manual ROIs")
        button_export_viewer_rois.setStyleSheet("font-weight: bold")
        button_export_viewer_rois.clicked.connect(
            lambda: self.export_to_viewer()
        )
        hlayout_export_buttons.addWidget(button_export_viewer_rois)

        self.vlayout.addLayout(hlayout_export_buttons)

        self.glw = GraphicsLayoutWidget(self)
        self.imgitem = ImageItem()
        self.viewbox = self.glw.addViewBox()
        self.viewbox.setAspectLocked(True)
        self.viewbox.addItem(self.imgitem)

        self.vlayout.addWidget(self.glw)

        self.colored_mask: np.ndarray = np.empty(0)
        self.masks: Union[np.ndarray, List[np.ndarray]] = np.empty(0)
        self.binary_shape: tuple = None

        colormap = cm.get_cmap("nipy_spectral")  # cm.get_cmap("CMRmap")
        colormap._init()
        lut = (colormap._lut * 255).view(np.ndarray)
        self.imgitem.setLookupTable(lut)

        self.nuset_widget.sig_zlevel_changed.connect(
            self.set_colored_mask
        )

        self.setLayout(self.vlayout)

    # TODO: I should really use qtap here
    def get_params(self):
        selem = self.spinbox_selem.value()

        return {
            'thr': self.spinbox_thr.value(),
            'selem': selem if selem > 0 else None,
            'edge_method': self.combo_edge_method.currentText(),
            'minsize': self.spinbox_minsize.value(),
            'maxsize': self.spinbox_maxsize.value(),
            'connectivity': self.spinbox_connectivity.value(),
            'multi-2d': self.checkbox_multi2d.isChecked()
        }

    def get_all_params(self):
        """
        All params, including those used for segmentation before the export GUI.
        :return:
        """
        d = \
            {
                'nuset_segment_params': self.nuset_widget.params_final,
                'nuset_export_params': self.get_params(),
            }

        return d

    def set_colored_mask(self, z):
        if self.colored_mask.size > 0:
            self.imgitem.setImage(
                self.colored_mask[:, :, z]
            )

    def _make_binary(self, seg_img, params, shape):
        binary_ = np.full(seg_img.shape, False, dtype=np.bool)
        binary_[seg_img > params['thr']] = True

        binary = np.full(shape, False, np.bool)

        if len(shape) > 2:
            binary[:binary_.shape[0], :binary_.shape[1], :binary_.shape[2]] = binary_
        else:
            binary[:binary_.shape[0], :binary_.shape[1]] = binary_

        if params['minsize'] > 0:
            print("Removing small objs")
            binary = skimage.morphology.remove_small_objects(
                binary, min_size=params['minsize'], connectivity=params['connectivity']
            )
            binary = remove_large_objects(
                binary, params['maxsize'], connectivity=params['connectivity']
            )

        return binary

    def _apply_threshold_2d(self):
        params = self.get_params()
        shape = self.nuset_widget.imgs_projected[0].T.shape
        seg_img = self.nuset_widget.imgs_postprocessed[0].T

        print("Thresholding")
        binary = self._make_binary(seg_img, params, shape)#.T
        self.binary_shape = binary.shape

        print("Creating sparse masks")
        self.masks = get_sparse_masks(
            segmented_img=binary,
            raw_img_shape=shape,
            edge_method=params['edge_method'],
            selem=params['selem'],
        )

        self.colored_mask = get_colored_mask(self.masks, binary.T.shape)
        self.imgitem.setImage(self.colored_mask)

    def _apply_threshold_3d(self):
        params = self.get_params()
        # 3D
        seg_img = np.stack(self.nuset_widget.imgs_postprocessed)
        shape = np.stack(self.nuset_widget.imgs_projected).shape

        print("Thresholding")
        # binary array
        binary = self._make_binary(seg_img, params, shape)
        self.binary_shape = binary.shape

        print("Creating sparse masks")
        self.masks = get_sparse_masks(
            segmented_img=binary,
            raw_img_shape=shape,
            edge_method=params['edge_method'],
            selem=params['selem']
        )

        self.colored_mask = get_colored_mask(self.masks, binary.T.shape)
        self.imgitem.setImage(
            self.colored_mask[:, :, self.nuset_widget.zlevel]
        )

    def _apply_threshold_2d_multi(self):
        params = self.get_params()

        shape = self.nuset_widget.imgs_projected[0].T.shape

        masks = []
        print("Thresholding & Creating sparse masks")
        for ix in tqdm(range(len(self.nuset_widget.imgs_postprocessed))):
            seg_img = self.nuset_widget.imgs_postprocessed[ix].T

            binary = self._make_binary(seg_img, params, shape)
            self.binary_shape = binary.shape

            masks.append(
                get_sparse_masks(
                    segmented_img=binary,
                    raw_img_shape=shape,
                    edge_method=params['edge_method'],
                    selem=params['selem']
                )
            )

        self.masks = masks

        print("Coloring masks")
        colored_masks = []
        for ix in tqdm(range(len(self.masks))):
            colored_masks.append(
                get_colored_mask(
                    self.masks[ix], binary.shape
                )
            )

        self.colored_mask = np.stack(colored_masks).T
        self.imgitem.setImage(self.colored_mask[:, :, self.nuset_widget.zlevel])

    @present_exceptions()
    def apply_threshold(self):
        if not self.nuset_widget.imgs_postprocessed:
            raise ValueError("You must segment images before you can proceed.")

        for img in self.nuset_widget.imgs_postprocessed:
            if not img.size > 0:
                raise ValueError("Your must segment the entire stack before you can proceed.")

        if self.nuset_widget.z_max > 0:
            if QtWidgets.QMessageBox.question(
                    self, 'Export for CNMF?', 'This may take a few minutes, and could take ~10 minutes '
                                              'if segmenting a large stack. Proceed?',
            ) == QtWidgets.QMessageBox.No:
                return

        # 3D
        if self.nuset_widget.z_max > 0:
            if self.checkbox_multi2d.isChecked():
                self._apply_threshold_2d_multi()
            else:
                self._apply_threshold_3d()
        # 2D
        else:
            self._apply_threshold_2d()

    def _check_save_masks(self):
        if not self.nuset_widget.imgs_postprocessed:
            raise ValueError("You must segment images before you can proceed.")

        for img in self.nuset_widget.imgs_postprocessed:
            if not img.size > 0:
                raise ValueError("Your must segment the entire stack before you can proceed.")

        if not len(self.masks) > 0:
            raise ValueError("You must apply the threshold before you can proceed")

    @use_save_file_dialog('Save masks', None, '.h5')
    @present_exceptions()
    def save_masks_cnmf(self, path):
        print("Please wait, saving masks...")
        if self.get_params()['multi-2d']:
            sm = {}
            for z in range(len(self.masks)):
                sm[str(z)] = self.masks[z]  # each plane is addressed as an hdf5 group
        else:
            sm = self.masks

        d = \
            {
                'sparse_mask': sm,
                'segment_params': self.get_all_params()
            }
        HdfTools.save_dict(d, path, 'data')
        print("Finishing saving masks!")

    @present_exceptions()
    def export_to_viewer(self):
        if not self.nuset_widget.imgs_postprocessed:
            raise ValueError("You must segment images before you can proceed.")

        for img in self.nuset_widget.imgs_postprocessed:
            if not img.size > 0:
                raise ValueError("Your must segment the entire stack before you can proceed.")

        if not self.masks.size > 0:
            raise ValueError("You must apply the threshold before you can proceed")

        roi_manager = self.nuset_widget.vi.viewer.parent().get_module('roi_manager')
        roi_manager.start_backend('Manual')

        if QtWidgets.QMessageBox.question(
            self, 'Use Convex Hull?',
            'Use a Convex Hull to get the vertices? [Yes]\n'
            'This is recommended if you are importing as ManualROIs.\n'
            'If you select [No] ALL vertices for the masks will be imported and '
            'this could be extremely slow!',
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
        ) == QtWidgets.QMessageBox.Yes:
            method = 'ConvexHull'
        else:
            method = 'cKDTree'

        if self.nuset_widget.z_max > 0:
            shape = self.binary_shape
        else:
            shape = self.binary_shape[::-1]

        if method == 'ConvexHull':
            self._export_hulls(shape)
        elif method == 'cKDTree':
            self._export_ckdtrees(shape)

        self.nuset_widget.vi.viewer.workEnv.history_trace.append(
            {
                'nuset_segmentation': \
                    {
                        **self.get_all_params(),
                        'vertex_method': method
                    }
            }
        )

    def _export_hulls(self, shape):
        for i in tqdm(range(self.masks.shape[1])):
            try:
                vs = area_to_hull(
                    self.masks[:, i].reshape(shape)
                )
            except QhullError:
                print(f"Skipping {i}, not enough points for convex hull")
            else:
                self.nuset_widget.vi.viewer.workEnv.roi_manager.add_roi_from_points(
                    xs=vs[:, 0], ys=vs[:, 1]
                )

    def _export_ckdtrees(self, shape):
        for i in tqdm(range(self.masks.shape[1])):
            vs = area_to_vertices(
                self.masks[:, i].reshape(shape)
            )

            self.nuset_widget.vi.viewer.workEnv.roi_manager.add_roi_from_points(
                xs=vs[:, 0], ys=vs[:, 1]
            )


class NusetWidget(QtWidgets.QWidget):
    sig_zlevel_changed = QtCore.pyqtSignal(int)

    def __init__(self, parent, viewer_ref):
        QtWidgets.QWidget.__init__(self, parent)

        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vlayout.addWidget(self.splitter)

        self.left_layout = QtWidgets.QVBoxLayout(self)

        self.left_widget = QtWidgets.QWidget(self.splitter)
        self.left_widget.setLayout(self.left_layout)

        hlayout_custom_img = QtWidgets.QHBoxLayout(self.left_widget)
        self.lineedit_custom_img_path = QtWidgets.QLineEdit(self.left_widget)
        self.lineedit_custom_img_path.setPlaceholderText("Path to custom image or stack")
        self.lineedit_custom_img_path.setToolTip(
            "Use a different image or stack for segmentation, such as an image or stack of nuclei."
        )
        self.button_use_custom = QtWidgets.QPushButton(self.left_widget)
        self.button_use_custom.setMaximumWidth(50)
        self.button_use_custom.setText("Set")
        hlayout_custom_img.addWidget(self.lineedit_custom_img_path)
        hlayout_custom_img.addWidget(self.button_use_custom)
        self.left_layout.addLayout(hlayout_custom_img)

        hlayout_projection_radios = QtWidgets.QHBoxLayout(self.left_widget)
        self.radio_std = QtWidgets.QRadioButton(self.left_widget)
        self.radio_std.setText("Std. Deviation")
        self.radio_max = QtWidgets.QRadioButton(self.left_widget)
        self.radio_max.setText("Max")
        self.radio_mean = QtWidgets.QRadioButton(self.left_widget)
        self.radio_mean.setText("Mean")

        self.projection_option: str = ''

        for w in [self.radio_std, self.radio_max, self.radio_mean]:
            hlayout_projection_radios.addWidget(w)
            w.clicked.connect(self.update_projection)

        label_projections = QtWidgets.QLabel(self.left_widget)
        label_projections.setText("Choose Input Projection")
        label_projections.setStyleSheet("font-weight: bold")

        self.left_layout.addWidget(label_projections)
        self.left_layout.addLayout(hlayout_projection_radios)

        # projection image
        self.glw_raw = GraphicsLayoutWidget(self.left_widget)
        self.imgitem_raw = ImageItem()
        self.viewbox_raw = self.glw_raw.addViewBox()
        self.viewbox_raw.setAspectLocked(True)
        self.viewbox_raw.addItem(self.imgitem_raw)

        self.left_layout.addWidget(self.glw_raw)

        hlayout_preprocess = QtWidgets.QHBoxLayout(self.left_widget)

        arg_opts_preprocess = \
            {
                'img': {'ignore': True},

                'sigmoid_cutoff': {
                    'step': 10,
                    'minmax': (0, 9999.9)
                },

                'sigmoid_gain': {
                    'step': 0.01
                },
                'equalize_lower': {
                    'step': 0.01,
                    'minmax': (-1.0, 1.0)
                },
                'equalize_upper': {
                    'step': 0.01,
                    'minmax': (-1.0, 1.0)
                }
            }

        self.preprocess_controls = \
            Function(
                get_preprocess,
                arg_opts=arg_opts_preprocess,
                parent=self.left_widget
            )
        self.preprocess_controls.button_set.hide()
        self.preprocess_controls.sig_changed.connect(self.update_preprocess)
        self.preprocess_controls.set_title("Pre-process Settings")

        hlayout_preprocess.addWidget(self.preprocess_controls.widget)

        self.zslider = QtWidgets.QSlider(parent=self.left_widget, orientation=QtCore.Qt.Vertical)
        self.zslider.setInvertedAppearance(True)
        self.zslider.setSingleStep(1)
        self.zslider.valueChanged.connect(self.update_zlevel)

        label_zslider = QtWidgets.QLabel(self.left_widget)
        label_zslider.setText("z-level")

        self.spinbox_zlevel = QtWidgets.QSpinBox(self.left_widget)
        self.spinbox_zlevel.setSingleStep(1)
        self.spinbox_zlevel.valueChanged.connect(self.zslider.setValue)
        self.zslider.valueChanged.connect(self.spinbox_zlevel.setValue)


        hlayout_preprocess.addWidget(label_zslider)
        hlayout_preprocess.addWidget(self.zslider)
        hlayout_preprocess.addWidget(self.spinbox_zlevel)

        self.left_layout.addLayout(hlayout_preprocess)

        # preprocess image item
        self.glw_preprocess = GraphicsLayoutWidget(self.left_widget)
        self.imgitem_preprocess = ImageItem()
        self.viewbox_preprocess = self.glw_preprocess.addViewBox()
        self.viewbox_preprocess.setAspectLocked(True)
        self.viewbox_preprocess.addItem(self.imgitem_preprocess)

        self.left_layout.addWidget(self.glw_preprocess)

        self.splitter.addWidget(self.left_widget)

        # segmentation stuff
        self.nuset_model = Nuset()

        self.right_layout = QtWidgets.QVBoxLayout(self)

        self.right_widget = QtWidgets.QWidget(self.splitter)
        self.right_widget.setLayout(self.right_layout)

        hlayout_nuset = QtWidgets.QHBoxLayout(self.right_widget)

        arg_opts_nuset = \
            {
                'image': {'ignore': True},

                'min_score': {
                    'minmax': (0.0, 1.0),
                    'step': 0.05
                },

                'nms_threshold': {
                    'minmax': (0.0, 1.0),
                    'step': 0.05
                },

                'rescale_ratio': {
                    'minmax': (0.1, 10.0),
                    'step': 0.25,
                    'val': 1.25  # not working if set to 1.0 with pyqtgraph ImageItem for some reason
                }

            }

        self.nuset_controls = \
            Function(
                self.nuset_model.predict,
                arg_opts=arg_opts_nuset,
                parent=self.right_widget
            )

        # self.nuset_controls.button_set.hide()
        self.nuset_controls.sig_set_clicked.connect(self.update_segmentation)
        self.nuset_controls.set_title("NuSeT Parameters")
        hlayout_nuset.addWidget(self.nuset_controls.widget)

        arg_opts_postprocess = \
            {
                'img': {'ignore': True},

                'abs_obj_threshold': {
                    'minmax': (-1, 100),
                    'step': 2,
                },

                'rel_obj_threshold': {
                    'minmax': (0, 100),
                    'step': 2
                },

                'obj_connectivity': {
                    'minmax': (0, 10),
                    'step': 1
                },

                'abs_hol_threshold': {
                    'minmax': (-1, 100),
                    'step': 2,
                },

                'rel_hol_threshold': {
                    'minmax': (0, 100),
                    'step': 2
                },

                'hol_connectivity': {
                    'minmax': (0, 100),
                    'step': 1
                }
            }

        self.postprocess_controls = \
            Function(
                get_postprocess,
                arg_opts=arg_opts_postprocess,
                parent=self.right_widget
            )
        self.postprocess_controls.button_set.hide()
        self.postprocess_controls.sig_changed.connect(self.update_postprocess)
        self.postprocess_controls.set_title("Post-process Parameters")

        hlayout_nuset.addWidget(self.postprocess_controls.widget)
        self.right_layout.addLayout(hlayout_nuset)

        self.checkbox_segment_current_plane = QtWidgets.QCheckBox(self.nuset_controls.widget)
        self.checkbox_segment_current_plane.setText("Only segment current plane")
        self.checkbox_segment_current_plane.setToolTip(
            "Performs segmentation for only the current plane, "
            "useful for trying out parameters."
        )
        self.checkbox_segment_current_plane.setChecked(True)
        self.nuset_controls.vlayout.addWidget(self.checkbox_segment_current_plane)

        self.glw_segmented = GraphicsLayoutWidget(self.right_widget)
        self.imgitem_segmented = ImageItem()
        self.imgitem_segmented_underlay = ImageItem()
        self.viewbox_segmented = self.glw_segmented.addViewBox()
        self.viewbox_segmented.setAspectLocked(True)
        self.viewbox_segmented.addItem(self.imgitem_segmented)
        self.viewbox_segmented.addItem(self.imgitem_segmented_underlay)

        # colormaps for the mask overlay plot
        cm_cyan = cm.get_cmap(cmap_cyan)
        cm_cyan._init()
        lut_cyan = (cm_cyan._lut * 255).view(np.ndarray)[128:-5]
        self.imgitem_segmented_underlay.setLookupTable(lut_cyan)

        # colormaps for the mask overlay plot
        cm_magenta = cm.get_cmap(cmap_magenta)
        cm_magenta._init()
        lut_magenta = (cm_magenta._lut * 255).view(np.ndarray)[:-5]  # so it displays as a mask
        self.imgitem_segmented.setLookupTable(lut_magenta)

        # allow transparency
        # self.imgitem_segmented.setCompositionMode(QtGui.QPainter.CompositionMode_Overlay)
        self.imgitem_segmented_underlay.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        self.imgitem_segmented.setZValue(2)
        self.imgitem_segmented.setOpacity(0.5)
        self.imgitem_segmented_underlay.setZValue(1)
        self.imgitem_segmented_underlay.setOpacity(0.3)

        self.slider_underlay_opacity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_underlay_opacity.setMinimum(0)
        self.slider_underlay_opacity.setMaximum(100)
        self.slider_underlay_opacity.setValue(30)
        self.slider_underlay_opacity.valueChanged.connect(
            lambda v: self.imgitem_segmented_underlay.setOpacity(v / 100)
        )
        label_underlay_opacity = QtWidgets.QLabel(self.nuset_controls.widget)
        label_underlay_opacity.setText("Underlay opacity")
        self.nuset_controls.vlayout.addWidget(label_underlay_opacity)
        self.nuset_controls.vlayout.addWidget(self.slider_underlay_opacity)

        self.slider_mask_opacity = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_mask_opacity.setMinimum(0)
        self.slider_mask_opacity.setMaximum(100)
        self.slider_mask_opacity.setValue(50)
        self.slider_mask_opacity .valueChanged.connect(
            lambda v: self.imgitem_segmented.setOpacity(v / 100)
        )
        label_segmented_opacity = QtWidgets.QLabel(self.nuset_controls.widget)
        label_segmented_opacity.setText("Segmentation opacity")
        self.nuset_controls.vlayout.addWidget(label_segmented_opacity)
        self.nuset_controls.vlayout.addWidget(self.slider_mask_opacity)

        self.combo_blend_mode = QtWidgets.QComboBox(self.nuset_controls.widget)
        self.combo_blend_mode.addItems(
            [
                'SourceOver',
                'Overlay',
                'Plus',
                'Multiply'
            ]
        )
        self.combo_blend_mode.setCurrentIndex(0)
        self.combo_blend_mode.currentTextChanged.connect(
            lambda opt: self.imgitem_segmented.setCompositionMode(
                getattr(QtGui.QPainter, f'CompositionMode_{opt}')
            )
        )
        label_blend_mode = QtWidgets.QLabel(self.nuset_controls.widget)
        label_blend_mode.setText('Blend mode:')
        self.nuset_controls.vlayout.addWidget(label_blend_mode)
        self.nuset_controls.vlayout.addWidget(self.combo_blend_mode)

        self.right_layout.addWidget(self.glw_segmented)
        self.splitter.addWidget(self.right_widget)

        self.export_widget = ExportWidget(self)

        self.imgs_projected: List[np.ndarray] = []
        self.imgs_preprocessed: List[np.ndarray] = []
        self.imgs_segmented: List[np.ndarray] = []
        self.imgs_postprocessed: List[np.ndarray] = []

        self.input_img: np.ndarray = np.empty(0)
        self.zlevel = 0
        self.z_max: int = 0

        self.process_pool = Pool(cpu_count())

        self.error_label = QtWidgets.QLabel(self)
        self.error_label.setMaximumHeight(20)
        self.error_label.setStyleSheet("font-weight: bold; color: red")
        self.vlayout.addWidget(self.error_label)

        self.projection_option = ''
        self.params_final = None

        if viewer_ref is None:
            print("Assuming testing mode")
        else:
            self.vi = ViewerUtils(viewer_ref)
            self.vi.viewer.sig_workEnv_changed.connect(self.set_input)
            self.set_input(self.vi.viewer.workEnv)

    @use_open_file_dialog('Open image file', None, ['*.tiff', '*.tif'])
    @present_exceptions('Error', 'Error loading custom input image')
    def set_custom_input(self, path, *args):
        self.clear_widget()
        img = tifffile.imread(path)
        self._set_input_image(img.T)

    def set_input(self, workEnv: ViewerWorkEnv):
        self.clear_widget()

        try:
            img = workEnv.imgdata._seq
        except:
            return

        self._set_input_image(img)

    def _set_input_image(self, img: np.ndarray):
        self.input_img = img

        if self.input_img.ndim == 4:
            self.z_max = self.input_img.shape[3] - 1
        else:
            self.z_max = 0

        self.zslider.valueChanged.disconnect(self.update_zlevel)
        self.zslider.setValue(0)
        self.zslider.setMaximum(self.z_max)
        self.spinbox_zlevel.setMaximum(self.z_max)
        self.zslider.valueChanged.connect(self.update_zlevel)

    def update_zlevel(self, z: int):
        self.zlevel = z
        self.sig_zlevel_changed.emit(z)

        for imgitem, imglist in zip(
            [
                self.imgitem_raw,
                self.imgitem_preprocess,
                self.imgitem_segmented_underlay,
                self.imgitem_segmented
            ],
            [
                self.imgs_projected,
                self.imgs_preprocessed,
                self.imgs_preprocessed,
                self.imgs_postprocessed
            ]
        ):
            if imglist:  # set if the list is not empty
                if imglist[z].size > 0:
                    imgitem.setImage(imglist[z])

    def update_projection(self):
        if not self.input_img.size > 0:
            self.error_label.setText("No input image")
            return

        if self.radio_std.isChecked():
            opt = 'std'
        elif self.radio_max.isChecked():
            opt = 'max'
        elif self.radio_mean.isChecked():
            opt = 'mean'

        if self.projection_option == opt:
            return
        
        self.projection_option = opt

        func = getattr(np, f'nan{opt}')

        print("Updating Projection(s)")
        if self.input_img.ndim == 4:
            self.imgs_projected = [
                func(self.input_img[:, :, :, z], axis=2) for z in tqdm(range(self.z_max + 1))
            ]
        else:
            self.imgs_projected = [func(self.input_img, axis=2)]

        self.imgitem_raw.setImage(self.imgs_projected[self.zlevel])
        self.error_label.clear()

    def update_preprocess(self, params):
        if not self.imgs_projected:
            self.error_label.setText("Projection Image is Empty")
            return

        print("Preprocessing Image(s)")

        # self.image_preprocesses = [
        #     get_preprocess(p, **params) for p in tqdm(self.image_projections)
        # ]

        kwargs = [{'img': img, **params} for img in self.imgs_projected]

        self.imgs_preprocessed = self.process_pool.map(wrap_preprocess, kwargs)

        self.imgitem_preprocess.setImage(self.imgs_preprocessed[self.zlevel])
        self.imgitem_segmented_underlay.setImage(self.imgs_preprocessed[self.zlevel])
        self.error_label.clear()

    def update_segmentation(self, params):
        if not self.imgs_preprocessed:
            self.error_label.setText("Preprocess Image is Empty")
            return

        print("Segmenting Image(s)")
        if not self.checkbox_segment_current_plane.isChecked():
            self.imgs_segmented = [
                self.nuset_model.predict(img, **params) for img in tqdm(self.imgs_preprocessed)
            ]
        else:
            self.imgs_segmented = [
                np.empty(0) for i in range(self.z_max + 1)
            ]

            self.imgs_segmented[self.zlevel] = self.nuset_model.predict(
                self.imgs_preprocessed[self.zlevel], **params
            )

        # postprocess funciton will just return the segmented img if do_postprocess is False
        self.update_postprocess(self.postprocess_controls.get_data())

        self.params_final = \
            {
                'method': 'NuSeT',
                'projection_option': self.projection_option,
                **self.preprocess_controls.get_data(),
                **self.nuset_controls.get_data(),
                **self.postprocess_controls.get_data(),
            }

        self.error_label.clear()

    def update_postprocess(self, params):
        if not self.imgs_segmented:
            self.error_label.setText("Segmented Image is Empty")
            return

        print("Postprocessing Image(s)")
        self.imgs_postprocessed = [
            get_postprocess(img, **params) for img in tqdm(self.imgs_segmented)
        ]

        self.imgitem_segmented.setImage(self.imgs_postprocessed[self.zlevel])
        self.error_label.clear()

    def clear_widget(self):
        self.imgs_projected.clear()
        self.imgs_preprocessed.clear()
        self.imgs_segmented.clear()
        self.imgs_postprocessed.clear()

        self.imgitem_raw.clear()
        self.imgitem_preprocess.clear()
        self.imgitem_segmented.clear()
        self.imgitem_segmented_underlay.clear()

        self.radio_std.setChecked(False)
        self.radio_max.setChecked(False)
        self.radio_mean.setChecked(False)

        self.projection_option = ''
