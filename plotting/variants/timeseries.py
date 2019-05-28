#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import seaborn as sns
from pandas import DataFrame
import numpy as np


class TimeseriesPlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        self.ax = self.fig.add_subplot(111)
        self.plot = None

    def set(self, data: np.ndarray, *args, **kwargs):
        self._set_lineplot(data, **kwargs)

    # def _set_tsplot(self):
    #     pass

    def _set_lineplot(self, data, **kwargs):
        self.clear()
        df = DataFrame(data).melt()
        self.plot = sns.lineplot(x='variable', y='value', data=df, ax=self.ax, **kwargs)
        self.draw()

    def set_single_line(self, y: np.ndarray, x: np.ndarray = None, **kwargs):
        self.clear()
        if x is None:
            x = np.arange(0, len(y))

        self.plot = sns.lineplot(x=x, y=y, ax=self.ax, **kwargs)
        self.draw()

    def clear(self):
        self.ax.cla()
