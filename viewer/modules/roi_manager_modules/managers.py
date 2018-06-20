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


class AbstractBaseManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add_roi(self):
        pass

    @abc.abstractmethod
    def del_roi(self):
        pass

    @abc.abstractmethod
    def save_all_states(self):
        pass

    @abc.abstractmethod
    def restore_from_states(self, states):
        pass

    def set_tag(self, roi_def: str, tag: str):
        pass


class ManagerManual(AbstractBaseManager):
    def restore_from_states(self, states):
        pass

    def del_roi(self):
        pass

    def add_roi(self):
        pass

    def save_all_states(self):
        pass


class ManagerCNMFE(AbstractBaseManager):
    def __init__(self, viewer, cnmA, cnmC, idx_components, dims):
        super(ManagerCNMFE, self).__init__()
        self.contours = caiman_get_contours(cnmA[:, idx_components], dims)
        self.temporal_components = cnmC[idx_components]

        self.roi_list = ROIList(CNMFROI, viewer)
        self.list_widget = self.roi_list.list_widget

        self.vi = ViewerInterface(viewer_reference=viewer)

    def add_all_components(self):
        for ix in range(len(self.contours)):
            curve_data = self.temporal_components[ix]
            contour = self.contours[ix]

            plot_item = self.vi.viewer.ui.roiPlot.plot()
            roi = CNMFROI(plot_item, self.vi.viewer.getView(), curve_data, contour)

            self.roi_list.append(roi)

    def delete_component(self, reason: str):
        pass

    def del_roi(self):
        pass

    def add_roi(self):
        pass

    def save_all_states(self):
        pass

    def restore_from_states(self, states):
        pass
