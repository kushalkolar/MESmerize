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
from pyqtgraphCore.console import ConsoleWidget
from .modules import *
from .modules.batch_manager import ModuleGUI as BatchModuleGUI
from .modules.common import ViewerInterface
import pickle; import tifffile; import numpy as np; import pandas as pd; from MesmerizeCore import DataTypes
from MesmerizeCore import packager
import os
from MesmerizeCore import configuration
from .image_menu.main import ImageMenu


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

        self.ui.dockConsole.hide()

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

        ns = {'pd':         pd,
              'np':         np,
              'pickle':     pickle,
              'tifffile':   tifffile,
              'packager':   packager,
              'DataTypes':  DataTypes,
              'main':       self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as 'pickle    \n" \
              "tifffile as tifffile \n" \
              "MesmerizeCore.packager as packager" \
              "MesmerizeCore.DataTypes as DataTypes" \
              "viewer as main.viewer     \n" \
              "ViewerInterface as main.vi" \
              "self as main         \n" \
              "call curr_tab() to return current tab widget\n" \
              "call addTab(<dataframe>, <title>, <filtLog>, <filtLogPandas>) to add a new tab\n"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/viewer.pik'

        self.dockWidget.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))

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

