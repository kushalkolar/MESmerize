#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 5 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
from pyqtgraphCore.console import ConsoleWidget
from .welcome_window_pytemplate import *
from common import configuration, system_config_window, doc_pages
# from viewer.modules import batch_manager
import traceback
from project_manager.project_manager import ProjectManager
import numpy as np; import tifffile; import pandas as pd;import pickle
import os
from common import start
from functools import partial
from viewer.modules.batch_manager import ModuleGUI as BatchModuleGUI


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Mesmerize - Main Window')

        self.window_manager = configuration.window_manager

        self.ui.btnProjectBrowser.setVisible(False)
        self.ui.labelProjectBrowser.setVisible(False)

        mpath = os.path.abspath(__file__)
        mdir = os.path.dirname(mpath)

        self.ui.btnProjectBrowser.setIcon(QtGui.QIcon(mdir + '/icons/noun_917603_cc.png'))
        self.ui.btnProjectBrowser.setIconSize(QtCore.QSize(100, 100))

        self.ui.btnNewProject.setIcon(QtGui.QIcon(mdir + '/icons/noun_1327089_cc.png'))
        self.ui.btnNewProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnNewProject.clicked.connect(self.create_new_project)

        self.ui.btnOpenProject.setIcon(QtGui.QIcon(mdir + '/icons/noun_1327109_cc.png'))
        self.ui.btnOpenProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnOpenProject.clicked.connect(self.open_project)

        self.ui.btnViewer.setIcon(QtGui.QIcon(mdir + '/icons/noun_38902_cc.png'))
        self.ui.btnViewer.setIconSize(QtCore.QSize(24,24))
        self.ui.btnViewer.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnViewer.clicked.connect(self.spawn_new_viewer)

        self.ui.verticalLayoutViewersRunning.addWidget(self.window_manager.viewers.list_widget)

        self.ui.btnFlowchart.setIcon(QtGui.QIcon(mdir + '/icons/noun_907242_cc.png'))
        self.ui.btnFlowchart.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnFlowchart.clicked.connect(self.spawn_new_flowchart)

        self.ui.verticalLayoutFlowchartRunning.addWidget(self.window_manager.flowcharts.list_widget)

        # self.ui.btnPlot.setIcon(QtGui.QIcon(mdir + '/icons/noun_635936_cc.png'))
        # self.ui.btnPlot.setIconSize(QtCore.QSize(100, 100))
        # # self.ui.btnPlot.clicked.connect(self.spawn_new_plot_gui)
        #
        # self.ui.verticalLayoutPlotsRunning.addWidget(self.window_manager.plots.list_widget)
        #
        # self.ui.btnClustering.setIcon(QtGui.QIcon(mdir + '/icons/noun_195949_cc.png'))
        # self.ui.btnClustering.setIconSize(QtCore.QSize(100, 100))

        self.ui.actionDocs_homepage.triggered.connect(doc_pages['home'])
        self.ui.actionNew_Project_Docs.triggered.connect(doc_pages['new_project'])

        self.sys_config_gui = system_config_window.SystemConfigGUI()
        self.ui.actionSystem_Configuration.triggered.connect(self.sys_config_gui.show)

        self.initialize_console_widget()

        self.resize(800, 625)
        # configuration.projPath = '/home/kushal/mesmerize_test_proj'

        self._batch_manager = None

    def initialize_console_widget(self):
        ns = {'pd': pd,
              'np': np,
              'pickle': pickle,
              'tifffile': tifffile,
              'configuration': configuration,
              'window_manager': self.window_manager,
              'main': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as pickle    \n" \
              "configuration as configuration\n" \
              "tifffile as tifffile \n" \
              "self.window_manager as window_manager     \n" \
              "self as main         \n" \

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/main.pik'
        console = ConsoleWidget(namespace=ns, text=txt, historyFile=cmd_history_file)
        self.ui.dockConsole.setWidget(console)

        self.resizeDocks([self.ui.dockConsole], [235], QtCore.Qt.Vertical)
        # console.resize(self.ui.dockConsole.width(), 100)
        # self.ui.dockConsole.resize(self.ui.dockConsole.width(), 150)
        # console.input.resize(console.input.width(), 80)

        # self.ui.dockConsole.hide()

    def create_new_project(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a new project')
        if path == '':
            return

        name, start = QtWidgets.QInputDialog.getText(self, '', 'Project Name:', QtWidgets.QLineEdit.Normal, '')

        if any(s in name for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid Name', 'Project Name can only contain alphanumeric characters')
            return

        if start and name != '':
            try:
                self.project_manager = ProjectManager(path + '/' + name)
                configuration.project_manager = self.project_manager
                self.project_manager.setup_new_project()
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Error!',
                                              'Could not create a new project.\n' +
                                              traceback.format_exc())
                return
        else:
            return
        self.ui.actionProject_Configuration.setEnabled(True)
        self.ui.actionProject_Configuration.triggered.connect(self.project_manager.show_config_window)

        self.set_proj_buttons_visible(False)

        # self.initialize_project_browser()

    def open_project(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Project Folder')

        if path == '':
            return

        self.project_manager = ProjectManager(path)
        configuration.project_manager = self.project_manager

        try:
            self.project_manager.open_project()
        except:
            QtWidgets.QMessageBox.warning(self, 'Error',
                                          'The selected directory is probably not a valid Mesmerize Project.\n' +
                                          traceback.format_exc())
            return

        self.ui.actionProject_Configuration.setEnabled(True)
        self.ui.actionProject_Configuration.triggered.connect(self.project_manager.show_config_window)

        self.set_proj_buttons_visible(False)

        start.project_browser()
        self.ui.btnProjectBrowser.clicked.connect(partial(configuration.window_manager.show_project_browser, 0))
        start.load_child_dataframes_gui()

    def set_proj_buttons_visible(self, b: bool):
        self.ui.btnNewProject.setVisible(b)
        self.ui.labelNewProj.setVisible(b)
        self.ui.btnOpenProject.setVisible(b)
        self.ui.labelOpenProject.setVisible(b)
        self.ui.listWidgetRecentProjects.setVisible(b)
        self.ui.labelRecentProjects.setVisible(b)

        self.ui.btnProjectBrowser.setHidden(b)
        self.ui.labelProjectBrowser.setHidden(b)

    def find_recent_projects(self):
        pass

    def populate_recent_projects_list(self):
        pass

    # def start_batch_manager(self):
    #     self.batch_manager = batch_manager.ModuleGUI(parent=self, self)
    #     self.batch_manager.hide()

    def spawn_new_viewer(self):
        start.viewer()

    def spawn_new_flowchart(self):
        start.flowchart()

    # def spawn_new_plot_gui(self):
    #     start.plots()

    def get_batch_manager(self, run_batch: list = None) -> BatchModuleGUI:
        if run_batch is not None:
            self._batch_manager = BatchModuleGUI(parent=None, run_batch=run_batch)
            self._batch_manager.show()
            return self._batch_manager

        elif self._batch_manager is None:
            QtWidgets.QMessageBox.information(None, 'No batch manager open',
                                           'Choose a location for a new batch or create a new batch')

            self._batch_manager = BatchModuleGUI(parent=None)
            #self._batch_manager.show()
            return self._batch_manager
        else:
            return self._batch_manager
            #self._batch_manager.show()
            #self._batch_manager.show()
