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
from .pytemplates.cnmfe_pytemplate import *
import json
from ...common import get_window_manager


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCorrPNR.clicked.connect(self.add_to_batch_corr_pnr)
        self.ui.btnAddToBatchCNMFE.clicked.connect(self.add_to_batch_cnmfe)

        self.ui.btnExport.clicked.connect(self.export_params)
        self.ui.btnImport.clicked.connect(self.import_params)

        # assert isinstance(self.vi.viewer_ref.batch_manager, BatchModuleGui)

    def _make_params_dict(self) -> dict:
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            QtWidgets.QMessageBox.warning(self, 'No framerate for current image sequence!',
                                          'You must set a framerate for the current image sequence before you can '
                                          'continue!', QtWidgets.QMessageBox.Ok)
            return None

        # Get bord_px param if motion correction was performed
        history_trace = self.vi.viewer.workEnv.history_trace
        try:
            bord_px = next(d for ix, d in enumerate(history_trace) if 'caiman_motion_correction' in d)['caiman_motion_correction']['bord_px']
        except StopIteration:
            bord_px = 0

        d = {'Input':           self.ui.comboBoxInput.currentText(),
             'frate':           self.vi.viewer.workEnv.imgdata.meta['fps'],
             'gSig':            self.ui.spinBoxGSig.value(),
             'bord_px':         bord_px,
             'min_corr':        self.ui.doubleSpinBoxMinCorr.value(),
             'min_pnr':         self.ui.spinBoxMinPNR.value(),
             'min_SNR':         self.ui.spinBoxMinSNR.value(),
             'r_values_min':    self.ui.doubleSpinBoxRValuesMin.value(),
             'decay_time':      self.ui.spinBoxDecayTime.value(),
             'rf':              self.ui.spinBoxRf.value(),
             'stride':          self.ui.spinBoxOverlap.value(),
             'gnb':             self.ui.spinBoxGnb.value(),
             'nb_patch':        self.ui.spinBoxNb_patch.value(),
             'k':               self.ui.spinBoxK.value(),
             'name_corr_pnr':   self.ui.lineEdCorrPNRName.text(),
             'name_cnmfe':      self.ui.lineEdName.text()
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
                self.set_params(d)
        except IOError as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return
        except KeyError as e:
            QtWidgets.QMessageBox.warning(self, 'Invalid params file!',
                                          'The chosen file is not a valid CNMF-E params file.\n' + str(e))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Import error', str(e))

    def set_params(self, params: dict):
        self.ui.comboBoxInput.setCurrentText(params['Input'])
        self.ui.spinBoxGSig.setValue(params['gSig'])
        self.ui.doubleSpinBoxMinCorr.setValue(params['min_corr'])
        self.ui.spinBoxMinPNR.setValue(params['min_pnr'])
        self.ui.spinBoxMinSNR.setValue(params['min_SNR'])
        self.ui.doubleSpinBoxRValuesMin.setValue(params['r_values_min'])
        self.ui.spinBoxDecayTime.setValue(params['decay_time'])
        self.ui.spinBoxRf.setValue(params['rf'])
        self.ui.spinBoxOverlap.setValue(params['stride'])
        self.ui.spinBoxGnb.setValue(params['gnb'])
        self.ui.spinBoxNb_patch.setValue(params['nb_patch'])
        self.ui.spinBoxK.setValue(params['k'])
        self.ui.lineEdCorrPNRName.setText(params['name_corr_pnr'])
        self.ui.lineEdName.setText(params['name_cnmfe'])

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

        batch_manager = get_window_manager().get_batch_manager()
        name = self.ui.lineEdCorrPNRName.text()

        self.vi.viewer.status_bar_label.showMessage('Please wait, adding Corr PNR: ' + name + ' to batch...')

        batch_manager.add_item(module='CNMFE',
                               viewer_reference=self.vi.viewer,
                               name=name,
                               input_workEnv=input_workEnv,
                               input_params=d,
                               info=d
                               )

        self.vi.viewer.status_bar_label.showMessage('Done adding Corr PNR: ' + name + ' to batch!')

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

        name = self.ui.lineEdName.text()
        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CNMFE: ' + name + ' to batch...')

        batch_manager = get_window_manager().get_batch_manager()
        batch_manager.add_item(module='CNMFE',
                               viewer_reference=self.vi.viewer,
                               name=name,
                               input_workEnv=input_workEnv,
                               input_params=d,
                               info=d
                               )
        self.vi.viewer.status_bar_label.showMessage('Done adding CNMFE: ' + name + ' to batch!')

    @QtCore.pyqtSlot()
    def update_available_inputs(self):
        pass
