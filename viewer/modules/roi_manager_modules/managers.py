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

    @abc.abstractmethod
    def add_roi(self, *args, **kwargs):
        pass

    def del_roi(self, ix: int):
        del self.roi_list[ix]

    @abc.abstractmethod
    def save_all_states(self):
        pass

    @abc.abstractmethod
    def restore_from_states(self, states):
        pass

    def __del__(self):
        for i in range(len(self.roi_list)):
            self.del_roi(i)


class ManagerManual(AbstractBaseManager):
    def __init__(self, viewer_interface):
        super(ManagerManual, self).__init__(viewer_interface)
        self.roi_list = ROIList(ManualROI, self.vi.viewer)

    def restore_from_states(self, states):
        pass

    def del_roi(self, ix):
        pass

    def add_roi(self):
        pass

    def save_all_states(self):
        pass


class ManagerCNMFE(AbstractBaseManager):
    def __init__(self, viewer_interface, cnmA, cnmC, idx_components, dims):
        super(ManagerCNMFE, self).__init__(viewer_interface)
        self.contours = caiman_get_contours(cnmA[:, idx_components], dims)
        self.temporal_components = cnmC[idx_components]

        self.roi_list = ROIList(CNMFROI, viewer_interface)
        self.list_widget = self.roi_list.list_widget

    def add_all_components(self):
        for ix in range(len(self.contours)):
            self.add_roi(ix)

    def delete_component(self, reason: str):
        pass

    def add_roi(self, ix: int):
        curve_data = self.temporal_components[ix]
        contour = self.contours[ix]

        roi = CNMFROI(self.get_plot_item(), self.vi.viewer.getView(), curve_data, contour)

        self.roi_list.append(roi)

    def get_plot_item(self) -> pg.PlotDataItem:
        return self.vi.viewer.ui.roiPlot.plot()

    def save_all_states(self):
        states = []
        for roi in self.roi_list:
            assert isinstance(roi, CNMFROI)
            states.append(roi.to_state())

    def restore_from_states(self, states: list):
        for state in states:
            roi = CNMFROI.from_state(self.get_plot_item(), state)