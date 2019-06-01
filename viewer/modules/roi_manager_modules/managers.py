#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from caiman.utils.visualization import get_contours as caiman_get_contours
from viewer.modules.roi_manager_modules.roi_list import ROIList
from .roi_types import *
from ...core.common import ViewerInterface
import pyqtgraphCore as pg
from copy import deepcopy
from .read_imagej import read_roi_zip as read_imagej


class AbstractBaseManager(metaclass=abc.ABCMeta):
    def __init__(self, parent, ui, viewer_interface: ViewerInterface):
        self.ui = ui
        self.vi = viewer_interface
        self.roi_list = None
        self.parent = parent

    @abc.abstractmethod
    def add_roi(self, *args, **kwargs):
        pass

    def is_empty(self) -> bool:
        if not hasattr(self, 'roi_list'):
            return True
        if self.roi_list is None:
            return True
        if len(self.roi_list) < 1:
            return True
        else:
            return False

    def get_all_states(self) -> dict:
        self.vi.viewer.status_bar_label.showMessage('Saving ROIs...')
        states = {'roi_type': self.roi_list.roi_types, 'states': []}
        for roi in self.roi_list:
            state = roi.to_state()
            states['states'].append(state)
        self.vi.viewer.status_bar_label.showMessage('Finished saving ROIs!')
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
        super(ManagerManual, self).__init__(parent, ui, viewer_interface)
        self.create_roi_list()

    def create_roi_list(self):
        self.roi_list = ROIList(self.ui, 'ManualROI', self.vi)

    def restore_from_states(self, states: dict):
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        for state in states['states']:
            roi = ManualROI.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)
        # ix = 0
        # for state in states['states']:
        #     self.roi_list[ix].set_roi_graphics_object_state(state['roi_graphics_object_state'])
        #     ix += 1
        self.roi_list.reindex_colormap()

    def import_from_imagej(self, path: str):
        """
        Uses read-roi package created by Hadrien Mary.
        For licence see MESmerize/viewer/modules/roi_manager_modules/read_imagej/LICENSE
        """
        ij_roi = read_imagej(path)
        for k in ij_roi.keys():
            xs = ij_roi[k]['x']
            ys = ij_roi[k]['y']
            ps = list(zip(xs, ys))

            roi = ManualROI.from_positions(positions=ps,
                                           curve_plot_item=self.get_plot_item(),
                                           view_box=self.vi.viewer.getView())
            self.roi_list.append(roi)
        self.roi_list.reindex_colormap()

    def get_all_states(self) -> dict:
        self.vi.viewer.status_bar_label.showMessage('Saving ROIs...')
        states = {'roi_type': self.roi_list.roi_types, 'states': []}
        for ix in range(len(self.roi_list)):
            self.roi_list.set_pg_roi_plot(ix)
            state = self.roi_list[ix].to_state()
            states['states'].append(state)
        self.vi.viewer.status_bar_label.showMessage('Finished saving ROIs!')
        return states

    def add_roi(self, shape: str):
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        dims = self.vi.viewer.workEnv.imgdata.seq.shape
        roi_graphics_object = ManualROI.get_generic_roi_graphics_object(shape, dims)

        roi = ManualROI(self.get_plot_item(), roi_graphics_object, self.vi.viewer.getView())

        self.roi_list.append(roi)
        self.roi_list.reindex_colormap()


class ManagerCNMFE(AbstractBaseManager):
    def __init__(self, parent, ui, viewer_interface):
        super(ManagerCNMFE, self).__init__(parent, ui, viewer_interface)

        self.create_roi_list()
        self.list_widget = self.roi_list.list_widget
        self.input_params_dict = None
        self.idx_components = None
        self.orig_idx_components = None

        self.cnmA = None
        self.cnmb = None
        self.cnmC = None
        self.cnm_f = None
        self.cnmYrA = None

    def create_roi_list(self):
        self.roi_list = ROIList(self.ui, 'CNMFROI', self.vi)

    def add_all_components(self, cnmA, cnmb, cnmC, cnm_f, cnmYrA, idx_components, dims, input_params_dict, dfof=False):
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()
        self.cnmA = cnmA
        self.cnmb = cnmb
        self.cnmC = cnmC
        self.cnm_f = cnm_f
        self.cnmYrA = cnmYrA
        self.idx_components = idx_components
        self.orig_idx_components = deepcopy(idx_components)
        self.input_params_dict = input_params_dict

        contours = caiman_get_contours(cnmA[:, idx_components], dims)
        if dfof:
            temporal_components = cnmC
        else:
            temporal_components = cnmC[idx_components]
        self.input_params_dict = self.input_params_dict
        num_components = len(temporal_components)
        for ix in range(num_components):
            self.vi.viewer.status_bar_label.showMessage('Please wait, adding component #: '
                                                        + str(ix) + ' / ' + str(num_components))

            curve_data = temporal_components[ix]
            contour = contours[ix]
            roi = CNMFROI(self.get_plot_item(), self.vi.viewer.getView(), idx_components[ix], curve_data, contour)
            self.roi_list.append(roi)

        self.roi_list.reindex_colormap()
        self.vi.viewer.status_bar_label.showMessage('Finished adding all components!')

    def add_roi(self):
        raise NotImplementedError('Not implemented for CNMFE ROIs')

    def restore_from_states(self, states: dict):
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        for state in states['states']:
            roi = CNMFROI.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)
        self.input_params_dict = states['input_params_cnmfe']
        self.cnmA = states['cnmf_output']['cnmA']
        self.cnmb = states['cnmf_output']['cnmb']
        self.cnmC = states['cnmf_output']['cnmC']
        self.cnm_f = states['cnmf_output']['cnm_f']
        self.cnmYrA = states['cnmf_output']['cnmYrA']
        self.idx_components = states['cnmf_output']['idx_components']
        self.orig_idx_components = states['cnmf_output']['orig_idx_components']
        self.roi_list.reindex_colormap()

    def get_all_states(self) -> dict:
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()
        states = super(ManagerCNMFE, self).get_all_states()

        new_idx_components = np.array([roi.cnmf_idx for roi in self.roi_list], dtype=np.int64)

        l = [self.cnmA, self.cnmb, self.cnmC, self.cnm_f, self.cnmYrA, self.orig_idx_components, new_idx_components]
        if any(item is None for item in l):
            raise ValueError('One or more pieces of CNMF(E) data are missing')

        input_dict = {'input_params_cnmfe': self.input_params_dict,
                      'cnmf_output':
                          {
                              'cnmA': self.cnmA,
                              'cnmb': self.cnmb,
                              'cnmC': self.cnmC,
                              'cnm_f': self.cnm_f,
                              'cnmYrA': self.cnmYrA,
                              'idx_components': new_idx_components,
                              'orig_idx_components': self.orig_idx_components
                          }
                      }

        states.update(input_dict)
        return states

    def update_idx_components(self, ix: int):
        roi = self.roi_list[self.roi_list.current_index]
        self.idx_components = np.delete(self.idx_components, np.where(self.idx_components == roi.cnmf_idx)[0])
