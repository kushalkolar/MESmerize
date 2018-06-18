#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 17 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .tab_area_widget import TabAreaWidget
import pandas as pd
from common import configuration


class ProjectBrowserGUI(QtWidgets.QWidget):
    def __init__(self, parent, dataframe: pd.DataFrame):
        QtWidgets.QWidget.__init__(self)

        self.tabs = {}
        self.dataframe = dataframe

        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.tab_widget = QtWidgets.QTabWidget()
        self.vertical_layout.addWidget(self.tab_widget)

        self.add_tab(dataframe, '', is_root=True)

        self.tab_widget.tabCloseRequested.connect(self.close_tab)

    def add_tab(self, dataframe, filter_history, is_root=False):
        if not is_root:
            tab_name = QtWidgets.QInputDialog.getText(self, None, 'Enter name for new tab: ')
            if tab_name[0] == '' or tab_name[1] is False:
                return
            elif tab_name[0] in configuration.df_refs.keys():
                QtWidgets.QMessageBox.warning(self, 'DataFrame title already exists!',
                                              'That name already exists in your project, choose a different name!')
                self.add_tab(dataframe, filter_history, is_root)
        else:
            tab_name = 'root'

        tab_area_widget = TabAreaWidget(self.tab_widget, tab_name, dataframe, filter_history, is_root)

        self.tab_widget.addTab(tab_area_widget, tab_name)

        self.tab_widget.setTabsClosable(True)
        bar = self.tab_widget.tabBar()
        bar.setTabButton(0, bar.RightSide, None)

        self.tabs.update({tab_name: tab_area_widget})

        if is_root:
            num_columns = len(tab_area_widget.columns)
            self.resize(min(1920, num_columns * 215), 400)

    @QtCore.pyqtSlot(pd.DataFrame, list)
    def new_tab_requested(self, dataframe, filter_history):
        self.add_tab(dataframe, filter_history)

    def close_tab(self, ix):
        pass

