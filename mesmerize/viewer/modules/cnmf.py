#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerUtils
from .pytemplates.cnmf_pytemplate import *
import json
from ...common import get_window_manager
from ...common.qdialogs import *


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCNMF.clicked.connect(self.add_to_batch_cnmf)

        self.ui.btnExport.clicked.connect(self.export_params)
        self.ui.btnImport.clicked.connect(self.import_params)

        # assert isinstance(self.vi.viewer_ref.batch_manager, BatchModuleGui)

    @present_exceptions()
    def get_params(self, *args, **kwargs) -> dict:
        """
        Get a dict of the set parameters.
        If the work environment was loaded from a motion correction batch item it put the bord_px in the dict.
        Doesn't use any arguments

        :return: parameters dict
        :rtype: dict
        """
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            raise KeyError('No framerate for current image sequence!',
                           'You must set a framerate for the current image sequence. '
                           'You can set it manually in the console like this:\nget_meta()["fps"] = <framerate>')

        history_trace = self.vi.viewer.workEnv.history_trace
        try:
            bord_px = next(d for ix, d in enumerate(history_trace) if 'caiman_motion_correction' in d)['caiman_motion_correction']['bord_px']
        except StopIteration:
            bord_px = 0

        d = {'Input':           self.ui.comboBoxInput.currentText(),
             'p':               self.ui.spinBoxP.value(),
             'gnb':             self.ui.spinBoxGnb.value(),
             'merge_thresh':    self.ui.doubleSpinBoxMergeThresh.value(),
             'rf':              self.ui.spinBoxRf.value(),
             'stride_cnmf':     self.ui.spinBoxStrideCNMF.value(),
             'k':               self.ui.spinBoxK.value(),
             'gSig':            self.ui.spinBoxGSig.value(),
             'min_SNR':         self.ui.doubleSpinBoxMinSNR.value(),
             'rval_thr':        self.ui.doubleSpinBoxRvalThr.value(),
             'cnn_thr':         self.ui.doubleSpinBoxCNNThr.value(),
             'decay_time':      self.ui.spinBoxDecayTime.value(),
             'name_cnmf':       self.ui.lineEdName.text(),
             'refit':           self.ui.checkBoxRefit.isChecked()
             }

        # Non UI params
        d = {'fr': self.vi.viewer.workEnv.imgdata.meta['fps'],
             'bord_px': bord_px,
             **d}

        return d

    def set_params(self, d: dict):
        """
        Set all parameters from a dict. All keys must be present in the dict.

        :param d: parameters dict
        """
        self.ui.spinBoxP.setValue(d['p'])
        self.ui.spinBoxGnb.setValue(d['gnb'])
        self.ui.doubleSpinBoxMergeThresh.setValue(d['merge_thresh'])
        self.ui.spinBoxRf.setValue(d['rf'])
        self.ui.spinBoxStrideCNMF.setValue(d['stride_cnmf'])
        self.ui.spinBoxK.setValue(d['k'])
        self.ui.spinBoxGSig.setValue(d['gSig'])
        self.ui.doubleSpinBoxMinSNR.setValue(d['min_SNR'])
        self.ui.doubleSpinBoxRvalThr.setValue(d['rval_thr'])
        self.ui.doubleSpinBoxCNNThr.setValue(d['cnn_thr'])
        self.ui.spinBoxDecayTime.setValue(d['decay_time'])
        self.ui.lineEdName.setText(d['name_cnmf'])
        self.ui.checkBoxRefit.setChecked(d['refit'])

    @use_save_file_dialog('Save params file as', None, '.json')
    def export_params(self, path, args, **kwargs):
        with open(path, 'w') as f:
            d = self.get_params()
            json.dump(d, f)

    @use_open_file_dialog('Choose params file', None, ['*.json'])
    @present_exceptions('Cannot import parameters', 'Make sure it is a CNMF parameters file')
    def import_params(self, path, *args, **kwargs):
        with open(path, 'r') as f:
            d = json.load(f)
            self.set_params(d)

    def add_to_batch_cnmf(self):
        """
        Add a CNMF batch item with the currently set parameters and the current work environment.
        """
        input_workEnv = self.vi.viewer.workEnv

        d = self.get_params()

        name = self.ui.lineEdName.text()
        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CNMF: ' + name + ' to batch...')

        batch_manager = get_window_manager().get_batch_manager()
        batch_manager.add_item(module='CNMF',
                               name=name,
                               input_workEnv=input_workEnv,
                               input_params=d,
                               info=d
                               )
        self.vi.viewer.status_bar_label.showMessage('Done adding CNMF: ' + name + ' to batch!')
        self.ui.lineEdName.clear()
