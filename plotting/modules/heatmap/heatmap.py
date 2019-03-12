#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np
from seaborn import heatmap as seaborn_heatmap
from matplotlib.patches import Rectangle as RectangularPatch
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.patches import Patch as MPatch
from matplotlib import rcParams
from pandas import Series


class Heatmap(MatplotlibWidget):
    signal_row_selection_changed = QtCore.pyqtSignal(int)

    def __init__(self, highlight_mode='row'):
        MatplotlibWidget.__init__(self)
        rcParams['image.interpolation'] = None
        self.ax_heatmap = self.fig.add_subplot(111)
        self.ax_heatmap.get_yaxis().set_visible(False)

        self.ax_ylabel_bar = self.ax_heatmap.twiny()

        self.fig.subplots_adjust(right=0.8)
        self.cbar_ax = self.fig.add_axes([0.85, 0.15, 0.05, 0.7])
        self.data = None
        self._highlight = None
        self.highlighted_index = None

        self.stimulus_indicators = []

        if highlight_mode == 'row':
            self.canvas.mpl_connect('button_press_event', self.highlight_row)
        elif highlight_mode == 'item':
            pass

    def set(self, data: np.ndarray, *args, ylabels_bar: Series = None, cmap_ylabels_bar: str = 'tab20', **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.ax_heatmap.cla()
        self._highlight = None
        self.cbar_ax.cla()
        self.data = data

        # labels = kwargs.pop('ylabels_bar')
        # cmap_ylabels_bar = kwargs.pop('cmap_ylabels_bar')

        self.plot = seaborn_heatmap(data, *args, ax=self.ax_heatmap, cbar_ax=self.cbar_ax, **kwargs)

        if ylabels_bar is not None:
            self._set_ylabel_bar(ylabels_bar, cmap=cmap_ylabels_bar)

        self.draw()

    def _set_ylabel_bar(self, labels : Series, cmap: str = 'tab20'):
        assert isinstance(labels, Series)

        self.ax_ylabel_bar.cla()

        [[x1, y1], [x2, y2]] = self.ax_heatmap.get_position().get_points()
        bb = Bbox.from_extents([[0.123, y1], [0.11, y2]])
        self.ax_ylabel_bar.set_position(bb)

        # self.ax_ylabel_bar.get_xaxis().set_visible(False)set
        # self.ax_ylabel_bar.get_yaxis().set_visible(False)
        self.ax_ylabel_bar.axis('off')

        labels_unique = labels.unique()
        colors_map = {}

        for ix, c in enumerate(labels_unique):
            colors_map.update({labels_unique[ix]: ix})

        colors = labels.map(colors_map)
        color_labels_array = np.expand_dims(colors.values, axis=1)

        ylabel_bar = self.ax_ylabel_bar.imshow(color_labels_array, aspect='auto', cmap=cmap)

        cs = np.unique(color_labels_array.ravel())
        colors = [ylabel_bar.cmap(ylabel_bar.norm(c)) for c in cs]
        ps = [MPatch(color=colors[i], label=labels_unique[i]) for i in range(len(cs))]
        self.ax_ylabel_bar.legend(handles=ps, bbox_to_anchor=(1,1))

    def highlight_row(self, ev):
        if type(ev) is int:
            ix = ev
        else:
            ix = ev.ydata
            ix = int(ix)
            if ix is None:
                return
        self.highlighted_index = ix
        self.signal_row_selection_changed.emit(ix)
        if self._highlight is not None:
            self._highlight.remove()
        self._highlight = self.plot.add_patch(RectangularPatch((0, ix), self.data.shape[1], 1, facecolor='w', edgecolor='k', lw=3, alpha=0.5))
        self.draw()

    def add_stimulus_indicator(self, start: int, end: int, color: str):
        for t in [start, end]:
            x = np.array([t, t])
            y = np.array([0, self.data.shape[0]])
            line = Line2D(x, y, lw=3, color=color)
            self.stimulus_indicators.append(line)
            self.plot.add_line(line)


class Clustermap(Heatmap):
    def __init__(self):
        Heatmap.__init__(self)

    def set(self, data: np.ndarray, *args, **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.ax_heatmap.cla()
        self.cbar_ax.cla()
        self.data = data
        self.plot = sns.clustermap(data, *args, ax=self.ax_heatmap, cbar_ax=self.cbar_ax, **kwargs)
        self.draw()
