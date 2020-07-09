#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ....viewer.modules.roi_manager_modules.roi_list import ROIList
from .roi_types import *
from ...core.common import ViewerUtils
from .... import pyqtgraphCore as pg
from copy import deepcopy
from .read_imagej import read_roi_zip as read_imagej
from ....common.configuration import HAS_CAIMAN

if HAS_CAIMAN:
    from caiman.utils.visualization import get_contours as caiman_get_contours
    from caiman.source_extraction.cnmf.cnmf import load_CNMF


class AbstractBaseManager(metaclass=abc.ABCMeta):
    """Base ROI Manager"""
    def __init__(self, parent, ui, viewer_interface: ViewerUtils):
        """
        Set the common attributes

        :param parent: The ModuleGUI QDockWidget instance
        :param ui:  The ui of the ModuleGUI QDockWidget instance,
        :param viewer_interface:    A ViewerUtils instance for accessing the Viewer the parent QDockWidget belongs to
        """
        self.ui = ui
        self.vi = viewer_interface
        self.roi_list = None  #: The ROIList instance that stores the list of ROIs
        self.parent = parent

        self.metadata = None

    @abc.abstractmethod
    def add_roi(self, *args, **kwargs):
        """Method for adding an ROI, must be implemented in subclass"""
        pass

    def is_empty(self) -> bool:
        """Return true if the ROI list is empty, else return False"""
        if not hasattr(self, 'roi_list'):
            return True
        if self.roi_list is None:
            return True
        if len(self.roi_list) < 1:
            return True
        else:
            return False

    def get_all_states(self) -> dict:
        """
        Get the ROI states for all ROIs in self.roi_list so that they can be restored.
        The appropriate manager is instantiated based on the 'roi_type' key of the returned dict
        """
        self.vi.viewer.status_bar_label.showMessage('Saving ROIs...')
        # the key 'roi_type' determines which Manager subclass should be used, and 'states' are the actual ROI states
        states = {
            'roi_type': self.roi_list.roi_types.__name__,
            'states': [],
            'metadata': self.metadata
        }

        for roi in self.roi_list:
            state = roi.to_state()
            states['states'].append(state)
        self.vi.viewer.status_bar_label.showMessage('ROIs saved!')
        return states

    def restore_from_states(self, states: dict):
        if 'metadata' in states.keys():
            self.metadata = states['metadata']

    def get_plot_item(self) -> pg.PlotDataItem:
        """Get the viewer plot item that is associated to these ROIs"""
        return self.vi.viewer.ui.roiPlot.plot()

    def clear(self):
        """Cleanup of all ROIs in the list"""
        if not hasattr(self, 'roi_list'):
            return
        self.roi_list.clear_()
        del self.roi_list

    def __del__(self):
        """Cleanup of all ROIs in the list and deletes the manager instance. Used when switching modes."""
        self.clear()
        # self.roi_list.list_widget.clear()
        # self.roi_list.list_widget_tags.clear()
        # self.roi_list.disconnect_all()
        # for i in range(len(self.roi_list)):


