from PyQt5 import QtCore, QtGui, QtWidgets
from glob import glob
import os
from matplotlib import cm as matplotlib_color_map
from typing import List, Union, Any
from mesmerize.pyqtgraphCore import mkColor
import numpy as np
from collections import OrderedDict

qual_cmaps = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
              'tab20c']


def auto_colormap(n_colors: int, cmap: str = 'hsv', output: str = 'mpl', spacing: str = 'uniform') -> List[Union[QtGui.QColor, np.ndarray]]:
    """
    Returns colors evenly spread through the chosen colormap.

    :param n_colors: Numbers of colors to return
    :param cmap:     name of colormap
    :param output:   option: 'mpl' returns RGBA values between 0-1 which matplotlib likes,
                     option: 'pyqt' returns QtGui.QColor instances corresponding to the RGBA values
    :param spacing:  option: 'uniform' returns evenly spaced colors across the entire cmap range
                     option: 'subsequent' returns subsequent colors from the cmap

    :return:         List of colors as either QColor or numpy array with length n_colors
    """
    cm = matplotlib_color_map.get_cmap(cmap)
    cm._init()

    if output == 'pyqt':
        lut = (cm._lut * 255).view(np.ndarray)
    else:
        lut = (cm._lut).view(np.ndarray)

    if spacing == 'uniform':
        if not cmap in qual_cmaps:
            cm_ixs = np.linspace(0, 210, n_colors, dtype=int)
        else:
            if n_colors > len(lut):
                raise ValueError('Too many colors requested for the chosen cmap')
            cm_ixs = np.arange(0, len(lut), dtype=int)
    else:
        cm_ixs = range(n_colors)

    colors = []
    for ix in range(n_colors):
        c = lut[cm_ixs[ix]]
        if output == 'pyqt':
            colors.append(mkColor(c))
        else:
            colors.append(c)

    return colors


def get_colormap(labels: iter, cmap: str) -> OrderedDict:
    """
    Get dict for mapping labels onto colors
    :param labels:  labels for creating a colormap. Order is maintained if it is a list of unique elements.
    :param cmap:    name of colormap
    :return:        dict of labels as keys and colors as values
    """
    if not len(set(labels)) == len(labels):
        labels = list(set(labels))
    else:
        labels = list(labels)

    colors = auto_colormap(len(labels), cmap)

    return OrderedDict(zip(labels, colors))


def map_labels_to_colors(labels: iter, cmap: str):
    """
    Map labels into colors according to chosen colormap
    :param labels:  labels for mapping onto a colormap
    :param cmap:    name of colormap
    :return:        list of colors mapped onto the labels
    """
    mapper = get_colormap(labels, cmap)
    return list(map(mapper.get, labels))


class ColormapListWidget(QtWidgets.QListWidget):
    signal_colormap_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.populate_colormaps()
        self.currentItemChanged.connect(self.emit_colormap_changed)
        self.setToolTip('Colormap picker')
        self.setCurrentRow(0)

    @property
    def current_cmap(self) -> str:
        return self.currentItem().text()

    def set_cmap(self, cmap: str):
        item = self.findItems(cmap, QtCore.Qt.MatchExactly)[0]
        ix = self.indexFromItem(item)
        self.setCurrentIndex(ix)

    def emit_colormap_changed(self, item: QtWidgets.QListWidgetItem):
        self.signal_colormap_changed.emit(item.text())

    def populate_colormaps(self):
        mpath = os.path.abspath(__file__)
        mdir = os.path.dirname(mpath)
        cmap_img_files = glob(mdir + '/colormaps/*.png')
        cmap_img_files.sort()

        for path in cmap_img_files:
            img = QtGui.QIcon(path)
            item = QtWidgets.QListWidgetItem(os.path.basename(path)[:-4])
            item.setIcon(img)
            self.addItem(item)
        self.setIconSize(QtCore.QSize(120, 25))
