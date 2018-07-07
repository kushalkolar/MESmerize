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
from .pytemplates.cnmf_pytemplate import *
import json
from common import configuration


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCNMF.clicked.connect(self.add_to_batch_cnmf)

        self.ui.btnExport.clicked.connect(self.export_params)
        self.ui.btnImport.clicked.connect(self.import_params)

        # assert isinstance(self.vi.viewer_ref.batch_manager, BatchModuleGui)

    def _make_params_dict(self):
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            QtWidgets.QMessageBox.warning(self, 'No framerate for current image sequence!',
                                          'You must set a framerate for the current image sequence before you can '
                                          'continue!', QtWidgets.QMessageBox.Ok)
            return None

        d = {'Input':           self.ui.comboBoxInput.currentText(),
             'fr':              self.vi.viewer.workEnv.imgdata.meta['fps'],
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
             'frames_window':   self.ui.spinBoxFramesWindow.value(),
             'quantileMin':     self.ui.spinBoxQuantileMin.value()
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
        pass
        # path = QtWidgets.QFileDialog.getOpenFileName(self, 'Import Parameters', '', '(*.json)')
        # if path == '':
        #     return
        # try:
        #     with open(path, 'r') as f:
        #         d = json.load(f)
        #         self.ui.spinBoxGSig.setValue(d['gSig'])
        #         self.ui.doubleSpinBoxMinCorr.setValue(d['min_corr'])
        #         self.ui.spinBoxMinPNR.setValue(d['min_pnr'])
        #         self.ui.doubleSpinBoxRValuesMin.setValue(d['r_values_min'])
        #         self.ui.spinBoxDecayTime.setValue(d['decay_time'])
        # except IOError as e:
        #     QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
        #     return
        # except KeyError as e:
        #     QtWidgets.QMessageBox.warning(self, 'Invalid params file!',
        #                                   'The chosen file is not a valid CNMF-E params file.\n' + str(e))

    def add_to_batch_cnmf(self):
        input_workEnv = self.vi.viewer.workEnv

        d = self._make_params_dict()

        if d is None:
            return

        name = self.ui.lineEdName.text()
        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CNMF: ' + name + ' to batch...')

        batch_manager = configuration.window_manager.get_batch_manager()
        batch_manager.add_item(module='CNMF',
                               viewer_reference=self.vi.viewer,
                               name=name,
                               input_workEnv=input_workEnv,
                               input_params=d,
                               info=d
                               )
        self.vi.viewer.status_bar_label.showMessage('Done adding CNMF: ' + name + ' to batch!')

    @QtCore.pyqtSlot()
    def update_available_inputs(self):
        print('Input changes received in cnmfe module!')