class ManagerManual(AbstractBaseManager):
    """The Manager for the Manual mode"""
    def __init__(self, parent, ui, viewer_interface):
        super(ManagerManual, self).__init__(parent, ui, viewer_interface)
        self.create_roi_list()

    def create_roi_list(self):
        """Create a new empty ROI list instance for storing Manual ROIs"""
        self.roi_list = ROIList(self.ui, ManualROI, self.vi)

    def add_roi(self, shape: str) -> ManualROI:
        """
        Add an ROI to the list

        :param shape: either "PolyLineROI" or "EllipseROI"
        """
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        dims = self.vi.viewer.workEnv.imgdata.seq.shape
        roi_graphics_object = ManualROI.get_generic_roi_graphics_object(shape, dims)

        roi = ManualROI(self.get_plot_item(), roi_graphics_object, self.vi.viewer.getView())

        self.roi_list.append(roi)
        self.roi_list.reindex_colormap()

        return roi

    def restore_from_states(self, states: dict):
        """Restore ROIs from states"""
        super(ManagerManual, self).restore_from_states(states)
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

    def get_all_states(self) -> dict:
        """Get the ROI states so that they can be restored later"""
        self.vi.viewer.status_bar_label.showMessage('Saving ROIs...')

        states = {
            'roi_type': self.roi_list.roi_types.__name__,
            'states': [],
            'metadata': self.metadata
        }

        for ix in range(len(self.roi_list)):
            self.roi_list.set_pg_roi_plot(ix)
            state = self.roi_list[ix].to_state()
            states['states'].append(state)
        self.vi.viewer.status_bar_label.showMessage('Finished saving ROIs!')
        return states

    def import_from_imagej(self, path: str):
        """
        Uses read-roi package created by Hadrien Mary.
        https://pypi.org/project/read-roi/

        :param path: Full path to the ImageJ ROIs zip file
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


class ManagerScatterROI(AbstractBaseManager):
    """Manager for unmoveable ROIs drawn using scatterplots"""
    def __init__(self, parent, ui, viewer_interface: ViewerUtils):
        super(ManagerScatterROI, self).__init__(parent, ui, viewer_interface)
        self.create_roi_list()
        self.list_widget = self.roi_list.list_widget

    def add_roi(self, curve: np.ndarray,
                xs: np.ndarray,
                ys: np.ndarray,
                metadata: dict = None,
                dfof_data: np.ndarray = None,
                spike_data: np.ndarray = None) \
            -> ScatterROI:
        """
        Add a single ROI

        `xs` and `ys` arguments are 1D numpy arrays.

        :param curve:       curve data, 1-D array, y values/intensity values
        :param xs:          x-values for the scatter plot to spatially illustrate the ROI
        :param ys:          corresponding y-values for the scatter plot to spatially illustrate the ROI
        :param metadata:    Any metadata for this ROI
        :return:            ScatterROI object
        """
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        roi = ScatterROI(
            curve_plot_item=self.get_plot_item(),
            view_box=self.vi.viewer.getView(),
            curve_data=curve,
            xs=xs,
            ys=ys,
            dfof_data=dfof_data,
            spike_data=spike_data
        )

        roi.metadata = metadata
        self.roi_list.append(roi)
        self.roi_list.reindex_colormap()

        return roi

    def restore_from_states(self, states: dict):
        """Restore from states, such as when these ROIs are saved with a Project Sample"""
        super(ManagerScatterROI, self).restore_from_states(states)

        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        for state in states['states']:
            roi = ScatterROI.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)

        self.roi_list.reindex_colormap()

    def create_roi_list(self):
        """Create empty ROI List"""
        self.roi_list = ROIList(self.ui, ScatterROI, self.vi)

    def set_spot_size(self, size: int):
        """Set the spot size for the scatter plot which illustrates the ROI"""
        for roi in self.roi_list:
            roi.get_roi_graphics_object().setSize(size)
            roi.spot_size = size


class ManagerVolROI(ManagerScatterROI):
    """Manager for 3D ROIs"""
    def __init__(self, parent, ui, viewer_interface: ViewerUtils):
        super(ManagerVolROI, self).__init__(parent, ui, viewer_interface)
        self.vi.viewer.sigZLevelChanged.connect(self.set_zlevel)

    def set_zlevel(self, z: int):
        """Set the current z-level to be visible in the viewer"""
        for roi in self.roi_list:
            roi.set_zlevel(z)

    def create_roi_list(self):
        """Create new empty ROI list"""
        self.roi_list = ROIList(self.ui, VolCNMF, self.vi)


class ManagerVolCNMF(ManagerVolROI):
    """Manager for 3D CNMF based ROIs"""
    def __init__(self, parent, ui, viewer_interface):
        super(ManagerVolCNMF, self).__init__(parent, ui, viewer_interface)
        self.roi_list = ROIList(self.ui, VolCNMF, self.vi)

        self.input_params_dict = None
        self.idx_components = None  # Keep track of components if the user manually want to remove some
        self.orig_idx_components = None  # List of components prior to any manual deletion by the user

        # cnmf data dict directly from the hdf5 file
        self.cnmf_data_dict = None

        # These correspond to the caiman.source_extraction.cnmf attributes
        self.cnmA = None
        self.cnmb = None
        self.cnmC = None
        self.cnm_f = None
        self.cnmYrA = None

    def create_roi_list(self):
        self.roi_list = ROIList(self.ui, VolCNMF, self.vi)

    def add_all_components(self, cnmf_data_dict: dict, input_params_dict: dict):
        """
        Add all components from a CNMF(E) output. Arguments correspond to CNMF(E) outputs

        :param cnmf_data_dict:      CNMF results data directly from the HDF5 file
        :param input_params_dict:   dict of input params, from the batch manager
        :param calc_raw_min_max:    Calculate raw min & max for each ROI
        :return:
        """
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        self.cnmf_data_dict = cnmf_data_dict

        # self.cnmf_obj = load_CNMF(self.cnmf_data_dict)

        self.cnmA = self.cnmf_data_dict['estimates']['A']
        self.cnmb = self.cnmf_data_dict['estimates']['b']
        self.cnm_f = self.cnmf_data_dict['estimates']['f']
        self.cnmC = self.cnmf_data_dict['estimates']['C']
        self.cnmYrA = self.cnmf_data_dict['estimates']['YrA']
        self.dims = self.cnmf_data_dict['dims']
        self.cnmS = self.cnmf_data_dict['estimates']['S']
        self.cnm_dfof = self.cnmf_data_dict['estimates']['F_dff']

        # components are already filtered from the output file
        self.idx_components = np.arange(self.cnmC.shape[0])
        self.orig_idx_components = deepcopy(self.idx_components)
        self.input_params_dict = input_params_dict

        # spatial components
        contours = caiman_get_contours(self.cnmA[:, self.idx_components], self.dims, thr=0.9)

        temporal_components = self.cnmC

        self.input_params_dict = self.input_params_dict
        num_components = len(temporal_components)

        self.ui.radioButton_curve_data.setChecked(True)

        for ix in range(num_components):
            self.vi.viewer.status_bar_label.showMessage('Please wait, adding component #: '
                                                        + str(ix) + ' / ' + str(num_components))

            curve_data = temporal_components[ix]
            contour = contours[ix]

            roi = VolCNMF(curve_plot_item=self.get_plot_item(),
                          view_box=self.vi.viewer.getView(),
                          cnmf_idx=self.idx_components[ix],
                          curve_data=curve_data,
                          contour=contour,
                          dfof_data=self.cnm_dfof[ix] if (self.cnm_dfof is not None) else None,
                          spike_data=self.cnmS[ix])

            self.roi_list.append(roi)

        self.roi_list.reindex_colormap()
        self.vi.viewer.status_bar_label.showMessage('Finished adding all components!')

    def add_roi(self):
        """Not implemented, uses add_all_components to import all ROIs instead"""
        raise NotImplementedError('Not implemented for CNMFE ROIs')

    def restore_from_states(self, states: dict):
        """Restore from states, such as when these ROIs are saved with a Project Sample"""
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        self.cnmf_data_dict = states['cnmf_data_dict']

        for state in states['states']:
            roi = VolCNMF.from_state(self.get_plot_item(), self.vi.viewer.getView(), state)
            self.roi_list.append(roi)
        self.input_params_dict = states['input_params_cnmfe']
        self.cnmA = states['cnmf_output']['cnmA']
        self.cnmb = states['cnmf_output']['cnmb']
        self.cnmC = states['cnmf_output']['cnmC']
        self.cnm_f = states['cnmf_output']['cnm_f']
        self.cnmS = self.cnmf_data_dict['estimates']['S']
        self.cnm_dfof = self.cnmf_data_dict['estimates']['F_dff']
        self.cnmYrA = states['cnmf_output']['cnmYrA']
        self.idx_components = states['cnmf_output']['idx_components']
        self.orig_idx_components = states['cnmf_output']['orig_idx_components']
        self.roi_list.reindex_colormap()

    def get_all_states(self) -> dict:
        """Get all states so that they can be restored"""
        states = super(ManagerVolROI, self).get_all_states()

        # If the user has manually deleted some ROIs
        new_idx_components = np.array([roi.cnmf_idx for roi in self.roi_list], dtype=np.int64)

        # Make sure nothing weird happened
        # l = [self.cnmA, self.cnmb, self.cnmC, self.cnm_f, self.cnmYrA, self.orig_idx_components, new_idx_components]
        # if any(item is None for item in l):
        #     raise ValueError('One or more pieces of CNMF(E) data are missing')

        # Store the actual cnmf attributes as well.
        input_dict = {'input_params_cnmfe': self.input_params_dict,
                      'cnmf_data_dict':     self.cnmf_data_dict,
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
        """Update idx_components if the user manually delete an ROI"""
        roi = self.roi_list[self.roi_list.current_index]
        self.idx_components = np.delete(self.idx_components, np.where(self.idx_components == roi.cnmf_idx)[0])

    def set_spot_size(self, size: int):
        for roi in self.roi_list:
            roi.get_roi_graphics_object().setSize(size)
            roi.spot_size = size


class ManagerCNMFROI(AbstractBaseManager):
    """Manager for ROIs imported from CNMF or CNMFE outputs"""
    def __init__(self, parent, ui, viewer_interface):
        """Instantiate necessary attributes"""
        super(ManagerCNMFROI, self).__init__(parent, ui, viewer_interface)

        self.create_roi_list()
        self.list_widget = self.roi_list.list_widget
        self.input_params_dict = None
        self.idx_components = None  # Keep track of components if the user manually want to remove some
        self.orig_idx_components = None  # List of components prior to any manual deletion by the user

        # cnmf data dict directly from the hdf5 file
        self.cnmf_data_dict = None

        # These correspond to the caiman.source_extraction.cnmf attributes
        self.cnmA = None
        self.cnmb = None
        self.cnmC = None
        self.cnm_f = None
        self.cnmYrA = None

        self.raw_normalization_choices = ['top_5', 'top_10', 'top_5p', 'top_10p', 'top_25p']

    def create_roi_list(self):
        """Create empty CNMFROI list"""
        self.roi_list = ROIList(self.ui, CNMFROI, self.vi)

    def add_all_components(self, cnmf_data_dict, input_params_dict, calc_raw_min_max=False):
        """
        Add all components from a CNMF(E) output. Arguments correspond to CNMF(E) outputs

        :param cnmf_data_dict:      CNMF results data directly from the HDF5 file
        :param input_params_dict:   dict of input params, from the batch manager
        :param calc_raw_min_max:    Calculate raw min & max for each ROI
        :return:
        """
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        self.cnmf_data_dict = cnmf_data_dict

        self.cnmA = self.cnmf_data_dict['estimates']['A']
        self.cnmb = self.cnmf_data_dict['estimates']['b']
        self.cnm_f = self.cnmf_data_dict['estimates']['f']
        self.cnmC = self.cnmf_data_dict['estimates']['C']
        self.cnmS = self.cnmf_data_dict['estimates']['S']
        self.cnm_dfof = self.cnmf_data_dict['estimates']['F_dff']
        self.cnmYrA = self.cnmf_data_dict['estimates']['YrA']
        self.dims = self.cnmf_data_dict['dims']
        self.idx_components = cnmf_data_dict['estimates']['idx_components']

        if self.idx_components is None:
            self.idx_components = np.arange(self.cnmC.shape[0])

        self.orig_idx_components = deepcopy(self.idx_components)
        self.input_params_dict = input_params_dict

        # spatial components
        contours = caiman_get_contours(self.cnmA[:, self.idx_components], self.dims)
        # if dfof:
        #     temporal_components = cnmC
        # else:
        #     temporal_components = cnmC[idx_components]
        self.input_params_dict = self.input_params_dict
        num_components = len(self.cnmC)

        if calc_raw_min_max:
            img = self.vi.viewer.workEnv.imgdata.seq.T

        self.ui.radioButton_curve_data.setChecked(True)

        for ix in range(num_components):
            self.vi.viewer.status_bar_label.showMessage('Please wait, adding component #: '
                                                        + str(ix) + ' / ' + str(num_components))

            curve_data = self.cnmC[ix]
            contour = contours[ix]

            if calc_raw_min_max:
                # Get a binary mask
                mask = self.cnmA[:, self.idx_components[ix]].toarray().reshape(self.dims, order='F') > 0
                # mask3d = np.array((mask,) * curve_data.shape[0])

                max_ix = curve_data.argmax()
                min_ix = curve_data.argmin()

                array_at_max = img[max_ix, :, :].copy()
                array_at_max = array_at_max[mask]

                array_at_min = img[min_ix, :, :].copy()
                array_at_min = array_at_min[mask]

                raw_min_max = self.get_raw_min_max(array_at_max=array_at_max,
                                                   array_at_min=array_at_min)

            else:
                raw_min_max = None

            roi = CNMFROI(curve_plot_item=self.get_plot_item(),
                          view_box=self.vi.viewer.getView(),
                          cnmf_idx=self.idx_components[ix],
                          curve_data=curve_data,
                          contour=contour,
                          raw_min_max=raw_min_max,
                          dfof_data=self.cnm_dfof[ix] if (self.cnm_dfof is not None) else None,
                          spike_data=self.cnmS[ix])

            self.roi_list.append(roi)

        if calc_raw_min_max:
            del img

        self.roi_list.reindex_colormap()
        self.vi.viewer.status_bar_label.showMessage('Finished adding all components!')

    def get_raw_min_max(self, array_at_max, array_at_min):
        a_size = array_at_max.size
        p5 = int(a_size * 0.05)
        p10 = p5 * 2
        p25 = p5 * 5

        out = {}

        for a, r in zip((array_at_max, array_at_min), ('raw_max', 'raw_min')):
            out[r] = {'top_5': self.get_raw_mean(a, min(5, a_size)),
                      'top_10': self.get_raw_mean(a, min(10, a_size)),
                      'top_5p': self.get_raw_mean(a, p5),
                      'top_10p': self.get_raw_mean(a, p10),
                      'top_25p': self.get_raw_mean(a, p25),
                      'full_mean': a.mean()
                      }
        return out

    def get_raw_mean(self, array, num_items):
        return np.partition(array, -num_items)[-num_items:].mean()

    def add_roi(self):
        """Not implemented, uses add_all_components to import all ROIs instead"""
        raise NotImplementedError('Not implemented for CNMFE ROIs')

    def restore_from_states(self, states: dict):
        """Restore from states, such as when these ROIs are saved with a Project Sample"""
        super(ManagerCNMFROI, self).restore_from_states(states)
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()

        if 'cnmf_data_dict' in states.keys():
            self.cnmf_data_dict = states['cnmf_data_dict']
        else:
            self.cnmf_data_dict = None

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
        """Get all states so that they can be restored"""
        if not hasattr(self, 'roi_list'):
            self.create_roi_list()
        states = super(ManagerCNMFROI, self).get_all_states()

        # If the user has manually deleted some ROIs
        new_idx_components = np.array([roi.cnmf_idx for roi in self.roi_list], dtype=np.int64)

        # Store the actual cnmf attributes as well.
        input_dict = {'input_params_cnmfe': self.input_params_dict,
                      'cnmf_data_dict': self.cnmf_data_dict,
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
        """Update idx_components if the user manually delete an ROI"""
        roi = self.roi_list[self.roi_list.current_index]
        self.idx_components = np.delete(self.idx_components, np.where(self.idx_components == roi.cnmf_idx)[0])

    def set_spot_size(self, size: int):
        for roi in self.roi_list:
            roi.get_roi_graphics_object().setSize(size)
            roi.spot_size = size
