#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 21 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .main_window_pytemplate import *
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .modules import *
from .modules.batch_manager import ModuleGUI as BatchModuleGUI
from .modules.common import ViewerInterface


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.running_modules = []

        self.ui.actionMesfile.triggered.connect(lambda: self.run_module(mesfile_io.ModuleGUI))
        self.ui.actionTiff_file.triggered.connect(lambda: self.run_module(tiff_io.ModuleGUI))
        self.ui.actionCNMF_E.triggered.connect(lambda: self.run_module(cnmfe.ModuleGUI))
        self.ui.actionMotion_Correction.triggered.connect(lambda: self.run_module(caiman_motion_correction.ModuleGUI))
        self.ui.actionStandard_tools.triggered.connect(lambda: self.run_module(standard_tools.ModuleGUI))

    @property
    def viewer_reference(self):
        return self._viewer_ref

    @viewer_reference.setter
    def viewer_reference(self, viewer_ref):
        self._viewer_ref = viewer_ref

        self.ui.actionBatch_Manager.triggered.connect(self._viewer_ref.batch_manager.show)
        self._viewer_ref.batch_manager.listwchanged.connect(self.update_available_inputs)

        self.vi = ViewerInterface(viewer_ref)

        self.ui.actionDump_Work_Environment.triggered.connect(self.vi.VIEWER_discard_workEnv)

    def run_module(self, module_class):
        # Show the QDockableWidget if it's already running
        for m in self.running_modules:
            if isinstance(m, module_class):
                m.show()
                return

        # Else create instance and start running it
        self.running_modules.append(module_class(self, self._viewer_ref))

        self.running_modules[-1].show()

    def update_available_inputs(self):
        for m in self.running_modules:
            if hasattr(m, 'update_available_inputs'):
                m.update_available_inputs()
