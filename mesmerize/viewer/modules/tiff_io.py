#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerInterface
from .pytemplates.tiff_io_pytemplate import *
from ..core.viewer_work_environment import ViewerWorkEnv
import os
import traceback


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnSelectTiff.clicked.connect(self.select_tiff_file)
        self.ui.btnSelectMetaFile.clicked.connect(self.select_meta_file)
        self.ui.btnLoadIntoWorkEnv.clicked.connect(self.load_tiff_file)

    def select_tiff_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose tiff file', '', '(*.tiff)')
        if path == '':
            return
        if path[0] == '':
            return
        self.ui.labelFileTiff.setText(path[0])
        self.check_meta_path()

    def check_meta_path(self):
        meta_path = self.ui.labelFileTiff.text()[:-5] + '.json'
        if os.path.isfile(meta_path):
            self.ui.labelFileMeta.setText(meta_path)
            return True
        return False

    def select_meta_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose meta data file', '', '(*.json)')
        if path == '':
            return
        self.ui.labelFileMeta.setText(path[0])

    def load_tiff_file(self):
        tiff_path = self.ui.labelFileTiff.text()

        if tiff_path == '':
            QtWidgets.QMessageBox.warning(self, 'Nothing to load!', 'You must choose a file to load.')

        if self.ui.radioButtonImread.isChecked():
            method = 'imread'
        elif self.ui.radioButtonAsarray.isChecked():
            method = 'asarray'
        else:
            QtWidgets.QMessageBox.warning(self, 'No method selected!', 'You must select a method.')
            return
        self.vi.viewer.status_bar_label.showMessage('Please wait, loading tiff file, this may take a few minutes...')

        if not self.vi.discard_workEnv():
            return

        try:
            self.vi.viewer.workEnv = ViewerWorkEnv.from_tiff(path=tiff_path,
                                                             method=method,
                                                             meta_path=self.ui.labelFileMeta.text())
            self.vi.update_workEnv()
            self.vi.enable_ui(True)
            self.vi.viewer.ui.label_curr_img_seq_name.setText(os.path.basename(tiff_path))
            self.vi.viewer.status_bar_label.showMessage('File loaded into work environment!')
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!',
                                          'Could not open the chosen file.\n' + traceback.format_exc())
            self.vi.viewer.status_bar.clearMessage()
            return
