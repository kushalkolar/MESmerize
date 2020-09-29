#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 5 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..pyqtgraphCore.console import ConsoleWidget
from .pytemplates.welcome_window_pytemplate import *
# from ..project_manager import ProjectManager
from ..common import configuration, system_config_window, doc_pages, get_project_manager, set_project_manager
from ..common import get_window_manager, is_mesmerize_project
# from viewer.modules import batch_manager
import os
from ..common import start
from ..viewer.modules.batch_manager import ModuleGUI as BatchModuleGUI
from glob import glob
from ..plotting import open_plot_file
from functools import partial
from .qdialogs import *
import re
from .. import __version__


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Mesmerize - Welcome Window')

        self.window_manager = get_window_manager()

        self.ui.btnProjectBrowser.setVisible(False)
        self.ui.labelProjectBrowser.setVisible(False)

        mpath = os.path.abspath(__file__)
        mdir = os.path.dirname(mpath)

        self.ui.btnProjectBrowser.setIcon(QtGui.QIcon(mdir + '/icons/noun_917603_cc.png'))
        self.ui.btnProjectBrowser.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnProjectBrowser.clicked.connect(self.show_project_browser)

        self.ui.btnNewProject.setIcon(QtGui.QIcon(mdir + '/icons/noun_1327089_cc.png'))
        self.ui.btnNewProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnNewProject.clicked.connect(self.create_new_project)

        self.ui.btnOpenProject.setIcon(QtGui.QIcon(mdir + '/icons/noun_1327109_cc.png'))
        self.ui.btnOpenProject.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnOpenProject.clicked.connect(self.open_project_dialog)

        sys_cfg = configuration.get_sys_config()
        self.ui.listWidgetRecentProjects.addItems(sys_cfg['recent_projects'])
        self.ui.listWidgetRecentProjects.itemDoubleClicked.connect(lambda item: self.open_project(item.text()))

        self.ui.btnViewer.setIcon(QtGui.QIcon(mdir + '/icons/noun_38902_cc.png'))
        self.ui.btnViewer.setIconSize(QtCore.QSize(24, 24))
        self.ui.btnViewer.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnViewer.clicked.connect(self.open_new_viewer)

        self.ui.btnFlowchart.setIcon(QtGui.QIcon(mdir + '/icons/noun_907242_cc.png'))
        self.ui.btnFlowchart.setIconSize(QtCore.QSize(100, 100))
        self.ui.btnFlowchart.clicked.connect(self.open_new_flowchart)

        self.ui.actionDocs_homepage.triggered.connect(doc_pages['home'])
        self.ui.actionNew_Project_Docs.triggered.connect(doc_pages['new_project'])
        self.ui.actionSystem_Configuration_Docs.triggered.connect(doc_pages['sys_config'])

        self.ui.actionReport_issue_bug.triggered.connect(doc_pages['issue-tracker'])
        self.ui.actionQuestions_discussion.triggered.connect(doc_pages['gitter'])

        self.sys_config_gui = system_config_window.SystemConfigGUI()
        self.ui.actionSystem_Configuration.triggered.connect(self.sys_config_gui.show)

        self.initialize_console_widget()

        self.resize(914, 900)
        self.setWindowIcon(QtGui.QIcon(mdir + '/icons/main_icon.gif'))

        self._batch_manager = None

        self.ui.treeViewFlowcharts.setVisible(False)
        self.ui.labelProjectPlots.setVisible(False)
        self.ui.treeViewProjectPlots.setVisible(False)

        self.plot_windows = []

        self.flowcharts_dir = None
        self.plots_dir = None

        if not configuration.HAS_CAIMAN:
            QtWidgets.QMessageBox.information(
                self,
                'Caiman not found',
                'The caiman package could not be found in your python environment. '
                'Caiman features will not work.'
            )

        self.ui.action_version.setText(
            f"Version: {__version__}"
        )

    def initialize_console_widget(self):
        ns = {'configuration': configuration,
              'get_window_manager': get_window_manager,
              'this': self
              }

        txt = '\n'.join(["Namespaces:",
                         "self as this",
                         "callables:",
                         "get_window_manager()"])

        cmd_history_file = os.path.join(configuration.console_history_path, 'welcome_window.pik')
        console = ConsoleWidget(namespace=ns, text=txt, historyFile=cmd_history_file)

        self.ui.centralwidget.layout().addWidget(console)
        # self.ui.centralwidget.layout().addWidget(spacer)
        # self.ui.dockConsole.setWidget(console)

        # self.resizeDocks([self.ui.dockConsole], [235], QtCore.Qt.Vertical)
        # console.resize(self.ui.dockConsole.width(), 100)
        # self.ui.dockConsole.resize(self.ui.dockConsole.width(), 150)
        # console.input.resize(console.input.width(), 80)

        # self.ui.dockConsole.hide()

    def append_recent_projects_list(self):
        sys_cfg = configuration.get_sys_config()
        if self.project_manager.root_dir in sys_cfg['recent_projects']:
            sys_cfg['recent_projects'].remove(self.project_manager.root_dir)
        sys_cfg['recent_projects'].insert(0, self.project_manager.root_dir)
        if len(sys_cfg['recent_projects']) > 10:
            sys_cfg['recent_projects'] = sys_cfg['recent_projects'][:10]

        configuration.save_sys_config(sys_cfg)

    @use_open_dir_dialog('Choose location for a new project')
    @present_exceptions('Could not create new project', 'The following error occurred while creating a new project')
    def create_new_project(self, path, *args):
        # path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a new project')
        # if path == '':
        #     return

        name, start = QtWidgets.QInputDialog.getText(self, '', 'Project Name:', QtWidgets.QLineEdit.Normal, '')

        if not re.match("^[A-Za-z0-9_-]*$", name):
            QtWidgets.QMessageBox.warning(self, 'Invalid Name', 'Project Name can only contain alphanumeric characters')
            return

        if start and name != '':
            # try:
            proj_dir = os.path.join(path, name)
            self.project_manager = get_project_manager()
            self.project_manager.set(proj_dir)
            self.project_manager.setup_new_project()
            # except Exception:
            #     QtWidgets.QMessageBox.warning(self, 'Error!',
            #                                   'Could not create a new project.\n' +
            #                                   traceback.format_exc())
            #     return
        else:
            return
        self.ui.actionProject_Configuration.setEnabled(True)
        self.ui.actionProject_Configuration.triggered.connect(self.project_manager.show_config_window)

        self.set_proj_buttons_visible(False)
        self.append_recent_projects_list()

        self.setWindowTitle(
            f'{self.windowTitle()}'
            f' - '
            f'{os.path.basename(self.project_manager.root_dir)}'
        )

        # self.initialize_project_browser()

    @use_open_dir_dialog('Select Project Directory', '')
    def open_project_dialog(self, path, *args):
        self.open_project(path)

    @present_exceptions('Cannot open project', 'The selected directory is probably not a valid Mesmerize Project.')
    def open_project(self, path: str):
        is_mesmerize_project(path)
        self.project_manager = get_project_manager()
        self.project_manager.set(project_root_dir=path)

        self.project_manager.open_project()

        self.ui.actionProject_Configuration.setEnabled(True)
        self.ui.actionProject_Configuration.triggered.connect(self.project_manager.show_config_window)

        self.set_proj_buttons_visible(False)

        pb = start.project_browser()
        pb.reload_all_tabs()
        self.append_recent_projects_list()

        self.setWindowTitle(
            f'{self.windowTitle()}'
            f' - '
            f'{os.path.basename(self.project_manager.root_dir)}'
        )

    def show_project_browser(self):
        get_window_manager().project_browser.show()

    def set_proj_buttons_visible(self, b: bool):
        self.ui.btnNewProject.setVisible(b)
        self.ui.labelNewProj.setVisible(b)
        self.ui.btnOpenProject.setVisible(b)
        self.ui.labelOpenProject.setVisible(b)

        # self.ui.listWidgetRecentProjects.setVisible(b)
        # self.ui.labelRecentProjects.setVisible(b)

        self.ui.btnProjectBrowser.setHidden(b)
        self.ui.labelProjectBrowser.setHidden(b)

        self.set_flowcharts_list()
        self.set_plots_list()

    def set_flowcharts_list(self):
        self.ui.labelRecentProjects.setText('Project flowcharts')
        self.ui.listWidgetRecentProjects.setVisible(False)
        self.ui.treeViewFlowcharts.setVisible(True)

        self.flowcharts_dir = os.path.join(self.project_manager.root_dir, 'flowcharts')
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.flowcharts_dir)
        model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files | QtCore.QDir.Dirs)
        self.ui.treeViewFlowcharts.setModel(model)
        self.ui.treeViewFlowcharts.setRootIndex(model.index(self.flowcharts_dir))
        self.ui.treeViewFlowcharts.setColumnHidden(1, True)
        self.ui.treeViewFlowcharts.setColumnHidden(2, True)
        self.ui.treeViewFlowcharts.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.ui.treeViewFlowcharts.doubleClicked.connect(lambda m_ix: self.open_new_flowchart(model.filePath(m_ix)))

    def set_plots_list(self):
        self.ui.labelProjectPlots.setVisible(True)
        self.ui.treeViewProjectPlots.setVisible(True)

        self.plots_dir = os.path.join(self.project_manager.root_dir, 'plots')

        model = QtWidgets.QFileSystemModel()
        model.setRootPath(self.plots_dir)
        model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files | QtCore.QDir.Dirs)
        self.ui.treeViewProjectPlots.setModel(model)
        self.ui.treeViewProjectPlots.setRootIndex(model.index(self.plots_dir))
        self.ui.treeViewProjectPlots.setColumnHidden(1, True)
        self.ui.treeViewProjectPlots.setColumnHidden(2, True)
        self.ui.treeViewProjectPlots.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.ui.treeViewProjectPlots.doubleClicked.connect(lambda m_ix: self.open_plot(model.filePath(m_ix)))

    @present_exceptions('Could not open plot', 'The selected file is probably not a valid plot file.\n'
                                               'The following error occurred:\n')
    def open_plot(self, filename: str):
        if not os.path.isfile(filename):
            return
        plot = open_plot_file(filename)
        self.plot_windows.append(plot)
        plot.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        plot.destroyed.connect(partial(self.plot_windows.remove, plot))
        plot.show()

    def open_new_viewer(self):
        w = get_window_manager().get_new_viewer_window()
        w.show()
        # start.viewer()

    def open_new_flowchart(self, filename: str = None):
        if filename is not None and not isinstance(filename, str):
            filename = None
        else:
            if not os.path.isfile(filename):
                return

        w = get_window_manager().get_new_flowchart(filename, parent=self)
        w.show()

    def get_batch_manager(self, run_batch: list = None, testing=False) -> BatchModuleGUI:
        if run_batch is not None:
            self._batch_manager = BatchModuleGUI(parent=None, run_batch=run_batch)
            self._batch_manager.show()
            return self._batch_manager

        elif self._batch_manager is None:
            if not testing:
                 QtWidgets.QMessageBox.information(None, 'No batch manager open', 'Choose a location for a new batch or create a new batch')

            self._batch_manager = BatchModuleGUI(parent=None, testing=testing)
            # self._batch_manager.show()
            return self._batch_manager
        else:
            return self._batch_manager
            # self._batch_manager.show()
            # self._batch_manager.show()

    def closeEvent(self, QCloseEvent):
        if QtWidgets.QMessageBox.warning(self, 'Close Application?',
                                         'Are you sure you want to close all Mesmerize windows?',
                                         QtWidgets.QMessageBox.Yes,
                                         QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            QCloseEvent.ignore()
        else:
            for w in QtWidgets.QApplication.topLevelWidgets():
                QCloseEvent.accept()
                w.close()
