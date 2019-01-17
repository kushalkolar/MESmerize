#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle as RectangularPatch
from matplotlib.lines import Line2D


class ZSTPlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        sns.set()
        self.ax = self.fig.add_subplot(111)
        self.data = None
        self._highlight = None
        self.highlighted_index = None

        self.canvas.mpl_connect('button_press_event', self.highlight_row)

        self.stimulus_indicators = []

    def set(self, data: np.ndarray, *args, **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.data = data
        self.plot = sns.heatmap(data, *args, ax=self.ax, **kwargs)

    def highlight_row(self, ev):
        ix = ev.ydata
        if ix is None:
            return
        ix = int(ix)
        self.highlighted_index = ix
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

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ZSTPlot()
    w.show()
    data = np.load('/home/kushal/Sars_stuff/palp_project_mesmerize/zst_data.npy')
    w.set(data, cmap='jet')
    w.add_stimulus_indicator(144, 288, 'k')
    app.exec()
