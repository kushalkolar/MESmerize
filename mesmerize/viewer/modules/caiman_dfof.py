#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
from ..core.common import ViewerUtils
from ...common.qdialogs import *
from ...common.configuration import get_sys_config
from qtap import Function
from caiman.source_extraction.cnmf.cnmf import CNMF, Estimates, CNMFParams
from .roi_manager_modules.managers import ManagerCNMFROI, ManagerVolCNMF
import numpy as np

# just need the function signature
def detrend_df_f(quantileMin: float = 8,
                 frames_window: int = 500,
                 flag_auto: bool = True,
                 use_fast: bool = False,
                 use_residuals: bool = True,
                 detrend_only: bool = False):
    pass


# adapted from caiman code for reloading CNMF obj from hdf5 file
def get_CNMF_obj(d: dict) -> CNMF:
    new_obj = CNMF(get_sys_config()['_MESMERIZE_N_THREADS'])
    for key, val in d.items():
        if key == 'params':
            prms = CNMFParams()
            for subdict in val.keys():
                prms.set(subdict, val[subdict])
            setattr(new_obj, key, prms)
        elif key == 'estimates':
            estims = Estimates()
            for kk, vv in val.items():
                if kk == 'discarded_components':
                    if vv is not None:
                        discarded_components = Estimates()
                        for kk__, vv__ in vv.items():
                            setattr(discarded_components, kk__, vv__)
                        setattr(estims, kk, discarded_components)
                else:
                    setattr(estims, kk, vv)

            setattr(new_obj, key, estims)
        else:
            setattr(new_obj, key, val)

    return new_obj


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        QtWidgets.QDockWidget.__init__(self, parent)
        self.setFloating(True)
        self.setWindowTitle('Caiman detrend ΔF/F')

        self.vi = ViewerUtils(viewer_reference)

        opts = \
            {
                'quantileMin':
                    {
                        'minmax': (0, 100)
                    },
                'frames_window':
                    {
                        'minmax': (0, 1000),
                        'step': 10
                    }
            }

        self.function = Function(detrend_df_f, opts, parent=self)
        self.function.sig_set_clicked.connect(self.set_data)

        self.setWidget(self.function.widget)

    @present_exceptions()
    def set_data(self, kwargs: dict):
        if not isinstance(
                self.vi.viewer.workEnv.roi_manager,
                (ManagerCNMFROI, ManagerVolCNMF)
        ):
            raise TypeError("This module is only for CNMF ROIs")

        roi_manager: (ManagerCNMFROI, ManagerCNMFROI) = \
            self.vi.viewer.workEnv.roi_manager

        if not (roi_manager.idx_components == roi_manager.orig_idx_components).all():
            raise ValueError("You cannot use this module if you have deleted ROIs."
                             "If you want to delete some ROIs, first use this "
                             "module and then delete the ROIs.")

        self.vi.set_statusbar('Doing caiman detrend_df_f, please wait...')

        self.cnmf = get_CNMF_obj(roi_manager.cnmf_data_dict)
        self.cnmf.estimates.detrend_df_f(**kwargs)

        roi_manager.cnm_dfof = self.cnmf.estimates.F_dff

        for roi, dfof in zip(
                roi_manager.roi_list,
                roi_manager.cnm_dfof
        ):
            xs = np.arange(len(dfof))
            roi.dfof_data = [xs, dfof]

        history = self.vi.work_env.history_trace

        try:
            next(
                d for ix, d in enumerate(history) if 'caiman_detrend_df_f' in d
            )['caiman_detrend_df_f'] = kwargs
        except StopIteration:
            self.vi.work_env.history_trace.append({'caiman_detrend_df_f': kwargs})

        self.vi.set_statusbar('Finished caiman detrend_df_f!')

        self.vi.viewer.parent().get_module('roi_manager').ui.radioButton_dfof.click()
