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
from ...analysis.history_widget import HistoryTreeWidget
from ...pyqtgraphCore import ImageView, LinearRegionItem, mkColor, PlotDataItem
from uuid import UUID
import pandas as pd
import tifffile
import numpy as np
import pickle
from ...viewer.modules.roi_manager_modules.roi_types import CNMFROI, ManualROI, ScatterROI, VolCNMF, VolMultiCNMFROI
# from ...viewer.core import ViewerWorkEnv, ViewerUtils
from ...common import get_window_manager, get_project_manager
# from common import configuration
import os
from typing import Union, Optional
from ...common.utils import draw_graph
from ...analysis.data_types import HistoryTrace
from copy import deepcopy

region_data_types = ['_pf_uuid', '_ST_uuid']


class DatapointTracerWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Datapoint Tracer')

        self.uuid = None
        self.row = None
        self.proj_path = None
        self.sample_id = None
        self.previous_sample_id_projection = None
        self.history_trace = None
        self.peak_ix = None
        self.tstart = None
        self.tend = None

        self.is_3d = False

        self.ui = Ui_DatapointTracer()
        self.ui.setupUi(self)
        self.history_widget = HistoryTreeWidget(parent=self.ui.groupBoxInfo)
        self.ui.groupBoxInfo.layout().addWidget(self.history_widget)

        self.pandas_series_widget = HistoryTreeWidget(parent=self.ui.groupBoxInfo)

        self.ui.groupBoxInfo.layout().addWidget(self.pandas_series_widget)
        self.image_view = ImageView()
        self.image_view.tVals = np.arange(0, 100)
        self.image_item = self.image_view.getImageItem()
        self.view = self.ui.graphicsViewImage.addViewBox()
        self.view.setAspectLocked(True)
        self.view.addItem(self.image_item)

        self.peak_region = TimelineLinearRegion(self.ui.graphicsViewPlot)
        self.roi = None

        self.plot_data: np.ndarray = None
        self.plot_data_item: PlotDataItem = None

        self.ui.radioButtonMaxProjection.clicked.connect(lambda x: self.set_image('max'))
        self.ui.radioButtonSTDProjection.clicked.connect(lambda x: self.set_image('std'))

        self.ui.pushButtonOpenInViewer.clicked.connect(self.open_in_viewer)
        self.ui.pushButtonOpenAnalysisGraph.clicked.connect(self.open_analysis_graph)

    def set_widget(self, datapoint_uuid: UUID, data_column_curve: str, row: pd.Series, proj_path: str,
                   history_trace: Optional[list] = None, peak_ix: Optional[int] = None, tstart: Optional[int] = None,
                   tend: Optional[int] = None, roi_color: Optional[Union[str, float, int, tuple]] = 'ff0000',
                   clear_linear_regions: bool = True):
        """
        Set the widget from the datapoint.

        :param datapoint_uuid:      appropriate UUID for the datapoint (such as uuid_curve or _pfeature_uuid)
        :param data_column_curve:   data column containing an array to plot
        :param row:                 DataFrame row that corresponds to the datapoint
        :param proj_path:           root dir of the project the datapoint comes from, used for finding max & std projections
        :param history_trace:       history trace of the datablock the datapoint comes from
        :param peak_ix:             Deprecated
        :param tstart:              lower bounds for drawing `LinearRegionItem`
        :param tend:                upper bounds for drawing `LinearRegionItem`
        :param roi_color:           color for drawing the spatial bounds of the ROI
        """
        self.uuid = datapoint_uuid
        self.row = row
        self.proj_path = proj_path
        self.sample_id = self.row['SampleID']

        self.ui.label_zlevel.clear()

        if isinstance(self.sample_id, pd.Series):
            self.sample_id = self.sample_id.item()

        if not isinstance(self.sample_id, str):
            raise ValueError('SampleID datatype is not str or pandas.Series. '
                             'Something is wrong, it is this datatype :' + str(type(self.sample_id)))

        if history_trace is None:
            self.history_trace = []

        img_info_path = row['ImgInfoPath']
        if isinstance(img_info_path, pd.Series):
            img_info_path = img_info_path.item()
        img_info_path = os.path.join(self.proj_path, img_info_path)
        preprocess_history = pickle.load(open(img_info_path, 'rb'))['history_trace']

        self.history_trace = preprocess_history + history_trace

        self.ui.lineEditUUID.setText(str(self.uuid))
        self.history_widget.fill_widget(self.history_trace)

        row_dict = row.to_dict()
        for k in row_dict.keys():
            row_dict[k] = row_dict[k][row.index.item()]
        self.pandas_series_widget.fill_widget(row_dict)
        # self.pandas_series_widget.collapseAll()

        if self.ui.radioButtonMaxProjection.isChecked():
            self.img_proj = 'max'
        elif self.ui.radioButtonSTDProjection.isChecked():
            self.img_proj = 'std'

        if clear_linear_regions:
            self.peak_region.clear_all()

        if (tstart is not None) and (tend is not None):
            self.peak_region.add_linear_region(tstart, tend, color=mkColor('#a80035'))

        # get the plot data
        try:
            self.plot_data = self.row[data_column_curve].item()
        except:
            self.plot_data = self.row[data_column_curve]

        # get a new pyqtgraph plot data item
        if self.plot_data_item is None:
            self.plot_data_item = self.ui.graphicsViewPlot.plot(self.plot_data)

        # or set the existing one
        else:
            self.plot_data_item.clear()
            self.plot_data_item.setData(self.plot_data)

        self.plot_data_item.setPen('w', width=2)

        self.plot_data_item.setZValue(1)

        if self.roi is not None:
            self.roi.remove_from_viewer()
        try:
            roi_state = self.row['ROI_State'].item()
        except:
            roi_state = self.row['ROI_State']

        if roi_state['roi_type'] in ['CNMFROI', 'ScatterROI']:
            self.set_image(self.img_proj)
            ROIClass = globals()[roi_state['roi_type']]
            self.roi = ROIClass.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)
            self.roi.get_roi_graphics_object().setBrush(mkColor(roi_color))

        elif roi_state['roi_type'] == 'ManualROI':
            self.set_image(self.img_proj)
            self.roi = ManualROI.from_state(curve_plot_item=None, view_box=self.view, state=roi_state)

        elif roi_state['roi_type'] in ['VolCNMF']:
            self.is_3d = True
            self.zcenter = roi_state['zcenter']
            self.set_image(self.img_proj)

            self.roi = VolCNMF.from_state(curve_plot_item=None, view_box=self.view, state=roi_state, zlevel=self.zcenter)
            self.roi.get_roi_graphics_object().setBrush(mkColor(roi_color))

        elif roi_state['roi_type'] in ['VolMultiCNMFROI']:
            self.is_3d = True
            self.zcenter = roi_state['zcenter']
            self.set_image(self.img_proj)

            self.roi = VolMultiCNMFROI.from_state(
                curve_plot_item=None, view_box=self.view, state=roi_state, zlevel=self.zcenter
            )

        self.roi.get_roi_graphics_object().setPen(mkColor(roi_color))
        self.roi.add_to_viewer()

        if peak_ix is not None:
            pass

    def set_image(self, projection: str):
        """
        Set either the max or std projection image

        :param projection: one of either 'max' or 'std'
        """
        if f'{self.sample_id}{projection}' == self.previous_sample_id_projection:
            if not self.is_3d:
                return

        img_uuid = self.row['ImgUUID']

        if isinstance(img_uuid, pd.Series):
            img_uuid = img_uuid.item()

        if not isinstance(img_uuid, str):
            raise ValueError('Datatype for Projection Path must be pandas.Series or str, it is currently : ' + str(
                type(img_uuid)))

        if projection == 'max':
            suffix = '_max_proj'
        elif projection == 'std':
            suffix = '_std_proj'
        else:
            raise ValueError('Can only accept "max" and "std" arguments')

        self.ui.label_zlevel.clear()

        if self.is_3d:
            suffix += f'-{self.zcenter}'
            self.ui.label_zlevel.setText(f'Showing plane #: {self.zcenter}   ')

        img_path = os.path.join(self.proj_path, 'images', f'{self.sample_id}-_-{img_uuid}{suffix}.tiff')

        img = tifffile.imread(img_path)

        # z = np.zeros(img.shape)

        # img = np.dstack((img, z))

        # if img.shape[0] > img.shape[1]:
        #     x, y = (0, 1)
        # else:
        #     x,y = (1, 0)
        vmin = np.nanmin(img)
        vmax = np.nanmedian(img) + (10 * np.nanstd(img))
        self.image_view.setImage(img, axes={'x': 0, 'y': 1}, levels=(vmin, vmax))

        self.previous_sample_id_projection = f'{self.sample_id}{projection}'
        # self.image_item.setImage(img.T.astype(np.uint16))
        # self.image_item.resetTransform()

    def open_in_viewer(self):
        """
        Open the parent Sample of the current datapoint.
        """
        w = get_window_manager().get_new_viewer_window()
        w.open_from_dataframe(proj_path=self.proj_path, row=self.row)

    def open_analysis_graph(self):
        cleaned = HistoryTrace.clean_history_trace(deepcopy(self.history_trace))
        draw_graph(cleaned, view=True)


class TimelineLinearRegion:
    def __init__(self, plot_widget: PlotWidget):
        self.plot_widget = plot_widget
        self.linear_regions = []

    def add_linear_region(self, frame_start: int, frame_end: int, color: QtGui.QColor) -> LinearRegionItem:
        linear_region = LinearRegionItem(values=[frame_start, frame_end],
                                         brush=color, movable=False, bounds=[frame_start, frame_end])
        linear_region.setZValue(0)
        linear_region.lines[0].setPen(mkColor('#000000'))
        linear_region.lines[1].setPen(mkColor('#000000'))

        self.linear_regions.append(linear_region)
        self.plot_widget.addItem(linear_region)

        return linear_region

    def del_linear_region(self, linear_region: LinearRegionItem):
        self.plot_widget.removeItem(linear_region)
        linear_region.deleteLater()
        self.linear_regions.remove(linear_region)

    def clear_all(self):
        for region in self.linear_regions:
            self.plot_widget.removeItem(region)
            region.deleteLater()
        self.linear_regions = []
