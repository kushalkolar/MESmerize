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
import skimage
import numpy as np
import numexpr
from nuset import Nuset

from PyQt5 import QtWidgets, QtCore
from qtap import Function
from ..core import ViewerUtils
from ...pyqtgraphCore import GraphicsLayoutWidget, ImageItem, ViewBox


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
        do_equalize: bool = True,
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
        # equalize_hist works more easily with 16 bit integers
        img = normalize_image(img, np.uint16)
        img = skimage.exposure.equalize_adapthist(img, kernel_size=equalize_kernel)

    # float32 is best for GPU I think?
    img = normalize_image(img, np.float32)

    return img


# from NuSeT processing cleanimage function
def get_postprocess(
        img: np.ndarray,
        do_postprocess: bool = True,
        abs_obj_threshold: int = -1,
        rel_obj_threshold: int = 5,
        obj_connectivity: int = 2,
        abs_hol_threshold: int = -1,
        rel_hol_threshold: int = 5,
        hol_connectivity: int = 2
    ) -> np.ndarray:

    if not do_postprocess:
        return img

    image = img.astype(np.bool)
    im_label = skimage.morphology.label(image, connectivity=1)
    num_cells = np.max(im_label)
    mean_area = np.sum(image).astype(np.float32) / num_cells

    if abs_obj_threshold == -1:
        min_obj_size = mean_area / rel_obj_threshold
    else:
        min_obj_size = abs_obj_threshold
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


class ModuleGUI(QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref):
        # self.vi = ViewerUtils(viewer_ref)
        QtWidgets.QWidget.__init__(self, parent)
        self.resize(1000, 900)

        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vlayout.addWidget(self.splitter)

        self.left_layout = QtWidgets.QVBoxLayout(self)

        self.left_widget = QtWidgets.QWidget(self.splitter)
        self.left_widget.setLayout(self.left_layout)

        arg_opts_preprocess = \
            {
                'img': {'ignore': True},

                'sigmoid_gain': {
                    'step': 0.01
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

        hlayout_projection_radios = QtWidgets.QHBoxLayout(self.left_widget)
        self.radio_std = QtWidgets.QRadioButton(self.left_widget)
        self.radio_std.setText("Std. Deviation")
        self.radio_max = QtWidgets.QRadioButton(self.left_widget)
        self.radio_max.setText("Max")
        self.radio_mean = QtWidgets.QRadioButton(self.left_widget)
        self.radio_mean.setText("Mean")

        for w in [self.radio_std, self.radio_max, self.radio_mean]:
            hlayout_projection_radios.addWidget(w)

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
        self.left_layout.addWidget(self.preprocess_controls.widget)

        # preprocess image
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
                    'step': 0.5
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

        self.glw_segmented = GraphicsLayoutWidget(self.right_widget)
        self.imgitem_segmented = ImageItem()
        self.imgitem_segmented_underlay = ImageItem()
        self.viewbox_segmented = self.glw_segmented.addViewBox()
        self.viewbox_segmented.setAspectLocked(True)
        self.viewbox_segmented.addItem(self.imgitem_segmented)
        self.viewbox_segmented.addItem(self.imgitem_segmented_underlay)

        self.imgitem_segmented.setZValue(2)
        self.imgitem_segmented.setOpacity(0.5)
        self.imgitem_segmented_underlay.setZValue(1)
        self.imgitem_segmented_underlay.setOpacity(0.3)

        self.right_layout.addWidget(self.glw_segmented)
        self.splitter.addWidget(self.right_widget)

        self.image_projection: np.ndarray = np.empty(0)
        self.image_preprocess: np.ndarray = np.empty(0)
        self.image_segmented: np.ndarray = np.empty(0)
        self.image_postprocessed: np.ndarray = np.empty(0)

        self.error_label = QtWidgets.QLabel(self)
        self.error_label.setMaximumHeight(20)
        self.error_label.setStyleSheet("font-weight: bold; color: red")
        self.vlayout.addWidget(self.error_label)

    def update_projection(self):
        pass

    def update_preprocess(self, params):
        if not self.image_projection.size > 0:
            self.error_label.setText("Projection Image is Empty")
            return

        self.image_preprocess = get_preprocess(self.image_projection, **params)
        self.imgitem_preprocess.setImage(self.image_preprocess)
        self.imgitem_segmented_underlay.setImage(self.image_preprocess)
        self.error_label.clear()

    def update_segmentation(self, params):
        if not self.image_preprocess.size > 0:
            self.error_label.setText("Preprocess Image is Empty")
            return

        self.image_segmented = self.nuset_model.predict(self.image_preprocess, **params)

        if self.postprocess_controls.arguments.do_postprocess.val:
            self.update_postprocess(self.postprocess_controls.get_data())

        else:
            self.imgitem_segmented.setImage(self.image_segmented)

        self.error_label.clear()

    def update_postprocess(self, params):
        if not self.image_segmented.size > 0:
            self.error_label.setText("Segmented Image is Empty")
            return

        self.image_postprocessed = get_postprocess(self.image_segmented, **params)
        self.imgitem_segmented.setImage(self.image_postprocessed)
        self.error_label.clear()
