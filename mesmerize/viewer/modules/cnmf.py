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
from ...common import get_window_manager
from ...common.qdialogs import *
from ...common.utils import HdfTools
from uuid import UUID
from shutil import copy
import os
from copy import deepcopy


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCNMF.clicked.connect(lambda: self.add_to_batch())

    @present_exceptions()
    def get_params(self, *args, group_params: bool = False) -> dict:
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

        # Get width of border that is NaN, usually happens due ot motion correction
        history_trace = self.vi.viewer.workEnv.history_trace
        try:
            bord_px = next(d for ix, d in enumerate(history_trace) if 'caiman_motion_correction' in d)['caiman_motion_correction']['bord_px']
        except StopIteration:
            bord_px = 0

        rf = self.ui.spinBoxRf.value()

        # CNMF kwargs
        cnmf_kwargs = \
            {
                'p': self.ui.spinBoxP.value(),
                'nb': self.ui.spinBoxnb.value(),
                'merge_thresh': self.ui.doubleSpinBoxMergeThresh.value(),
                'rf': rf if not self.ui.checkBoxRfNone.isChecked() else None,
                'stride': self.ui.spinBoxStrideCNMF.value(),
                'K': self.ui.spinBoxK.value(),
                'gSig': [
                            self.ui.spinBox_gSig_x.value(),
                            self.ui.spinBox_gSig_y.value()
                        ],
                'ssub': self.ui.spinBox_ssub.value(),
                'tsub': self.ui.spinBox_tsub.value(),
                'method_init': self.ui.comboBox_method_init.currentText(),
                'border_pix': bord_px,
            }

        # Any additional cnmf kwargs set in the text entry
        if self.ui.groupBox_cnmf_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_cnmf_kwargs.toPlainText()
                cnmf_kwargs_add = eval(f"dict({_kwargs})")
                cnmf_kwargs.update(cnmf_kwargs_add)
            except:
                raise ValueError("CNMF kwargs not formatted properly.")

        # Component evaluation kwargs
        eval_kwargs = \
            {
                'min_SNR': self.ui.doubleSpinBoxMinSNR.value(),
                'rval_thr': self.ui.doubleSpinBoxRvalThr.value(),
                'use_cnn': self.ui.checkBoxUseCNN.isChecked(),
                'min_cnn_thr': self.ui.doubleSpinBoxCNNThr.value(),
                'cnn_lowest': self.ui.doubleSpinBox_cnn_lowest.value(),
                'decay_time': self.ui.spinBoxDecayTime.value(),
                'fr': self.vi.viewer.workEnv.imgdata.meta['fps']
            }

        # Any additional eval kwargs set in the text entry
        if self.ui.groupBox_eval_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_eval_kwargs.toPlainText()
                eval_kwargs_add = eval(f"dict{_kwargs}")
                eval_kwargs.update(eval_kwargs_add)
            except:
                raise ValueError("Evaluation kwargs not formatted properly.")

        if self.vi.viewer.workEnv.imgdata.ndim == 4:
            is_3d = True
        else:
            is_3d = False

        # Make the output dict
        d = \
            {
                'item_name': self.ui.lineEdName.text(),
                'refit': self.ui.checkBoxRefit.isChecked(),
                'border_pix': bord_px,
                'is_3d': is_3d
            }

        # Group the kwargs of the two parts seperately
        if group_params:
            d.update(
                {
                    'cnmf_kwargs': cnmf_kwargs,
                    'eval_kwargs': eval_kwargs
                }
            )

        # or not
        else:
            d.update(
                {
                    **cnmf_kwargs,
                    **eval_kwargs
                }
            )

        return d

    @present_exceptions()
    def add_to_batch(self, params: dict = None) -> UUID:
        """
        Add a CNMF batch item with the currently set parameters and the current work environment.
        """
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                          'nothing to add to batch')
            return

        input_workEnv = self.vi.viewer.workEnv

        if params is None:
            d = self.get_params(group_params=True)
        else:
            # Check that user passed dict is formatted correctly
            required_keys = ['cnmf_kwargs', 'eval_kwargs', 'item_name', 'refit', 'border_pix']
            if any([k not in params.keys() for k in required_keys]):
                raise ValueError(f'Must pass a params dict with the following keys:\n'
                                 f'{required_keys}\n'
                                 f'Please see the docs for more information.')
            d = deepcopy(params)

        name = d['item_name']
        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CNMF: ' + name + ' to batch...')

        if self.ui.groupBox_seed_components.isChecked():
            seed_path = self.ui.lineEdit_seed_components_path.text()
            if not os.path.isfile(seed_path):
                raise FileNotFoundError(
                    "Seed file does not exist, check the path"
                )

            try:
                seed_params = HdfTools.load_dict(seed_path, 'data/segment_params')
            except:
                seed_params = 'unknown'

            d['use_seeds'] = True
            d['seed_params'] = seed_params
        else:
            d['use_seeds'] = False

        batch_manager = get_window_manager().get_batch_manager()
        u = batch_manager.add_item(
            module='CNMF',
            name=name,
            input_workEnv=input_workEnv,
            input_params=d,
            info=d
        )

        if u is None:
            self.vi.viewer.status_bar_label.clearMessage()
            return

        if d['use_seeds']:
            print("Copying component seed file")
            copy(seed_path, os.path.join(batch_manager.batch_path, f'{u}.ain'))

        self.vi.viewer.status_bar_label.showMessage('Done adding CNMF: ' + name + ' to batch!')
        self.ui.lineEdName.clear()

        return u
