#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from collections import UserList
from PyQt5 import QtCore, QtGui, QtWidgets
from . import start
from functools import partial
import os


mpath = os.path.abspath(__file__)
mdir = os.path.dirname(mpath)


class WindowManager:
    """"""
    def __init__(self):
        self.welcome_window = None
        self.project_browser = None
        self.viewers = WindowList('Viewer')
        self.flowcharts = WindowList('Flowchart')

    def get_batch_manager(self, run_batch: list = None) -> QtWidgets.QWidget:
        return self.welcome_window.get_batch_manager(run_batch)

    def get_project_browser(self):
        if self.project_browser is None:
            raise AttributeError('Project Browser is not running')
        return self.project_browser

    # def initalize(self):
        # self.project_browsers = WindowClass('Project Browser')

    def get_new_viewer_window(self):
        w = start.viewer()
        self.viewers.append(w)
        w.destroyed.connect(partial(self.viewers.remove_window, w))
        return w

    def get_new_flowchart(self, filename: str = None, parent = None):
        w = start.flowchart(filename, parent)
        self.flowcharts.append(w)
        w.destroyed.connect(partial(self.flowcharts.remove_window, w))
        return w


class WindowList(UserList):
    """Simple management of the main windows of a certain type
     and the associated windows list widget on the welcome window"""
    def __init__(self, window_name: str):
        super(WindowList, self).__init__()
        self.window_name = window_name
        # self._selected_window = None
        #
        # self.list_widget = QtWidgets.QListWidget()
        # self.list_widget.itemDoubleClicked.connect(self._show_window)
        # self.list_widget.currentItemChanged.connect(self._set_selected_window)
        # self.list_widget.setToolTip('Double click to show window')
        #
        # action_delete_column = QtWidgets.QWidgetAction(self)
        # action_delete_column.setText('Delete column')
        # action_delete_column.triggered.connect(self.delete_column)

    def append(self, window: QtWidgets.QMainWindow):
        # self.list_widget.addItem(str(self.__len__() + 1))
        window.setWindowTitle('{} - {}'.format(self.window_name, self.__len__() + 1))
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        window.setWindowIcon(QtGui.QIcon(mdir + '/icons/main_icon.gif'))
        super(WindowList, self).append(window)

    # def _get_selected_window(self) -> QtWidgets.QMainWindow:
    #     return self._selected_window

    # def _set_selected_window(self):
        # i = self.list_widget.currentRow()
        # self._selected_window = self.__getitem__(i)

    # def _show_window(self):
    #     self._selected_window.show()

    def remove_window(self, window: QtWidgets.QMainWindow):
        self.data.remove(window)
        for ix, window in enumerate(self.data):
            window.setWindowTitle('{} - {}'.format(self.window_name, ix + 1))

    #
    # def __getitem__(self, item) -> QtWidgets.QMainWindow:
    #     return super(WindowClass, self).__getitem__(item)


