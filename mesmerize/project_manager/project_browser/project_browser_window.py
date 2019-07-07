#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 18 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .main_widget import ProjectBrowserWidget
from ...pyqtgraphCore.console import ConsoleWidget
from .pytemplates.mainwindow_pytemplate import Ui_MainWindow
from spyder.widgets.variableexplorer import objecteditor
import pandas as pd
import os
from ...common import configuration, get_project_manager
from functools import partial


class ProjectBrowserWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.project_browser = ProjectBrowserWidget(self, get_project_manager().dataframe)
        self.current_tab = 0
        self.project_browser.tab_widget.currentChanged.connect(self.set_current_tab)
        self.setCentralWidget(self.project_browser)

        self.ui.actionto_pickle.triggered.connect(partial(self.save_path_dialog, file_ext='pikl', save_root=True))
        self.ui.actionto_csv.triggered.connect(partial(self.save_path_dialog, file_ext='csv', save_root=True))
        self.ui.actionto_excel.triggered.connect(partial(self.save_path_dialog, file_ext='xlsx', save_root=True))

        self.ui.actionto_pickle_tab.triggered.connect(partial(self.save_path_dialog, file_ext='pikl', save_root=False))
        self.ui.actionto_csv_tab.triggered.connect(partial(self.save_path_dialog, file_ext='csv', save_root=False))
        self.ui.actionto_excel_tab.triggered.connect(partial(self.save_path_dialog, file_ext='xlsx', save_root=False))

        self.ui.actionDataframe_editor.triggered.connect(self.edit_root_dataframe)

        self.ui.actionViewCurrent_dataframe.triggered.connect(self.view_current_dataframe)
        self.ui.actionCurrent_tab_filter_history.triggered.connect(self.view_filters)

        self.ui.actionUpdate_current_tab.triggered.connect(self.update_tab_from_child_dataframe)
        self.ui.actionUpdate_all_tabs.triggered.connect(self.update_tabs_from_child_dataframes)

        self.ui.actionSave_to_project.triggered.connect(self._save_dataframe)

        ns = {'pd': pd,
              'project_browser': self.project_browser,
              'this': self,
              'get_dataframe': lambda: self.get_current_dataframe()[0],
              'get_root_dataframe': lambda: self.get_current_dataframe(get_root=True)[0],
              'set_root_dataframe': lambda df: get_project_manager().set_dataframe(df)
              }

        txt = "Namespaces:          \n" \
              "pandas as pd         \n" \
              "Useful callables:\n" \
              "get_dataframe() - returns dataframe of the current tab\n" \
              "get_root_dataframe() - always return dataframe of root tab (i.e. entire dataframe)\n" \
              "set_root_dataframe() - save the root dataframe\n" \
              "self as this         \n" \

        cmd_history_file = os.path.join(configuration.console_history_path, 'project_browser.pik')

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt, historyFile=cmd_history_file))
        # self.resizeDocks([self.ui.dockConsole], [235], QtCore.Qt.Vertical)
        self.ui.dockConsole.hide()

        self._status_bar = None
        self.status_bar = self.statusBar()

        self.setWindowTitle('Project Browser')

    @property
    def status_bar(self) -> QtWidgets.QStatusBar:
        return self._status_bar

    @status_bar.setter
    def status_bar(self, status_bar: QtWidgets.QStatusBar):
        self._status_bar = status_bar

    def set_current_tab(self, ix: int):
        self.current_tab = ix

    def save_path_dialog(self, file_ext: str, save_root=False):
        path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save DataFrame as', '', f'(*.{file_ext})')
        if path == '':
            return
        if path[0].endswith('.' + file_ext):
            path = path[0]
        else:
            path = path[0] + '.' + file_ext

        if file_ext == 'pikl':
            self.get_current_dataframe(get_root=save_root)[0].to_pickle(path, protocol=4)
        elif file_ext == 'csv':
            self.get_current_dataframe(get_root=save_root)[0].to_csv(path)
        elif file_ext == '.xlsx':
            self.get_current_dataframe(get_root=save_root)[0].to_excel(path)

    def get_current_dataframe(self, get_root=False) -> (pd.DataFrame, list):
        if self.current_tab == 0 or get_root:
            dataframe = get_project_manager().get_dataframe()
            return dataframe, []
        else:
            tab_name = self.project_browser.tab_widget.widget(self.current_tab).tab_name
            child = get_project_manager().child_dataframes[tab_name]
        return child['dataframe'], child['filter_history']

    def _save_dataframe(self):
        get_project_manager().save_dataframe()

    def edit_root_dataframe(self):
        QtWidgets.QMessageBox.warning(self, 'Proceed with caution!',
                                      'You are about to edit the project DataFrame, be careful!\n'
                                      'If you make a mistake press "Close"')

        df = objecteditor.oedit(get_project_manager().get_dataframe())
        if df is not None:
            get_project_manager().set_dataframe(df)

    def view_current_dataframe(self):
        objecteditor.oedit(self.get_current_dataframe()[0])

    def view_filters(self):
        filters = self.get_current_dataframe()[1]

        QtWidgets.QMessageBox.information(self, 'Filters for current tab', '\n'.join(filters))

    def reload_all_tabs(self):
        self.status_bar.showMessage('Please wait, loading tabs...')
        for i in range(1, self.project_browser.tab_widget.count()):
            self.project_browser.tab_widget.removeTab(i)

        # for child in configuration.project_manager.child_dataframes.keys():
        #     configuration.project_manager.child_dataframes.pop(child)

        get_project_manager().create_sub_dataframe()

        for child in get_project_manager().child_dataframes.keys():
            dataframe = get_project_manager().child_dataframes[child]['dataframe']
            filter_history = get_project_manager().child_dataframes[child]['filter_history']
            self.project_browser.add_tab(dataframe, filter_history, name=child)
        self.status_bar.showMessage('Finished loading tabs!')

    def update_tab_from_child_dataframe(self, tab_name=None):
        if tab_name is None:
            tab_name = self.project_browser.tab_widget.widget(self.current_tab).tab_name

        child = get_project_manager().child_dataframes[tab_name]
        dataframe = child['dataframe']
        filter_history = child['filter_history']
        self.project_browser.tabs[tab_name].dataframe = dataframe
        self.project_browser.tabs[tab_name].filter_history = filter_history
        self.project_browser.tabs[tab_name].populate_tab()

    def update_tabs_from_child_dataframes(self):
        for tab_name in self.project_browser.tabs.keys():
            if tab_name == 'root':
                continue
            self.update_tab_from_child_dataframe(tab_name)
