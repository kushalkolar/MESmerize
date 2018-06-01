#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 23 2018

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
from MesmerizeCore.packager import viewerWorkEnv


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

        assert isinstance(self.viewer_ref.batch_manager, BatchModuleGui)
        self.viewer_ref.batch_manager.listwchanged.connect(self.update_available_inputs)

    def _make_params_dict(self):
        if 'fps' not in self.viewer_ref.workEnv.imgdata.meta.keys():
            QtWidgets.QMessageBox.warning(self, 'No framerate for current image sequence!',
                                          'You must set a framerate for the current image sequence before you can '
                                          'continue!', QtWidgets.QMessageBox.Ok)
            return None

        d = {'Input_Corr_PNR':  self.ui.comboBoxInputCorrPNR.currentText(),
             'frate':           self.viewer_ref.workEnv.imgdata.meta['fps'],
             'gSig':            self.ui.spinBoxGSig.value(),
             'Input_CNMFE':     self.ui.comboBoxInput.currentText(),
             'min_corr':        self.ui.doubleSpinBoxMinCorr.value(),
             'min_pnr':         self.ui.spinBoxMinPNR.value(),
             'min_SNR':         self.ui.spinBoxMinSNR.value(),
             'r_values_min':    self.ui.doubleSpinBoxRValuesMin.value(),
             'decay_time':      self.ui.spinBoxDecayTime.value(),
             'rf':              self.ui.spinBoxRf.value(),
             'stride':          self.ui.spinBoxOverlap.value(),
             'gnb':             self.ui.spinBoxGnb.value(),
             'nb_patch':        self.ui.spinBoxNb_patch.value(),
             'k':               self.ui.spinBoxK.value()
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
        if self.ui.comboBoxInput.currentText() == 'Current Work Environment':
            if self.viewer_ref.workEnv.isEmpty:
                QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                              'nothing to add to batch')
                return
            input_workEnv = self.viewer_ref.workEnv
        else:
            input_workEnv = self.ui.comboBoxInput.currentText()

        d = self._make_params_dict()

        if d is None:
            return

        d['do_corr_pnr'] = True
        d['do_cnmfe'] = False

        self.viewer_ref.batch_manager.add_item(module='CNMFE',
                                               name=self.ui.lineEdCorrPNRName.text(),
                                               input_workEnv=input_workEnv,
                                               input_params=d,
                                               meta=d
                                               )

    def add_to_batch_cnmfe(self):
        if self.ui.comboBoxInput.currentText() == 'Current Work Environment':
            if self.viewer_ref.workEnv.isEmpty:
                QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                              'nothing to add to batch')
                return
            input_workEnv = self.viewer_ref.workEnv
        else:
            input_workEnv = self.ui.comboBoxInput.currentText()

        d = self._make_params_dict()

        if d is None:
            return

        d['do_corr_pnr'] = False
        d['do_cnmfe'] = True

        # d = np.array(self._make_params_dict(), dtype=object)

        self.viewer_ref.batch_manager.add_item(module='CNMFE',
                                               name=self.ui.lineEdName.text(),
                                               input_workEnv=input_workEnv,
                                               input_params=d,
                                               meta=d
                                               )

    def save_memmap(self):
        pass

    @QtCore.pyqtSlot()
    def update_available_inputs(self):
        print('Input changes received in cnmfe module!')
