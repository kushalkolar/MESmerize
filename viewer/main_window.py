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
from pyqtgraphCore.imageview import ImageView
from .modules import *
from .modules.batch_manager import ModuleGUI as BatchModuleGUI
from .core.common import ViewerInterface
import pickle;
import tifffile;
import numpy as np;
import pandas as pd;
from .core import DataTypes
from .core.viewer_work_environment import ViewerWorkEnv
import os
from common import configuration
from .image_menu.main import ImageMenu
from spyder.widgets.variableexplorer import objecteditor
import traceback


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.running_modules = []
        # TODO: Integrate viewer initiation here instead of outside
        self.ui.actionMesfile.triggered.connect(lambda: self.run_module(mesfile_io.ModuleGUI))
        self.ui.actionTiff_file.triggered.connect(lambda: self.run_module(tiff_io.ModuleGUI))
        self.ui.actionCNMF_E.triggered.connect(lambda: self.run_module(cnmfe.ModuleGUI))
        self.ui.actionMotion_Correction.triggered.connect(lambda: self.run_module(caiman_motion_correction.ModuleGUI))
        self.ui.actionWork_Environment_Info.triggered.connect(self.open_workEnv_editor)

        self.ui.actionAdd_to_project.triggered.connect(self.add_work_env_to_project)

        self.ui.dockConsole.hide()

    @property
    def viewer_reference(self):
        return self._viewer

    @viewer_reference.setter
    def viewer_reference(self, viewer: ImageView):
        self._viewer = viewer

        status_label = QtWidgets.QLabel()
        status_bar = self.statusBar()
        status_bar.addWidget(status_label)

        self._viewer.status_bar_label = status_label

        self.initialize_menubar_triggers()

        ns = {'pd':             pd,
              'np':             np,
              'pickle':         pickle,
              'tifffile':       tifffile,
              'ViewerWorkEnv':       ViewerWorkEnv,
              'DataTypes':      DataTypes,
              'objecteditor':   objecteditor,
              'main':           self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as 'pickle    \n" \
              "tifffile as tifffile \n" \
              "MesmerizeCore.packager as packager \n" \
              "MesmerizeCore.DataTypes as DataTypes \n" \
              "viewer as main.viewer_reference     \n" \
              "ViewerInterface as main.vi \n" \
              "self as main         \n" \
              "objecteditor as objecteditor\n"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/viewer.pik'

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                    historyFile=cmd_history_file))

    def run_module(self, module_class):
        # Show the QDockableWidget if it's already running
        for m in self.running_modules:
            if isinstance(m, module_class):
                m.show()
                return

        # Else create instance and start running it
        self.running_modules.append(module_class(self, self._viewer))

        self.running_modules[-1].show()

    def update_available_inputs(self):
        for m in self.running_modules:
            if hasattr(m, 'update_available_inputs'):
                m.update_available_inputs()

    def initialize_menubar_triggers(self):
        if configuration.proj_path is None:
            self.ui.actionBatch_Manager.triggered.connect(self.ask_create_standalone_batch)
        else:
            self.ui.actionBatch_Manager.triggered.connect(configuration.window_manager.batch_manager.show)
            configuration.window_manager.batch_manager.listwchanged.connect(self.update_available_inputs)

        self.vi = ViewerInterface(self._viewer)

        self.ui.actionDump_Work_Environment.triggered.connect(self.vi.discard_workEnv)

        self.image_menu = ImageMenu(self.vi)

        self.ui.actionReset_Scale.triggered.connect(self.image_menu.reset_scale)
        self.ui.actionMeasure.triggered.connect(self.image_menu.measure_tool)
        self.ui.actionResize.triggered.connect(self.image_menu.resize)
        self.ui.actionCrop.triggered.connect(self.image_menu.crop)

    def ask_create_standalone_batch(self):
        if QtWidgets.QMessageBox.question(self, 'No project open',
                                          'Would you like to create a standalone batch?',
                                          QtWidgets.QMessageBox.No,
                                          QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
            return

        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a batch')
        if path == '':
            return

        name, start = QtWidgets.QInputDialog.getText(self, '', 'Batch Name:', QtWidgets.QLineEdit.Normal, '')

        if start and name != '':
            batch_path = path + '/' + name
            os.makedirs(batch_path)
            configuration.window_manager.initialize_batch_manager(batch_path)

    def open_workEnv_editor(self):
        self.vi.viewer.status_bar_label.setText('Please wait, loading editor interface...')
        try:
            changes = objecteditor.oedit(self.vi.viewer.workEnv)
        except:
            QtWidgets.QMessageBox.warning(self, 'Unable to open work environment editor',
                                          'The following error occured while trying to open the work environment editor:'
                                          '\n' + str(traceback.format_exc()))
            return

        if changes is not None:
            try:
                self.vi.viewer.workEnv = changes
            except:
                QtWidgets.QMessageBox.warning(self, 'Unable to apply changes',
                                              'The following error occured while trying to save changes to the work '
                                              'environment. You may want to use the console and make sure your work '
                                              'environment has not been corrupted.'
                                              '\n' + str(traceback.format_exc()))
                return
        elif changes is None:
            self.vi.viewer.status_bar_label.setText('Work environment unchanged')
            return

        self.vi.viewer.status_bar_label.setText('Your edits were successfully applied to the work environment!')

        # You can even let the user save changes if they click "OK", and the function returns None if they cancel

    def add_work_env_to_project(self):
        if configuration.proj_path is None:
            if QtWidgets.QMessageBox.question(self, 'No project open',
                                              'Would you like to switch to project mode?',
                                              QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
                return
            else:
                import common.start
                common.start.main()
