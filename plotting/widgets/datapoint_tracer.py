#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .datapoint_tracer_pytemplate import *
from analysis.history_widget import HistoryTreeWidget
from pyqtgraphCore import ImageView, LinearRegionItem, mkColor
from uuid import UUID
import pandas as pd
import tifffile
import numpy as np
from viewer.modules.roi_manager_modules.roi_types import CNMFROI, ManualROI
# from common import configuration


class DatapointTracerWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Datapoint Tracer')

        self.uuid = None
        self.row = None
        self.proj_path = None
        self.sample_id = None
        self.history_trace = None
        self.peak_ix = None
        self.tstart = None
        self.tend = None

        self.ui = Ui_DatapointTracer()
        self.ui.setupUi(self)
        self.history_widget = HistoryTreeWidget(parent=self.ui.groupBoxInfo)
        self.ui.groupBoxInfo.layout().addWidget(self.history_widget)

        self.pandas_series_widget = HistoryTreeWidget(parent=self.ui.groupBoxInfo)

        self.ui.groupBoxInfo.layout().addWidget(self.pandas_series_widget)
        self.image_view = ImageView()
        self.image_item = self.image_view.getImageItem()
        self.view = self.ui.graphicsViewImage.addViewBox()
        self.view.setAspectLocked(True)
        self.view.addItem(self.image_item)

        self.peak_region = TimelineLinearRegion(self.ui.graphicsViewPlot)
        self.roi = None

        self.ui.radioButtonMaxProjection.clicked.connect(lambda x: self.set_image('max'))
        self.ui.radioButtonSTDProjection.clicked.connect(lambda x: self.set_image('std'))

    def set_widget(self, datapoint_uuid: UUID,
                   data_column_curve: str,
                   row: pd.Series,
                   proj_path: str,
                   history_trace: list = None,
                   peak_ix: int = None,
                   tstart: int = None,
                   tend: int = None):

        self.uuid = datapoint_uuid
        self.row = row
        self.proj_path = proj_path
        self.sample_id = self.row['SampleID']

        if isinstance(self.sample_id, pd.Series):
            self.sample_id = self.sample_id.item()

        if not isinstance(self.sample_id, str):
            raise ValueError('SampleID datatype is not str or pandas.Series. '
                             'Something is wrong, it is this datatype :' + str(type(self.sample_id)))

        if history_trace is None:
            self.history_trace = []
        self.history_trace = history_trace

        self.ui.lineEditUUID.setText(str(self.uuid))
        self.history_widget.fill_widget(self.history_trace)

        row_dict = row.to_dict()
        for k in row_dict.keys():
            row_dict[k] = row_dict[k][row.index.item()]
        self.pandas_series_widget.fill_widget(row_dict)
        self.pandas_series_widget.collapseAll()

        if self.ui.radioButtonMaxProjection.isChecked():
            self.set_image('max')
        elif self.ui.radioButtonSTDProjection.isChecked():
            self.set_image('std')

        self.peak_region.clear_all()
        self.ui.graphicsViewPlot.clear()
        if (tstart is not None) and (tend is not None):
            self.peak_region.add_linear_region(tstart, tend, color=mkColor('#a80035'))
        try:
            self.ui.graphicsViewPlot.plot(self.row[data_column_curve].item())
        except:
            self.ui.graphicsViewPlot.plot(self.row[data_column_curve])

        self.ui.graphicsViewPlot.plotItem.setZValue(1)

        if self.roi is not None:
            self.roi.remove_from_viewer()
        try:
            roi_state = self.row['ROI_State'].item()
        except:
            roi_state = self.row['ROI_State']

        if roi_state['roi_type'] == 'CNMFROI':
            self.roi = CNMFROI.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)
            self.roi.get_roi_graphics_object().setBrush(mkColor('#ff0000'))
        elif roi_state['roi_type'] == 'ManualROI':
            self.roi = ManualROI.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)
        self.roi.get_roi_graphics_object().setPen(mkColor('#ff0000'))
        self.roi.add_to_viewer()

        if peak_ix is not None:
            pass

    def set_image(self, projection: str):
        img_uuid = self.row['ImgUUID']

        if isinstance(img_uuid, pd.Series):
            img_uuid = img_uuid.item()

        if not isinstance(img_uuid, str):
            raise ValueError('Datatype for Projection Path must be pandas.Series or str, it is currently : ' + str(
                type(img_uuid)))

        if projection == 'max':
            suffix = '_max_proj.tiff'
        elif projection == 'std':
            suffix = '_std_proj.tiff'
        else:
            raise ValueError('Can only accept "max" and "std" arguments')

        img_path = self.proj_path + '/images/' + self.sample_id + '-_-' + img_uuid + suffix

        img = tifffile.imread(img_path)

        self.image_item.setImage(img.astype(np.uint16))
        self.image_item.resetTransform()


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
