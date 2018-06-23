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
from .core.add_to_project import AddToProjectDialog


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
        self.ui.actionROI_Manager.triggered.connect(lambda: self.run_module(roi_manager.ModuleGUI))

        self.ui.actionWork_Environment_Info.triggered.connect(self.open_workEnv_editor)
        self.ui.actionAdd_to_project.triggered.connect(self.add_work_env_to_project)

        self.ui.dockConsole.hide()

    @property
    def viewer_reference(self):
        return self._viewer

    @viewer_reference.setter
    def viewer_reference(self, viewer: ImageView):
        self._viewer = viewer

        self.run_module(roi_manager.ModuleGUI, hide=True)
        self.roi_manager = self.running_modules[-1]

        status_label = QtWidgets.QLabel()
        status_bar = self.statusBar()
        status_bar.addWidget(status_label)

        self._viewer.status_bar_label = status_label

        self.initialize_menubar_triggers()

        ns = {'pd': pd,
              'np': np,
              'pickle': pickle,
              'tifffile': tifffile,
              'ViewerWorkEnv': ViewerWorkEnv,
              'DataTypes': DataTypes,
              'objecteditor': objecteditor,
              'main': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as 'pickle    \n" \
              "tifffile as tifffile \n" \
              "ViewerInterface as main.vi \n" \
              "self as main         \n" \
              "objecteditor as objecteditor\n"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/viewer.pik'

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                    historyFile=cmd_history_file))

    def run_module(self, module_class, hide=False):
        # Show the QDockableWidget if it's already running
        for m in self.running_modules:
            if isinstance(m, module_class):
                m.show()
                return

        # Else create instance and start running it
        m = module_class(self, self._viewer)
        self.running_modules.append(m)

        if not hide:
            self.running_modules[-1].show()
        else:
            self.running_modules[-1].hide()

    def update_available_inputs(self):
        for m in self.running_modules:
            if hasattr(m, 'update_available_inputs'):
                m.update_available_inputs()

    def initialize_menubar_triggers(self):
        self.ui.actionBatch_Manager.triggered.connect(self.start_batch_manager)

        self.vi = ViewerInterface(self._viewer)

        self.ui.actionDump_Work_Environment.triggered.connect(self.vi.discard_workEnv)

        self.image_menu = ImageMenu(self.vi)

        self.ui.actionReset_Scale.triggered.connect(self.image_menu.reset_scale)
        self.ui.actionMeasure.triggered.connect(self.image_menu.measure_tool)
        self.ui.actionResize.triggered.connect(self.image_menu.resize)
        self.ui.actionCrop.triggered.connect(self.image_menu.crop)

    def start_batch_manager(self):
        if configuration.window_manager.batch_manager is None:
            configuration.window_manager.initialize_batch_manager()
            configuration.window_manager.batch_manager.show()

        else:
            configuration.window_manager.batch_manager.show()

    def open_workEnv_editor(self):
        self.vi.viewer.status_bar_label.setText('Please wait, loading editor interface...')

        if hasattr(self.vi.viewer.workEnv.roi_manager, 'roi_list'):
            roi_list = self.vi.viewer.workEnv.roi_manager.roi_list
        else:
            roi_list = None

        d = {'custom_columns_dict': self.vi.viewer.workEnv.custom_columns_dict,
             'isEmpty':             self.vi.viewer.workEnv.isEmpty,
             'imgdata':             self.vi.viewer.workEnv.imgdata.seq,
             'meta_data':           self.vi.viewer.workEnv.imgdata.meta,
             'roi_list':            roi_list,
             'comments':            self.vi.viewer.workEnv.comments,
             'origin_file':         self.vi.viewer.workEnv.origin_file,
             '_saved':              self.vi.viewer.workEnv._saved
             }

        try:
            changes = objecteditor.oedit(d)
        except:
            QtWidgets.QMessageBox.warning(self, 'Unable to open work environment editor',
                                          'The following error occured while trying to open the work environment editor:'
                                          '\n' + str(traceback.format_exc()))
            return

        if changes is not None:
            try:
                for key in d.keys():
                    setattr(self.vi.viewer.workEnv, key, d[key])
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

        if len(self.viewer_reference.workEnv.roi_manager.roi_list) == 0:
            QtWidgets.QMessageBox.warning(self, 'No curves',
                                          'You do not have any curves in your work environment')
            return

        else:
            self.add_to_project_dialog = AddToProjectDialog(self.viewer_reference.workEnv)
            self.add_to_project_dialog.signal_finished.connect(self._delete_add_to_project_dialog)
            self.add_to_project_dialog.show()

    def _delete_add_to_project_dialog(self):
        self.add_to_project_dialog.deleteLater()
