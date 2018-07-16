#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .pytemplates.datapoint_tracer_pytemplate import *
from .HistoryWidget import HistoryTreeWidget
from pyqtgraphCore import ImageView, LinearRegionItem, mkColor
from uuid import UUID
import pandas as pd
import tifffile
import numpy as np
from viewer.modules.roi_manager_modules.roi_types import CNMFROI, ManualROI


class DatapointTracerWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Datapoint Tracer')

        self.uuid = None
        self.row = None
        self.history_trace = None
        self.peak_ix = None
        self.tstart = None
        self.tend = None

        self.ui = Ui_DatapointTracer()
        self.ui.setupUi(self)
        self.history_widget = HistoryTreeWidget(parent=self.ui.groupBoxInfo)
        self.ui.groupBoxInfo.layout().addWidget(self.history_widget)

        self.pandas_series_widget = PandasWidget(parent=self.ui.groupBoxInfo)
        self.ui.groupBoxInfo.layout().addWidget(self.pandas_series_widget)
        self.image_view = ImageView()
        self.image_item = self.image_view.getImageItem()
        self.view = self.ui.graphicsViewImage.addViewBox()
        self.view.setAspectLocked(True)
        self.view.addItem(self.image_item)

        self.peak_region = TimelineLinearRegion(self.ui.graphicsViewPlot)
        self.roi = None

    def set_widget(self, datapoint_uuid: UUID,
                   row: pd.Series,
                   history_trace: list,
                   peak_ix: int = None,
                   tstart: int = None,
                   tend: int = None):

        self.uuid = datapoint_uuid
        self.row = row
        self.history_trace = history_trace

        self.ui.lineEditUUID.setText(str(self.uuid))
        self.history_widget.fill_widget(self.history_trace)

        self.row.reset_index(inplace=True)
        self.pandas_series_widget.set_data(row)

        img = tifffile.imread(self.row['MaxProjPath'].item())
        self.image_item.setImage(img.astype(np.uint16))
        # self.image_item.setPxMode(True)
        self.image_item.resetTransform()

        self.peak_region.clear_all()
        self.ui.graphicsViewPlot.clear()
        if (tstart is not None) and (tend is not None):
            self.peak_region.add_linear_region(tstart, tend, color=mkColor('#a80035'))
        self.ui.graphicsViewPlot.plot(self.row['curve'].item())
        self.ui.graphicsViewPlot.plotItem.setZValue(1)

        if self.roi is not None:
            self.roi.remove_from_viewer()

        roi_state = self.row['ROI_State'].item()
        if roi_state['roi_type'] == 'CNMFROI':
            self.roi = CNMFROI.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)
            self.roi.get_roi_graphics_object().setBrush(mkColor('#ff0000'))
        elif roi_state['roi_type'] == 'ManualROI':
            self.roi = ManualROI.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)
        self.roi.get_roi_graphics_object().setPen(mkColor('#ff0000'))
        self.roi.add_to_viewer()

        if peak_ix is not None:
            pass



    def set_image(self):
        pass
        # roi = row['ROI_States'].value
        #


class PandasWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()
        vLayout.addLayout(hLayout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        self.pandasTv.setSortingEnabled(True)

    def set_data(self, series: pd.Series):
        model = PandasModel(series)
        self.pandasTv.setModel(model)


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.Series(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class TimelineLinearRegion:
    def __init__(self, plot_widget: PlotWidget):
        self.plot_widget = plot_widget
        self.linear_regions = []

    def add_linear_region(self, frame_start: int, frame_end: int, color: QtGui.QColor):
        linear_region = LinearRegionItem(values=[frame_start, frame_end],
                                         brush=color, movable=False, bounds=[frame_start, frame_end])
        linear_region.setZValue(0)
        linear_region.lines[0].setPen(mkColor('#350101'))
        linear_region.lines[1].setPen(mkColor('#350101'))

        self.linear_regions.append(linear_region)
        self.plot_widget.addItem(linear_region)

    def del_linear_region(self, linear_region: LinearRegionItem):
        self.plot_widget.removeItem(linear_region)
        linear_region.deleteLater()
        self.linear_regions.remove(linear_region)

    def clear_all(self):
        for region in self.linear_regions:
            self.plot_widget.removeItem(region)
            region.deleteLater()
        self.linear_regions = []