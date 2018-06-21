#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import abc
from caiman.utils.visualization import get_contours as caiman_get_contours
from .roi_types import *
from ...core.common import ViewerInterface
import pyqtgraphCore as pg


class AbstractBaseManager(metaclass=abc.ABCMeta):
    def __init__(self, viewer_interface: ViewerInterface):
        self.vi = viewer_interface
        self.roi_list = None

    @abc.abstractmethod
    def add_roi(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_all_states(self) -> dict:
        pass

    @abc.abstractmethod
    def restore_from_states(self, states: list):
        pass

    def get_plot_item(self) -> pg.PlotDataItem:
        return self.vi.viewer.ui.roiPlot.plot()

    def clear(self):
        if not hasattr(self, 'roi_list'):
            return
        self.roi_list.clear_()
        del self.roi_list

    def __del__(self):
        self.clear()
        # self.roi_list.list_widget.clear()
        # self.roi_list.list_widget_tags.clear()
        # self.roi_list.disconnect_all()
        # for i in range(len(self.roi_list)):



class ManagerManual(AbstractBaseManager):
    def __init__(self, ui, viewer_interface):
        super(ManagerManual, self).__init__(viewer_interface)
        self.roi_list = ROIList(ui, 'ManualROI', self.vi)

    def restore_from_states(self, states):
        pass

    def add_roi(self, shape):
        dims = self.vi.viewer.workEnv.imgdata.seq.shape
        roi_graphics_object = ManualROI.get_generic_roi_graphics_object(shape, dims)


        roi = ManualROI(self.get_plot_item(), roi_graphics_object, self.vi.viewer.getView())

        self.roi_list.append(roi)
        self.roi_list.reindex_colormap()

    def get_all_states(self):
        pass


class ManagerCNMFE(AbstractBaseManager):
    def __init__(self, ui, viewer_interface, cnmA, cnmC, idx_components, dims):
        super(ManagerCNMFE, self).__init__(viewer_interface)
        self.contours = caiman_get_contours(cnmA[:, idx_components], dims)
        self.temporal_components = cnmC[idx_components]

        self.roi_list = ROIList(ui, 'CNMFROI', viewer_interface)
        self.list_widget = self.roi_list.list_widget

    def add_all_components(self):
        for ix in range(len(self.contours)):
            self.add_roi(ix)
        self.roi_list.reindex_colormap()
            # curve_data = self.temporal_components[ix]
            # contour = self.contours[ix]
            # roi = CNMFROI(self.get_plot_item(), self.vi.viewer.getView(), curve_data, contour)
            # self.roi_list.append(roi)

    def add_roi(self, ix: int):
        curve_data = self.temporal_components[ix]
        contour = self.contours[ix]

        roi = CNMFROI(self.get_plot_item(), self.vi.viewer.getView(), curve_data, contour)

        self.roi_list.append(roi)

    def get_all_states(self):
        states = []
        for roi in self.roi_list:
            assert isinstance(roi, CNMFROI)
            states.append(roi.to_state())

    def restore_from_states(self, states: list):
        for state in states:
            roi = CNMFROI.from_state(self.get_plot_item(), state)