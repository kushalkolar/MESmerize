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
from ...common.utils import HdfTools
from uuid import UUID
from shutil import copy
import os
from copy import deepcopy


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_CNMF3D_template()
        self.ui.setupUi(self)

        # If keep memmap, cannot use another item's memmap
        self.ui.checkBox_keep_memmap.toggled.connect(self.set_memmap_checkboxes)

        # If use another item's memmap, can't keep it's own memmap
        self.ui.groupBox_use_previous_memmap.toggled.connect(self.set_memmap_checkboxes)

        self.ui.pushButton_add_to_batch.clicked.connect(lambda: self.add_to_batch())

    def set_memmap_checkboxes(self):
        if self.ui.checkBox_keep_memmap.isChecked():
            self.ui.groupBox_use_previous_memmap.setChecked(False)

        elif self.ui.groupBox_use_previous_memmap.isChecked():
            self.ui.checkBox_keep_memmap.setChecked(False)

    @present_exceptions()
    def get_params(self, *args, group_params: bool = False) -> dict:
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

        # Any additional cnmf kwargs
        if self.ui.groupBox_cnmf_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_cnmf_kwargs.toPlainText()
                cnmf_kwargs_add = eval(f"dict({_kwargs})")
                cnmf_kwargs.update(cnmf_kwargs_add)
            except:
                raise ValueError("CNMF kwargs not formatted properly.")


        # kwargs for component evaluation
        eval_kwargs = {
                        'fr':           self.vi.viewer.workEnv.imgdata.meta['fps'],
                        'decay_time':   self.ui.doubleSpinBox_decay_time.value(),
                        'min_SNR':      self.ui.doubleSpinBox_minSNR.value(),
                        'rval_thr':     self.ui.doubleSpinBox_rval.value(),
        }

        # Any additional eval kwargs
        if self.ui.groupBox_eval_kwargs.isChecked():
            try:
                _kwargs = self.ui.plainTextEdit_eval_kwargs.toPlainText()
                eval_kwargs_add = eval(f"dict{_kwargs}")
                eval_kwargs.update(eval_kwargs_add )
            except:
                raise ValueError("Evaluation kwargs not formatted properly.")

        use_memmap = self.ui.groupBox_use_previous_memmap.isChecked()
        memmap_uuid = self.ui.lineEdit_memmap_uuid.text()

        if use_memmap:
            try:
                UUID(memmap_uuid)
            except ValueError:
                raise ValueError('Invalid UUID format. Please check that you entered the UUID correctly.')

        d = {
            'refit':        self.ui.checkBox_refit.isChecked(),
            'item_name':    self.ui.lineEdit_name.text(),
            'use_patches':  self.ui.groupBox_use_patches.isChecked(),
            'use_memmap':   use_memmap,
            'memmap_uuid':  memmap_uuid,
            'keep_memmap':  self.ui.checkBox_keep_memmap.isChecked()
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

    @present_exceptions()
    def add_to_batch(self, params: dict = None) -> UUID:
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Empty work environment', 'The work environment is empty, '
                                                                          'nothing to add to batch')
            return

        if params is None:
            d = self.get_params(group_params=True)
        else:
            # Check that user passed dict is formatted correctly
            required_keys = ['cnmf_kwargs', 'eval_kwargs', 'item_name', 'refit', 'use_patches',
                             'use_memmap', 'memmap_uuid', 'keep_memmap']
            if any([k not in params.keys() for k in required_keys]):
                raise ValueError(f'Must pass a params dict with the following keys:\n'
                                 f'{required_keys}\n'
                                 f'Please see the docs for more information.')
            d = deepcopy(params)

        name = d['item_name']

        self.vi.viewer.status_bar_label.showMessage(f'Please wait, adding CNMF 3D item: "{name}" to batch')

        bm = get_window_manager().get_batch_manager()

        if d['use_memmap']:
            memmap_uuid = UUID(d['memmap_uuid'])

            if memmap_uuid not in bm.df['uuid'].values:
                raise ValueError("The entered memmap UUID isn't present in this batch")

            bm.df.loc[bm.df['uuid'] == memmap_uuid, 'save_temp_files'] = 1

        if self.ui.groupBox_seed_components.isChecked():
            if self.ui.groupBox_seed_components.isChecked():
                seed_path = self.ui.lineEdit_seed_components_path.text()
                if not os.path.isfile(seed_path):
                    raise FileNotFoundError(
                        "Seed file does not exist, check the path"
                    )

                seed_params = HdfTools.load_dict(seed_path, 'data/segment_params')

                d['use_seeds'] = True
                d['seed_params'] = seed_params

        u = bm.add_item(
            module='CNMF_3D',
            name=name,
            input_workEnv=self.vi.viewer.workEnv,
            input_params=d,
            info=d
        )

        if u is None:
            self.vi.viewer.status_bar_label.clearMessage()
            return

        if d['use_seeds']:
            print("Copying component seeds files")
            copy(seed_path, os.path.join(bm.batch_path, f'{u}.ain'))

        if d['keep_memmap']:
            bm.df.loc[bm.df['uuid'] == u, 'save_temp_files'] = 1

        self.vi.viewer.status_bar_label.showMessage(f'Finished adding CNMF 3D item: "{name}" to batch')
        self.ui.lineEdit_name.clear()
        self.ui.lineEdit_memmap_uuid.clear()

        return u
