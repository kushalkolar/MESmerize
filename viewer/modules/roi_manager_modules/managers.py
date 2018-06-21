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
    def __init__(self, parent, viewer_interface: ViewerInterface):
        self.vi = viewer_interface
        self.roi_list = None
        self.parent = parent

    @abc.abstractmethod
    def add_roi(self, *args, **kwargs):
        pass

    def get_all_states(self) -> dict:
        states = {'roi_type': self.roi_list.roi_types, 'states': []}
        for roi in self.roi_list:
            state = roi.to_state()
            states['states'].append(state)
        return states

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
    def __init__(self, parent, ui, viewer_interface):
        super(ManagerManual, self).__init__(parent, viewer_interface)
        self.roi_list = ROIList(ui, 'ManualROI', self.vi)

    def restore_from_states(self, states: dict):
        for state in states['states']:
            roi = ManualROI.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)
        ix = 0
        for state in states['states']:
            self.roi_list[ix].set_roi_graphics_object_state(state['roi_graphics_object_state'])
            ix += 1
        self.roi_list.reindex_colormap()


    def add_roi(self, shape):
        dims = self.vi.viewer.workEnv.imgdata.seq.shape
        roi_graphics_object = ManualROI.get_generic_roi_graphics_object(shape, dims)

        roi = ManualROI(self.get_plot_item(), roi_graphics_object, self.vi.viewer.getView())

        self.roi_list.append(roi)
        self.roi_list.reindex_colormap()


class ManagerCNMFE(AbstractBaseManager):
    def __init__(self, parent, ui, viewer_interface):
        super(ManagerCNMFE, self).__init__(parent, viewer_interface)

        self.roi_list = ROIList(ui, 'CNMFROI', viewer_interface)
        self.list_widget = self.roi_list.list_widget
        self.input_params_dict = None

    def add_all_components(self, cnmA, cnmC, idx_components, dims, input_params_dict):
        contours = caiman_get_contours(cnmA[:, idx_components], dims)
        temporal_components = cnmC[idx_components]
        self.input_params_dict = self.input_params_dict

        for ix in range(len(contours)):
            curve_data = temporal_components[ix]
            contour = contours[ix]
            roi = CNMFROI(self.get_plot_item(), self.vi.viewer.getView(), curve_data, contour)
            self.roi_list.append(roi)

        self.roi_list.reindex_colormap()

    def add_roi(self, ix: int):
        raise NotImplementedError('Not implemented for CNMFE ROIs')

    def restore_from_states(self, states: dict):
        for state in states['states']:
            roi = CNMFROI.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)
        self.roi_list.reindex_colormap()

    def get_all_states(self) -> dict:
        states = super(ManagerCNMFE, self).get_all_states()
        input_dict = {'input_params_cnmfe': self.input_params_dict}
        states.update(input_dict)
        return states
