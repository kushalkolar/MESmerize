#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore import ScatterPlotItem, SpotItem, GraphicsLayoutWidget
from ...pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
# from ...pyqtgraphCore.functions import mkBrush
import pandas as pd
from uuid import UUID
# from collections.abc import Iterable
import numpy as np
from typing import *


class PgScatterPlot(QtCore.QObject):
    signal_spot_clicked = QtCore.pyqtSignal(UUID)  #: Emits the UUID of a spot when it is clicked

    def __init__(self, graphics_view: GraphicsLayoutWidget, parent=None):
        """
        :param graphics_view: This plot will instantiate within this GraphicsLayoutWidget
        """
        QtCore.QObject.__init__(self, parent)

        self.graphics_view = graphics_view
        self.current_datapoint = None
        self.lastClicked = []
        self.plots = self.graphics_view.addPlot(title='Scatter_Plot')
        self.plot = ScatterPlotItem(title='Scatter_Plot')
        self.plot.sigClicked.connect(self._clicked)

        self.plots.addItem(self.plot)

        self.legend = self.plots.addLegend()
        self.legend.setParentItem(self.plots)

        self.color_legend_items = []
        self.shape_legend_items = []

        # For creating legend
        self.pseudo_plots = []
        # self.legend.addItem(self.plot, 'Legend')
        
    def add_data(self, xs: np.ndarray, ys: np.ndarray, uuid_series: pd.Series,
                 color: Union[str, QtGui.QColor, QtGui.QBrush, List[Union[QtGui.QBrush, QtGui.QColor, str]]],
                 size: int = 10, **kwargs):
        """
        Add data to the plot

        :param xs:          array of x values, indices must correspond to the "ys" array
        :type xs:           np.ndarray

        :param ys:          array of y values, indices must correspond to the "xs" array
        :type ys:           np.ndarray

        :param uuid_series: series of UUID values.
                            Each SpotItem on the plot is tagged with these UUIDs, therefore
                            the indices must correspond to the "xs" and "ys" arrays.
        :type uuid_series:  pd.Series

        :param color:       Either a single color or list of colors that pqytgraph.fn.mkBrush() can accept
        :type color:        Union[str, QtGui.QColor, QtGui.QBrush, List[Union[QtGui.QBrush, QtGui.QColor, str]]]

        :param size:        spot size
        :type size:         int

        :param kwargs:      any additional kwargs that are passed to ScatterPlotItem.addPoints()
        """
        self.plot.addPoints(xs, ys, uuid=uuid_series, pen='k', brush=color, size=size, name='scatter', **kwargs)

    def _clicked(self, plot, points):
        """Called when the plot is clicked"""
        for i, p in enumerate(self.lastClicked):
            assert isinstance(p, SpotItem)
            p.setPen('k')#p._data['orig_pen'])
            p.setBrush(p._data['orig_brush'])
            # p.setSymbol(p._data['orig_symbol'])

        if len(points) == 1:
            p = points[0]
            assert isinstance(p, SpotItem)
            if isinstance(p.uuid, str):
                u = UUID(p.uuid)
            elif isinstance(p.uuid, UUID):
                u = p.uuid
            elif isinstance(p.uuid, int):
                u = p.uuid
            elif np.issubdtype(p.uuid, np.integer):
                u = p.uuid
            else:
                raise TypeError('spot uuid attribute must be either <uuid.UUID>, <str>, or <int>')

            self.signal_spot_clicked.emit(u)

        for p in points:
            assert isinstance(p, SpotItem)
            # p.setSymbol(p._data['orig_symbol'])
            p.setPen('w')

            p.setBrush('w')

        self.lastClicked = points

    def set_legend(self, colors: dict, shapes: dict = None):
        """
        Set the legend.

        :param colors: dict mapping of labels onto their corresponding colors {'label': QtGui.QColor}
        :type colors: Dict[str, Union[QtGui.QColor, QtGui.QBrush, str]]

        :param shapes: dict mapping of labels onto their corresponding shapes {'label': <shape as a str>}
        :type shapes: Dict[str, str]
        """
        self.clear_legend()

        for k in colors.keys():
            p = ScatterPlotItem()
            p.setData(x=[0], y=[0], brush=colors[k])
            self.color_legend_items.append(k)
            self.legend.addItem(p, k)
            self.pseudo_plots.append(p)

        if shapes is None:
            return

        for k in shapes.keys():
            p = ScatterPlotItem()
            p.setData(x=[0], y=[0], brush='w', symbol=shapes[k])
            self.shape_legend_items.append(k)
            self.legend.addItem(p, k)
            self.pseudo_plots.append(p)

    def clear_legend(self):
        """Clear the legend"""
        for i in range(len(self.pseudo_plots)):
            del self.pseudo_plots[0]

        for name in self.color_legend_items:
            self.legend.removeItem(name)
        self.color_legend_items.clear()

        for name in self.shape_legend_items:
            self.legend.removeItem(name)
        self.shape_legend_items.clear()

    def clear(self):
        """Clear the plot"""
        self.plot.clear()

    def export_plot(self, column: str, filetype: str = 'svg', title: str = None, error_bars: str = 'mean',
                    spots_color=None, spots_outline='black', background_color='black', axis_color='white'):
        pass