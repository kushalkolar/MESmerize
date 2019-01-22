#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore import ScatterPlotItem, SpotItem, GraphicsLayoutWidget
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import pandas as pd
from uuid import UUID
import numpy as np


class ScatterPlot(QtCore.QObject):
    signal_spot_clicked = QtCore.pyqtSignal(UUID)

    def __init__(self, graphics_view: GraphicsLayoutWidget, parent=None):
        QtCore.QObject.__init__(self, parent)

        self.graphics_view = graphics_view
        self.current_datapoint = None
        self.lastClicked = []
        self.plots = self.graphics_view.addPlot(title='LDA')
        self.plot = ScatterPlotItem(title='LDA')
        self.plot.sigClicked.connect(self._clicked)

        self.plots.addItem(self.plot)

    def add_data(self, xs, ys, uuid_series: pd.Series, color: QtGui.QColor):
        self.plot.addPoints(xs, ys, uuid=uuid_series, pen='k', brush=color, symbol='o', size=10)

    def _clicked(self, plot, points):
        for i, p in enumerate(self.lastClicked):
            assert isinstance(p, SpotItem)
            p.setPen('k')#p._data['orig_pen'])
            p.setBrush(p._data['orig_brush'])

        if len(points) == 1:
            p = points[0]
            assert isinstance(p, SpotItem)
            self.signal_spot_clicked.emit(p.uuid)

        for p in points:
            assert isinstance(p, SpotItem)
            p.setPen('w')
            p.setBrush('w')

        self.lastClicked = points

    @property
    def spot_color(self, group: str):
        pass

    @spot_color.setter
    def spot_color(self, d: dict):
        pass

    @property
    def spot_outline(self):
        pass

    @spot_outline.setter
    def spot_outline(self, color):
        pass

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, title: str):
        pass

    @property
    def spot_size(self) -> int:
        pass

    @spot_size.setter
    def spot_size(self, size: int):
        pass

    def clear(self):
        self.plot.clear()

    def export_plot(self, column: str, filetype: str = 'svg', title: str = None, error_bars: str = 'mean',
                    spots_color=None, spots_outline='black', background_color='black', axis_color='white'):
        pass