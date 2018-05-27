#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.tiff_io_pytemplate import *
from MesmerizeCore.packager import viewerWorkEnv
import os

class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

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
        self.ui.labelFileTiff.setText(path[0])

        meta_path = path[0][:-5] + '.json'
        if os.path.isfile(meta_path):
            self.ui.labelFileMeta.setText(meta_path)

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

        try:
            self.viewer_ref.workEnv = viewerWorkEnv.from_tiff(path=tiff_path,
                                                              method=method,
                                                              meta_path=self.ui.labelFileMeta.text())
            self.VIEWER_update_workEnv()
            self.VIEWER_enable_ui(True)

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return



