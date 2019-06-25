from PyQt5 import QtCore, QtGui, QtWidgets
from glob import glob
import os
from matplotlib import cm as matplotlib_color_map
from typing import List, Union, Any
from ...pyqtgraphCore import mkColor
import numpy as np


def auto_colormap(number_of_colors: int, color_map: str = 'hsv') -> List[Union[QtGui.QColor, Any]]:
    cm = matplotlib_color_map.get_cmap(color_map)
    cm._init()
    lut = (cm._lut * 255).view(np.ndarray)
    cm_ixs = np.linspace(0, 210, number_of_colors, dtype=int)

    colors = []
    for ix in range(number_of_colors):
        c = lut[cm_ixs[ix]]
        colors.append(mkColor(c))

    return colors


def get_colormap(labels: iter, cmap: str) -> dict:
    """
    Maps labels onto colors
    :param labels:
    :param cmap:    name of colormap
    :return:        dict of labels as keys and colors as values
    """
    labels = set(labels)
    colors = auto_colormap(len(labels), cmap)

    return dict(zip(labels, colors))


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


