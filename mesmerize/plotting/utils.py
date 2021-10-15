from PyQt5 import QtCore, QtGui, QtWidgets
from glob import glob
import os
from matplotlib import cm as matplotlib_color_map
from typing import *
from ..pyqtgraphCore.functions import mkColor
import numpy as np
from collections import OrderedDict
from warnings import warn

qual_cmaps = ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2', 'Set1',
              'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c']


def auto_colormap(
        n_colors: int,
        cmap: str = 'hsv',
        output: str = 'mpl',
        spacing: str = 'uniform',
        alpha: float = 1.0
    ) \
        -> List[Union[QtGui.QColor, np.ndarray, str]]:
    """
    If non-qualitative map: returns list of colors evenly spread through the chosen colormap.
    If qualitative map: returns subsequent colors from the chosen colormap

    :param n_colors: Numbers of colors to return
    :param cmap:     name of colormap

    :param output:   option: 'mpl' returns RGBA values between 0-1 which matplotlib likes,
                     option: 'pyqt' returns QtGui.QColor instances that correspond to the RGBA values
                     option: 'bokeh' returns hex strings that correspond to the RGBA values which bokeh likes

    :param spacing:  option: 'uniform' returns evenly spaced colors across the entire cmap range
                     option: 'subsequent' returns subsequent colors from the cmap

    :param alpha:    alpha level, 0.0 - 1.0

    :return:         List of colors as either ``QColor``, ``numpy.ndarray``, or hex ``str`` with length ``n_colors``
    """

    valid = ['mpl', 'pyqt', 'bokeh']
    if output not in valid:
        raise ValueError(f'output must be one {valid}')

    valid = ['uniform', 'subsequent']
    if spacing not in valid:
        raise ValueError(f'spacing must be one of either {valid}')

    if alpha < 0.0 or alpha > 1.0:
        raise ValueError('alpha must be within 0.0 and 1.0')

    cm = matplotlib_color_map.get_cmap(cmap)
    cm._init()

    if output == 'pyqt':
        lut = (cm._lut * 255).view(np.ndarray)
    else:
        lut = (cm._lut).view(np.ndarray)

    lut[:, 3] *= alpha

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

        elif output == 'bokeh':
            c = tuple(c[:3] * 255)
            hc = '#%02x%02x%02x' % tuple(map(int, c))
            colors.append(hc)

        else:  # mpl
            colors.append(c)

    return colors


def get_colormap(labels: iter, cmap: str, **kwargs) -> OrderedDict:
    """
    Get a dict for mapping labels onto colors

    Any kwargs are passed to auto_colormap()

    :param labels:  labels for creating a colormap. Order is maintained if it is a list of unique elements.
    :param cmap:    name of colormap

    :return:        dict of labels as keys and colors as values
    """
    if not len(set(labels)) == len(labels):
        labels = list(set(labels))
    else:
        labels = list(labels)

    colors = auto_colormap(len(labels), cmap, **kwargs)

    return OrderedDict(zip(labels, colors))


def map_labels_to_colors(labels: iter, cmap: str, **kwargs) -> list:
    """
    Map labels onto colors according to chosen colormap

    Any kwargs are passed to auto_colormap()

    :param labels:  labels for mapping onto a colormap
    :param cmap:    name of colormap
    :return:        list of colors mapped onto the labels
    """
    mapper = get_colormap(labels, cmap, **kwargs)
    return list(map(mapper.get, labels))


class ColormapListWidget(QtWidgets.QListWidget):
    signal_colormap_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent):
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

    def get_cmap(self) -> str:
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


class WidgetEntry:
    def __init__(self, setter: callable, getter: callable, name: str):
        self.setter = setter
        self.getter = getter
        self.name = name


class WidgetRegistry:
    """
    Register widgets to conveniently store and restore their states
    """

    def __init__(self):
        self.widgets = dict()

    def register(self, widget: QtWidgets.QWidget, setter: callable, getter: callable, name: str):
        """
        Register a widget. The `setter` and `getter` methods must be interoperable

        :param widget: widget to register
        :type widget: QtWidgets.QWidget

        :param setter: widget's method to use for setting its value
        :type setter: callable

        :param getter: widget's method to use for getting its value. This value must be settable through the specified "setter" method
        :type getter: callable

        :param name: a name for this widget
        :type name: str
        """
        if (not callable(setter)) or (not callable(getter)):
            raise TypeError('setter and getter must be callable')

        self.widgets[widget] = WidgetEntry(setter=setter, getter=getter, name=name)

    def get_state(self) -> dict:
        """Get a dict of states for all registered widgets"""
        s = dict()

        for w in self.widgets.keys():
            name = self.widgets[w].name
            s[name] = self.widgets[w].getter()

        return s

    def set_state(self, state: dict):
        """Set all registered widgets from a dict"""
        for w in self.widgets.keys():
            name = self.widgets[w].name

            # account for using old saved state files whilst control widgets change
            if name not in state.keys():
                warn(f'State not available for widget: {name}\n{w}')
                continue

            s = state[name]

            self.widgets[w].setter(s)
