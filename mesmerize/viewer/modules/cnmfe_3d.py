#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerUtils
from .pytemplates.cnmf_3d_pytemplate import *
from ...common import get_window_manager
from ...common.qdialogs import *


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_CNMF3D_template()
        self.ui.setupUi(self)

        self.ui.pushButton_add_to_batch.clicked.connect(self.add_to_batch)

    @present_exceptions()
    def get_params(self, *args, group_params: bool = False, **kwargs) -> dict:
        """
        Get a dict of the params.
        Doesn't use arguments, *args and **kwargs are there just for compatibility with `@present_exceptions`
        """
        if self.vi.viewer.workEnv.imgdata.meta['fps'] == 0:
            raise KeyError('No framerate for current image sequence!',
                           'You must set a framerate for the current image sequence. '
                           'You can set it manually in the console like this:\nget_meta()["fps"] = <framerate>')

        # kwargs for CNMF
        cnmf_kwargs = {
                        'k': self.ui.spinBox_k.value(),
                        'gSig': [
                            self.ui.spinBox_gSig_x.value(),
                            self.ui.spinBox_gSig_y.value(),
                            self.ui.spinBox_gSig_z.value()
                        ],
                        'merge_thresh': self.ui.doubleSpinBox_merge_threshold.value(),
                        'p': self.ui.spinBox_p.value()
        }

        # kwargs for component evaluation
        eval_kwargs = {
                        'fr':           self.vi.viewer.workEnv.imgdata.meta['fps'],
                        'decay_time':   self.ui.doubleSpinBox_decay_time.value(),
                        'min_SNR':      self.ui.doubleSpinBox_minSNR.value(),
                        'rval_thr':     self.ui.doubleSpinBox_rval.value(),
        }

        d = {
            'refit':        self.ui.checkBox_refit.isChecked(),
            'item_name':    self.ui.lineEdit_name.text(),
            'use_patches':  self.ui.groupBox_use_patches.isChecked()
        }

        if d['use_patches']:
            cnmf_kwargs.update(
                {
                    'rf': self.ui.spinBox_rf.value(),
                    'stride': self.ui.spinBox_stride.value(),
                }
            )

        if group_params:
            d.update(
                {
                    'cnmf_kwargs': cnmf_kwargs,
                    'eval_kwargs': eval_kwargs,
                }
            )
        else:
            d.update(
                {
                    **cnmf_kwargs,
                    **eval_kwargs,
                }
            )

        return d

    def set_params(self, d: dict):
        if ('cnmf_kwargs' in d.keys()) and ('eval_kwargs' in d.keys()):
            p = {**d['cnmf_kwargs'], **d['eval_kwargs']}
        else:
            p = d

        self.ui.spinBox_rf.setValue(p['rf'])
        self.ui.spinBox_stride.setValue(p['stride'])
        self.ui.spinBox_K.setValue(p['k'])

        self.ui.spinBox_gSig_x.setValue(p['gSig'][0])
        self.ui.spinBox_gSig_y.setValue(p['gSig'][1])
        self.ui.spinBox_gSig_z.setValue(p['gSig'][2])

        self.ui.doubleSpinBox_merge_threshold.setValue(p['merge_thresh'])
        self.ui.spinBox_p.setValue(p['p'])
        self.ui.doubleSpinBox_decay_time.setValue(p['decay_time'])
        self.ui.doubleSpinBox_minSNR.setValue(p['min_SNR'])
        self.ui.doubleSpinBox_rval.setValue(p['rval_thr'])

        self.ui.lineEdit_name.setText(d['item_name'])  # same key regardless of format

    @present_exceptions()
    def add_to_batch(self, *args, **kwargs):
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                          'nothing to add to batch')
            return

        d = self.get_params(group_params=True)
        name = d['item_name']

        self.vi.viewer.status_bar_label.showMessage(f'Please wait, adding CNMF 3D item: "{name}" to batch')

        bm = get_window_manager().get_batch_manager()

        bm.add_item(
            module='CNMF_3D',
            name=name,
            input_workEnv=self.vi.viewer.workEnv,
            input_params=d,
            info=self.get_params()
        )

        self.vi.viewer.status_bar_label.showMessage(f'Finished adding CNMF 3D item: "{name}" to batch')
        self.ui.lineEdit_name.clear()
