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
from common import configuration, system_config_window
# from viewer.modules import batch_manager
import traceback
from project_manager.project_manager import ProjectManager
from project_manager.project_browser.main_gui import ProjectBrowserGUI
import numpy as np; import tifffile; import pandas as pd;import pickle
import os
from common import start


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Mesmerize - Main Window')

        self.window_manager = configuration.window_manager

        self.ui.btnProjectBrowser.setVisible(False)
        self.ui.labelProjectBrowser.setVisible(False)

        self.ui.btnProjectBrowser.setIcon(QtGui.QIcon('./common/icons/noun_917603_cc.png'))
        self.ui.btnProjectBrowser.setIconSize(QtCore.QSize(100, 100))

        self.ui.btnNewProject.setIcon(QtGui.QIcon('./common/icons/noun_1327089_cc.png'))
        self.ui.btnNewProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnNewProject.clicked.connect(self.create_new_project)

        self.ui.btnOpenProject.setIcon(QtGui.QIcon('./common/icons/noun_1327109_cc.png'))
        self.ui.btnOpenProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnOpenProject.clicked.connect(self.open_project)

        self.ui.btnViewer.setIcon(QtGui.QIcon('./common/icons/noun_38902_cc.png'))
        self.ui.btnViewer.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnViewer.clicked.connect(self.spawn_new_viewer)

        self.ui.verticalLayoutViewersRunning.addWidget(self.window_manager.viewers.list_widget)

        self.ui.btnFlowchart.setIcon(QtGui.QIcon('./common/icons/noun_907242_cc.png'))
        self.ui.btnFlowchart.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnFlowchart.clicked.connect(self.spawn_new_flowchart)

        self.ui.verticalLayoutFlowchartRunning.addWidget(self.window_manager.flowcharts.list_widget)

        self.ui.btnPlot.setIcon(QtGui.QIcon('./common/icons/noun_635936_cc.png'))
        self.ui.btnPlot.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnPlot.clicked.connect(self.spawn_new_plot_gui)

        self.ui.verticalLayoutPlotsRunning.addWidget(self.window_manager.plots.list_widget)

        self.ui.btnClustering.setIcon(QtGui.QIcon('./common/icons/noun_195949_cc.png'))
        self.ui.btnClustering.setIconSize(QtCore.QSize(100, 100))

        self.sys_config_gui = system_config_window.SystemConfigGUI()
        self.ui.actionSystem_Configuration.triggered.connect(self.sys_config_gui.show)

        self.initialize_console_widget()

        self.resize(800, 550)
        # configuration.projPath = '/home/kushal/mesmerize_test_proj'

    def initialize_console_widget(self):
        ns = {'pd': pd,
              'np': np,
              'pickle': pickle,
              'tifffile': tifffile,
              'window_manager': self.window_manager,
              'main': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as pickle    \n" \
              "tifffile as tifffile \n" \
              "self.window_manager as window_manager     \n" \
              "self as main         \n" \

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/main.pik'

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))

        self.ui.dockConsole.hide()

    def create_new_project(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a new project')
        if path == '':
            return

        name, start = QtWidgets.QInputDialog.getText(self, '', 'Project Name:', QtWidgets.QLineEdit.Normal, '')

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
        self.ui.actionProject_Configuration.setEnabled(True)
        self.ui.actionProject_Configuration.triggered.connect(self.project_manager.show_config_window)

        self.set_proj_buttons_visible(False)

        self.initialize_project_browser()

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

        self.initialize_project_browser()

    def set_proj_buttons_visible(self, b):
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

    def initialize_project_browser(self):
        self.project_browser_window = QtWidgets.QMainWindow(parent=self)
        self.window_manager.project_browsers.append(self.project_browser_window)
        self.project_browser = ProjectBrowserGUI(self, self.project_manager.dataframe)
        self.project_browser_window.setCentralWidget(self.project_browser)

        num_columns = len(self.project_browser.tabs['root'].columns)
        self.project_browser_window.resize(min(1920, num_columns * 215), 600)

        self.ui.btnProjectBrowser.clicked.connect(self.project_browser_window.show)

    def spawn_new_viewer(self):
        start.viewer()

    def spawn_new_flowchart(self):
        start.flowchart()

    def spawn_new_plot_gui(self):
        start.plots()

    def spawn_new_clustering_gui(self):
        pass
