#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 24 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.batch_manager_pytemplate import *
import json
import pandas
from . import batch_modules
import uuid
import numpy as np
from .common import BatchRunInterface


class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    """GUI for the Batch Manager"""
    listwchanged = QtCore.pyqtSignal()

    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.listwBatch.itemDoubleClicked.connect(self.show_item_output)
        self.ui.listwBatch.itemClicked.connect(self.show_item_meta)

        self.ui.btnStart.clicked.connect(self.process_batch)
        self.ui.btnOpen.clicked.connect(self.open_batch)
        self.ui.btnDelete.clicked.connect(self.del_item)

        listwmodel = self.ui.listwBatch.model()
        listwmodel.rowsInserted.connect(self.listwchanged.emit)
        listwmodel.rowsRemoved.connect(self.listwchanged.emit)

        self.df = pandas.DataFrame(columns=['module', 'input_imgseq', 'input_params',
                                            'output_imgseq', 'output_misc', 'meta', 'uuid'])

    @staticmethod
    def get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def show_item_output(self, s: QtWidgets.QListWidgetItem):
        """Calls subclass of BatchRunInterface.show_output()"""
        item_txt = s.text()
        UUID = s.data(3)

        row = self.df.loc[self.df['uuid'] == UUID]
        output_imgseq = row['output_imgseq']
        output_misc = row['output_misc']

        module = item_txt.split(':')[0]
        m = globals()['batch_modules.'.join(module)]
        b = m.Batch()
        assert issubclass(b, BatchRunInterface)

        b.show_output(output_imgseq=output_imgseq, output_misc=output_misc)

    def show_item_meta(self, s: QtWidgets.QListWidgetItem):
        """Shows any meta-info (such as the batch module's params) in the meta-info label"""
        UUID = s.data(3)
        row = self.df.loc[self.df['uuid'] == UUID]
        meta = row['meta'].item()
        info = "\n".join([": ".join([key, str(val)]) for key, val in meta.items()])
        self.ui.labelMeta_info.setText(info)

    def process_batch(self):
        """Process all the items in the batch"""
        for r in self.df.iterrows():
            m = globals()['batch_modules.'.join(r['module'])]
            b = m.Batch
            assert issubclass(b, BatchRunInterface)

            if type(r['input_imgseq']) is uuid.UUID:
                input_imgseq = self.df.loc[self.df['uuid'] == r['input_imgseq']]['output_imgseq']
            else:
                input_imgseq = r['input_imgseq']

            b.process(input_imgseq=input_imgseq, input_params=r['input_params'])

    def add_item(self, module, input_imgseq, input_params, name='', meta=''):
        """
        :param  module:         The module to run, based on common.BatchRunInterface.
        :type   module:         str

        :param  name:           A name for the batch item
        :type   name:           str

        :param  input_imgseq:   Input imgseq that the module will use
        :type   input_imgseq:

        :param  input_params:   Input params that the module will use.
                                Depends on your subclass of BatchRunInterface.process() method
        :type   input_params:   np.ndarray

        :param  meta:   np.ndarray object array containing a dictionary with any metadata information
                        to display in the scroll area label.
        :type   meta:   np.ndarray
        """

        UUID = uuid.uuid4()
        self.df.append({'module':        module,
                        'input_imgseq':  input_imgseq,
                        'input_params':  input_params,
                        'meta':          meta,
                        'uuid':          UUID,
                        'output_imgseq': None,
                        'output_misc':   None,
                        })

        self.ui.listwBatch.addItem(module + ': ' + name)
        n = self.ui.listwBatch.count()
        item = self.ui.listwBatch.item(n-1)
        assert isinstance(item, QtWidgets.QListWidgetItem)
        item.setData(3, UUID)

    def del_item(self, s: QtWidgets.QListWidgetItem):
        """Delete an item from the batch and any corresponding dependents of hte item's output"""
        UUID = s.data(3)

        dependents = self.df.loc[self.df['input_imgseq'] == UUID]
        if not dependents.empty:
            if QtWidgets.QMessageBox.warning(self, 'This item has dependents!',
                                          'There are other items in your batch list that are dependent on the item you '
                                          'have selected to delete. If you delete this item from the batch then all '
                                          'dependent items will also be deleted.\n\nDo you still wish to continue?',
                                          QtWidgets.QMessageBox.Yes,
                                          QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return

            for item in self.ui.listwBatch.items():
                if item.data(3) == UUID:
                    ix = self.ui.listwBatch.indexFromItem(item).row()
                    self.ui.listwBatch.takeItem(ix)

            self.df = self.df.loc[self.df['input_imseq'] != UUID]

        self.df = self.df.loc[self.df['uuid'] != UUID]

        ix = self.ui.listwBatch.indexFromItem(s).row()
        self.ui.listwBatch.takeItem(ix)

    def open_batch(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open batch folder')
        if path == '':
            return
