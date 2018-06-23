#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerInterface
from ..core.viewer_work_environment import ViewerWorkEnv
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.cnmfe_pytemplate import *
import json
import numpy as np
from .batch_manager import ModuleGUI as BatchModuleGui
from common import configuration


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)
        if configuration.window_manager.batch_manager is None:
            QtWidgets.QMessageBox.question(self, 'No batch manager open',
                                           'The batch manager has not been initialized, '
                                           'you must choose a location for a new batch or create a new batch',
                                           QtWidgets.QMessageBox.Ok)
            configuration.window_manager.initialize_batch_manager()

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCorrPNR.clicked.connect(self.add_to_batch_corr_pnr)
        self.ui.btnAddToBatchCNMFE.clicked.connect(self.add_to_batch_cnmfe)

        self.ui.btnExport.clicked.connect(self.export_params)
        self.ui.btnImport.clicked.connect(self.import_params)

        # assert isinstance(self.vi.viewer_ref.batch_manager, BatchModuleGui)
        self.vi.viewer.batch_manager.listwchanged.connect(self.update_available_inputs)

    def _make_params_dict(self):
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            QtWidgets.QMessageBox.warning(self, 'No framerate for current image sequence!',
                                          'You must set a framerate for the current image sequence before you can '
                                          'continue!', QtWidgets.QMessageBox.Ok)
            return None

        d = {'Input': self.ui.comboBoxInput.currentText(),
             'frate': self.vi.viewer.workEnv.imgdata.meta['fps'],
             'gSig': self.ui.spinBoxGSig.value(),
             'min_corr': self.ui.doubleSpinBoxMinCorr.value(),
             'min_pnr': self.ui.spinBoxMinPNR.value(),
             'min_SNR': self.ui.spinBoxMinSNR.value(),
             'r_values_min': self.ui.doubleSpinBoxRValuesMin.value(),
             'decay_time': self.ui.spinBoxDecayTime.value(),
             'rf': self.ui.spinBoxRf.value(),
             'stride': self.ui.spinBoxOverlap.value(),
             'gnb': self.ui.spinBoxGnb.value(),
             'nb_patch': self.ui.spinBoxNb_patch.value(),
             'k': self.ui.spinBoxK.value()
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
            if self.vi.viewer.workEnv.isEmpty:
                QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                              'nothing to add to batch')
                return
            input_workEnv = self.vi.viewer.workEnv
        else:
            input_workEnv = self.ui.comboBoxInput.currentText()

        d = self._make_params_dict()

        if d is None:
            return

        d['do_corr_pnr'] = True
        d['do_cnmfe'] = False

        self.vi.viewer.batch_manager.add_item(module='CNMFE',
                                                  name=self.ui.lineEdCorrPNRName.text(),
                                                  input_workEnv=input_workEnv,
                                                  input_params=d,
                                                  info=d
                                                  )

    def add_to_batch_cnmfe(self):
        if self.ui.comboBoxInput.currentText() == 'Current Work Environment':
            if self.vi.viewer.workEnv.isEmpty:
                QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                              'nothing to add to batch')
                return
            input_workEnv = self.vi.viewer.workEnv
        else:
            input_workEnv = self.ui.comboBoxInput.currentText()

        d = self._make_params_dict()

        if d is None:
            return

        d['do_corr_pnr'] = False
        d['do_cnmfe'] = True

        # d = np.array(self._make_params_dict(), dtype=object)

        self.vi.viewer.batch_manager.add_item(module='CNMFE',
                                                  name=self.ui.lineEdName.text(),
                                                  input_workEnv=input_workEnv,
                                                  input_params=d,
                                                  info=d
                                                  )

    def save_memmap(self):
        pass

    @QtCore.pyqtSlot()
    def update_available_inputs(self):
        print('Input changes received in cnmfe module!')
