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


def get_postprocess(img: np.ndarray) -> np.ndarray:
    pass


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

        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.vlayout.addWidget(self.splitter)

        self.left_layout = QtWidgets.QVBoxLayout(self)

        img_ignore = {'img': {'ignore': True}}

        self.preprocess_controls = Function(get_preprocess, arg_opts=img_ignore, parent=self.splitter)

        self.left_widget = QtWidgets.QWidget(self.splitter)
        self.left_widget.setLayout(self.left_layout)

        self.glw_raw = GraphicsLayoutWidget(self.left_widget)
        self.img_item_raw = ImageItem()
        self.viewbox_raw = self.glw_raw.addViewBox()
        self.viewbox_raw.addItem(self.img_item_raw)

        self.left_layout.addWidget(self.glw_raw)

        # self.left_layout.addWidget(self.img_item_raw)
        self.left_layout.addWidget(self.preprocess_controls.widget)

        # self.img_preprocessed = ImageItem()
        # self.left_layout.addWidget(self.img_preprocessed)

        self.splitter.addWidget(self.left_widget)

        self.right_layout = QtWidgets.QVBoxLayout(self)

        self.right_widget = QtWidgets.QWidget(self.splitter)
        self.right_widget.setLayout(self.right_layout)

        self.glw_raw2 = GraphicsLayoutWidget(self.right_widget)
        self.img_item_raw2 = ImageItem()
        self.viewbox_raw2 = self.glw_raw2.addViewBox()
        self.viewbox_raw2.addItem(self.img_item_raw2)

        self.right_layout.addWidget(self.glw_raw2)
        self.splitter.addWidget(self.right_widget)


