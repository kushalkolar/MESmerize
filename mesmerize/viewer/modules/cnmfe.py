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
from .pytemplates.cnmfe_pytemplate import *
import json
from ...common import get_window_manager
from ...common.qdialogs import *
from uuid import UUID
from copy import deepcopy


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchCorrPNR.clicked.connect(lambda: self.add_to_batch_corr_pnr())
        self.ui.btnAddToBatchCNMFE.clicked.connect(lambda: self.add_to_batch_cnmfe())

    @present_exceptions()
    def get_params(self, item_type: str, group_params: bool = False) -> dict:
        """
        Get a dict of the set parameters.
        If the work environment was loaded from a motion correction batch item it put the bord_px in the dict.
        Doesn't use any arguments

        :param item_type: one of `corr_pnr` or `cnmfe`
        """
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            raise KeyError('No framerate for current image sequence!',
                           'You must set a framerate for the current image sequence. '
                           'You can set it manually in the console like this:\nget_meta()["fps"] = <framerate>')

        # Get bord_px param if motion correction was performed
        history_trace = self.vi.viewer.workEnv.history_trace
        try:
            bord_px = next(d for ix, d in enumerate(history_trace) if 'caiman_motion_correction' in d)['caiman_motion_correction']['bord_px']
        except StopIteration:
            bord_px = 0

        deconv = self.ui.comboBoxDeconv.currentText()
        if deconv == 'SKIP':
            method_deconvolution = None
            deconv_flag = False
        else:
            deconv_flag = True
            method_deconvolution = deconv

        gSig = self.ui.spinBoxGSig.value()

        # Correlation-PNR param
        corr_pnr_kwargs = \
            {
                'gSig': gSig
            }

        kval = self.ui.spinBoxK.value()
        if kval == 0:
            kval = None

        # CNMFE kwargs
        cnmfe_kwargs = \
            {
                'gSig': (gSig, gSig),
                'gSiz': (4 * gSig + 1, 4 * gSig + 1),
                'border_pix': bord_px,
                'rf': self.ui.spinBoxRf.value(),
                'stride': self.ui.spinBoxOverlap.value(),
                'gnb': self.ui.spinBoxGnb.value(),
                'nb_patch': self.ui.spinBoxNb_patch.value(),
                'K': kval,
                'min_corr': self.ui.doubleSpinBoxMinCorr.value(),
                'min_pnr': self.ui.spinBoxMinPNR.value(),
                'deconv_flag': deconv_flag,
                'method_deconvolution': method_deconvolution,
                'Ain': self.ui.lineEditAin.text().replace(' ', '').strip('\n'),
                'p': self.ui.spinBox_p.value(),
                'merge_thresh': self.ui.doubleSpinBoxMergeThresh.value(),
                'ssub': self.ui.spinBox_ssub.value(),
                'tsub': self.ui.spinBox_tsub.value(),
                'low_rank_background': self.ui.checkBox_low_rank_background.isChecked(),
                'ring_size_factor': self.ui.doubleSpinBox_ring_size_factor.value(),
                'update_background_components': True,
                'del_duplicates': True
            }

        # Any additional CNMFE kwargs set in the text entry
        if self.ui.groupBox_cnmf_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_cnmf_kwargs.toPlainText()
                cnmfe_kwargs_add = eval(f"dict({_kwargs})")
                cnmfe_kwargs.update(cnmfe_kwargs_add)
            except:
                raise ValueError("CNMFE kwargs not formatted properly.")

        # kwargs for component evaluation
        eval_kwargs = \
            {
                'fr': self.vi.viewer.workEnv.imgdata.meta['fps'],
                'min_SNR': self.ui.spinBoxMinSNR.value(),
                'rval_thr': self.ui.doubleSpinBoxRValuesMin.value(),
                'decay_time': self.ui.doubleSpinBoxDecayTime.value(),
            }

        # Any additional eval kwargs set in the text entry
        if self.ui.groupBox_eval_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_eval_kwargs.toPlainText()
                eval_kwargs_add = eval(f"dict({_kwargs})")
                eval_kwargs.update(eval_kwargs_add)
            except:
                raise ValueError("Evaluation kwargs not formatted properly.")

        # Output either the dict for corr-pnr or CNMFE
        if item_type == 'corr_pnr':
            item_name = self.ui.lineEdCorrPNRName.text()
            d = \
                {
                    'item_name':        item_name,
                    'do_cnmfe':         False,
                    'do_corr_pnr':      True,
                    'border_pix':       bord_px
                }

            if group_params:
                d.update({'corr_pnr_kwargs': corr_pnr_kwargs})
            else:
                d.update({**corr_pnr_kwargs})

        elif item_type == 'cnmfe':
            item_name = self.ui.lineEdName.text()
            d = \
                {
                    'item_name':        item_name,
                    'do_cnmfe':         True,
                    'do_corr_pnr':      False,
                    'border_pix':       bord_px
                }
            if group_params:
                d.update(
                    {
                        'cnmfe_kwargs': cnmfe_kwargs,
                        'eval_kwargs': eval_kwargs,
                    }
                )
            else:
                d.update(
                    {
                        **cnmfe_kwargs,
                        **eval_kwargs
                    }
                )
        else:
            raise ValueError("Must specify argument `item_type` as either 'corr_pnr' or 'cnmfe'")

        return d

    def add_to_batch_corr_pnr(self, params: dict = None) -> UUID:
        """
        Add a Corr PNR batch item with the currently set parameters and the current work environment.

        """
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                          'nothing to add to batch')
            return
        input_workEnv = self.vi.viewer.workEnv

        if params is None:
            d = self.get_params('corr_pnr', group_params=True)
        else:
            # Check that user passed dict is formatted correctly
            required_keys = ['item_name', 'do_cnmfe', 'do_corr_pnr', 'border_pix', 'corr_pnr_kwargs']
            if any([k not in params.keys() for k in required_keys]):
                raise ValueError(f'Must pass a params dict with the following keys:\n'
                                 f'{required_keys}\n'
                                 f'Please see the docs for more information.')
            d = deepcopy(params)

        batch_manager = get_window_manager().get_batch_manager()
        name = d['item_name']

        self.vi.viewer.status_bar_label.showMessage('Please wait, adding Corr PNR: ' + name + ' to batch...')

        u = batch_manager.add_item(module='CNMFE',
                                   name=name,
                                   input_workEnv=input_workEnv,
                                   input_params=d,
                                   info=d
                                   )

        self.vi.viewer.status_bar_label.showMessage('Done adding Corr PNR: ' + name + ' to batch!')
        self.clear_line_edits()

        return u

    def add_to_batch_cnmfe(self, params: dict = None) -> UUID:
        """
        Add a CNMFE batch item with the currently set parameters and the current work environment.
        """
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                          'nothing to add to batch')
            return
        input_workEnv = self.vi.viewer.workEnv

        if params is None:
            d = self.get_params('cnmfe', group_params=True)
        else:
            # Check that user passed dict is formatted correctly
            required_keys = ['item_name', 'do_cnmfe', 'do_corr_pnr', 'border_pix', 'cnmfe_kwargs', 'eval_kwargs']
            if any([k not in params.keys() for k in required_keys]):
                raise ValueError(f'Must pass a params dict with the following keys:\n'
                                 f'{required_keys}\n'
                                 f'Please see the docs for more information.')
            d = deepcopy(params)

        name = d['item_name']
        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CNMFE: ' + name + ' to batch...')

        batch_manager = get_window_manager().get_batch_manager()
        u = batch_manager.add_item(module='CNMFE',
                                   name=name,
                                   input_workEnv=input_workEnv,
                                   input_params=d,
                                   info=d
                                   )

        if u is None:
            self.vi.viewer.status_bar_label.clearMessage()
            return

        self.vi.viewer.status_bar_label.showMessage('Done adding CNMFE: ' + name + ' to batch!')
        self.clear_line_edits()

        return u

    def clear_line_edits(self):
        self.ui.lineEdCorrPNRName.clear()
        self.ui.lineEdName.clear()
        self.ui.lineEditAin.clear()
