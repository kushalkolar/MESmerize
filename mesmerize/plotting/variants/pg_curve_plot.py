#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore import GraphicsLayoutWidget, LegendItem
from ...pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import numpy as np
import pandas as pd
from uuid import UUID
from typing import List, SupportsFloat


class PgCurvePlot(QtCore.QObject):
    signal_spot_clicked = QtCore.pyqtSignal(UUID)

    def __init__(self, graphics_view: GraphicsLayoutWidget, parent=None):
        QtCore.QObject.__init__(self, parent)

        self.graphics_view = graphics_view
        self.plots = []
        self.curve_plots = []
        self.title = ''
        self.current_datapoint = None
        self.lastClicked = []
        self.plot_items = []

    def add_plot(self, title: str):
        # plot = PlotDataItem()
        plot = self.graphics_view.addPlot(title=title)
        self.plots.append(plot)

    def add_data_to_plot(self, ix: int, data_series: pd.Series, name, color):
        if ix > len(self.plots) - 1:
            raise IndexError('Plot index out of range.')

        not_nan = data_series.notna()
        yvals = data_series[not_nan].values

        for yval in yvals:
            self.plots[ix].plot(y=yval, pen=color)

    def clear_plot(self):
        for plot in self.plots:
            self.graphics_view.removeItem(plot)
            plot.deleteLater()
        del self.plots
        self.plots = []

        # self.graphics_view.scene().clear()
        # for item in self.graphics_view.items():
        #     self.graphics_view.removeItem(item)

    def export_all_plots(self):
        pass

    def export_plot(self, column: str, filetype: str = 'svg', title: str = None, error_bars: str = 'mean',
                    spots_color=None, spots_outline='black', background_color='black', axis_color='white'):
        pass

    def get_range(self, plot_ix: int) -> list:
        return self.plots[plot_ix].vb.viewRange()

    def set_range(self, plot_ix, x_range: list, y_range: list):
        self.plots[plot_ix].setRange(xRange=x_range, yRange=y_range)

    def create_legend(self, plot_ix):
        legend = LegendItem()
        legend.setParentItem(self.plots[plot_ix])
