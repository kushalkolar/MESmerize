#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import seaborn as sns
from pandas import DataFrame
import numpy as np


class TimeseriesPlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        self.ax = self.fig.add_subplot(111)
        self.plot = None

        self.axs = []

    def set(self, data: np.ndarray, xticks: np.ndarray = None, **kwargs):
        """

        :param data:    2D Array of 1D curves
        :param xticks:
        :param kwargs:
        """
        self._set_lineplot(data, xticks=xticks, **kwargs)

    # def _set_tsplot(self):
    #     pass

    def _set_lineplot(self, data: np.ndarray, **kwargs):
        self.clear()
        df = DataFrame(data).melt()
        x = kwargs.pop('xticks')
        if x is not None:
            if x.size != data.shape[1]:
                raise ValueError('Length of xticks must match those of the input curves')

            xs = np.tile(x, data.shape[0])
            df.variable = xs

        self.plot = sns.lineplot(x='variable', y='value', data=df, ax=self.ax, **kwargs)
        self.draw()

    def set_single_line(self, y: np.ndarray, x: np.ndarray = None, **kwargs):
        self.clear()
        if x is None:
            x = np.linspace(0, len(y), len(y))

        self.plot = sns.lineplot(x=x, y=y, ax=self.ax, **kwargs)
        self.draw()

    def add_line(self, y: np.ndarray, x: np.ndarray = None, **kwargs):
        if x is None:
            x = np.linspace(0, len(y), len(y))

        self.axs.append(self.ax.twinx())
        sns.lineplot(x=x, y=y, ax=self.axs[-1], **kwargs)

        if 'color' in kwargs.keys():
            c = kwargs['color']
            self.axs[-1].tick_params(axis='y', colors=c)

    def clear(self):
        self.ax.cla()

    def clear_all(self):
        self.ax.cla()
        for ax in self.axs:
            ax.cla()
