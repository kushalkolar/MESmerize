#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 23 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.cnmfe_pytemplate import *
import json
import numpy as np
from .batch_manager import ModuleGUI as BatchModuleGui
from MesmerizeCore import configuration
import caiman as cm


class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCorrPNR.clicked.connect(self.add_to_batch_corr_pnr)
        self.ui.btnAddToBatchCNMFE.clicked.connect(self.add_to_batch_cnmfe)

        self.ui.btnExport.clicked.connect(self.export_params)
        self.ui.btnImport.clicked.connect(self.import_params)

        self.ui.comboBoxInputCorrPNR.currentIndexChanged.connect(self.combobox_input_corr_pnr_changed)
        self.ui.comboBoxCNMFE.currentIndexChanged.connect(self.combobox_input_cnmfe_changed)

        self.viewer_ref.batch_manager.listwchanged.connect(self.update_available_inputs)

    def _make_params_dict(self):
        d = {'Input_Corr_PNR':  self.ui.comboBoxInputCorrPNR.currentText(),
             'gSig':            self.ui.spinBoxGSig.value(),
             'gSize':           self.ui.spinBoxGSize.value(),
             'Input_CNMFE':     self.ui.comboBoxCNMFE.currentText(),
             'min_corr':        self.ui.doubleSpinBoxMinCorr.value(),
             'min_pnr':         self.ui.spinBoxMinPNR.value(),
             'min_SNR':         self.ui.spinBoxMinSNR.value(),
             'r_values_min':    self.ui.doubleSpinBoxRValuesMin.value(),
             'decay_time':      self.ui.spinBoxDecayTime.value()
             }

        return d

    def export_params(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Parameters', '', '(*.json)')

        if path == '':
            return
        if path[0].endswith('.json'):
            path = path[0]
        else:
            path = path[0] + '.json'

        with open(path, 'w') as f:
            d = self._make_params_dict()
            json.dump(d, f)

    def import_params(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Import Parameters', '', '(*.json)')
        if path == '':
            return
        try:
            with open(path, 'r') as f:
                d = json.load(f)
                self.ui.spinBoxGSig.setValue(d['gSig'])
                self.ui.spinBoxGSize.setValue(d['gSize'])
                self.ui.doubleSpinBoxMinCorr.setValue(d['min_corr'])
                self.ui.spinBoxMinPNR.setValue(d['min_pnr'])
                self.ui.doubleSpinBoxRValuesMin.setValue(d['r_values_min'])
                self.ui.spinBoxDecayTime.setValue(d['decay_time'])
        except IOError as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return
        except KeyError as e:
            QtWidgets.QMessageBox.warning(self, 'Invalid params file!',
                                          'The chosen file is not a valid CNMF-E params file.\n' + str(e))

    def add_to_batch_corr_pnr(self):
        if self.ui.comboBoxInputCorrPNR.currentText() == 'Current Work Environment':
            pass
        else:
            pass

        d = np.array(self._make_params_dict(), dtype=object)
        name = self.ui.lineEdName.text()
        assert isinstance(self.viewer_ref.batch_manager, BatchModuleGui)



        self.viewer_ref.batch_manager.add_item(module='CNMFE', name=name, input_imgseq=

    def add_to_batch_cnmfe(self):
        if self.ui.comboBoxInputCorrPNR.currentText() == 'Continue from above':
            pass
        else:
            pass

        if self.viewer_ref.workEnv.

    def save_memmap(self):
        fname_new = cm.save_memmap_each(
            filename_reorder,
            base_name='memmap_',
            order='C',
            border_to_0=bord_px,
            dview=self.dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_', dview=self.dview)

    def reset_dview(self):
        try:
            self.dview.terminate()
        except:
            c, self.dview, self.n_processes = cm.cluster.setup_cluster(backend='multiprocessing', n_processes=4,
                                                     # number of process to use, if you go out of memory try to reduce this one
                                                     single_thread=False)

    def update_available_inputs(self):
        pass

    # def combobox_input_corr_pnr_changed(self):
    #     if self.ui.comboBoxInputCorrPNR.currentText() == 'Current Work Environment':
    #         self.enable_radio_buttons_corr_pnr(True)
    #     else:
    #         self.enable_radio_buttons_corr_pnr(False)
    #
    # def combobox_input_cnmfe_changed(self):
    #     if self.ui.comboBoxCNMFE.currentText() == 'Current Work Environment':
    #         self.enable_radio_buttons_cnmfe(True)
    #     else:
    #         self.enable_radio_buttons_cnmfe(False)
    #
    # def enable_radio_buttons_corr_pnr(self, b):
    #     self.ui.radioButtonInputWriteCorrPNRNow.setEnabled(b)
    #     self.ui.radioButtonInputWriteCorrPNRRuntime.setEnabled(b)
    #
    # def enable_radio_buttons_cnmfe(self, b):
    #     self.ui.radioButtonCNMFEInputWriteNow.setEnabled(b)
    #     self.ui.radioButtonCNMFEInputWriteRuntime.setEnabled(b)