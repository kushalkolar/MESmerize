#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon March 5 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

# import sys
# sys.path.append('..')
from .pytemplates.plot_window_pytemplate import *
from .data_types import Transmission
from .history_widget import HistoryTreeWidget
from ..pyqtgraphCore import LinearRegionItem


class PlotWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Plot')
        self.show()
        self.history_widget = HistoryTreeWidget(self)

    def set_history_widget(self, sources):
        self.dockWidgetTransmissions.setWidget(self.history_widget)
        self.history_widget.fill_widget(sources)
        self.dockWidgetTransmissions.show()

    def _set_curve_color(self):
        pass


class RegionSelectionPlot(PlotWindow):
    def __init__(self, parent=None, *args):
        PlotWindow.__init__(self)
        self.linear_region = None
        self.btnSetFo = QtWidgets.QPushButton(self)
        self.gridLayout.addItem(self.btnSetFo, 0, 0, 0, 0)

    def set_linear_region(self, bounds: list):
        self.linear_region = LinearRegionItem(bounds)
        self.linear_region.setZValue(-10)
        self.graphicsView.addItem(self.linear_region)

    def get_linear_region_bounds(self) -> tuple:
        return self.linear_region.get_region()
