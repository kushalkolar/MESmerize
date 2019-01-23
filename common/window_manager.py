#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007


"""

from PyQt5 import QtCore, QtGui, QtWidgets


class WindowManager:
    """"""
    def __init__(self):
        pass

    def get_batch_manager(self):
        self._welcome_window.get_batch_manager()

    def show_project_browser(self, i: int):
        self.project_browsers[i].show()

    def initalize(self):
        self._welcome_window = None

        # self.project_browsers = None
        # self.viewers = None
        # self.flowcharts = None
        # self.plots = None
        # self.clustering_windows = None

        self.project_browsers = WindowClass('Project Browser')
        self.viewers = WindowClass('Viewer')
        self.flowcharts = WindowClass('Flowchart')
        self.plots = WindowClass('Plots')
        self.clustering_windows = WindowClass('Clustering')

    def garbage_collect(self):
        pass

    def garbage_collect_all_closed_windows(self):
        pass


class WindowClass(list):
    """Simple management of the main windows of a certain type
     and the associated windows list widget on the welcome window"""
    def __init__(self, window_name: str):
        super(WindowClass, self).__init__()
        self.window_name = window_name
        self._selected_window = None

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._show_window)
        self.list_widget.currentItemChanged.connect(self.set_selected_window)
        self.list_widget.setToolTip('Double click to show window')

    def append(self, window: QtWidgets.QMainWindow):
        self.list_widget.addItem(str(self.__len__()))
        window.setWindowTitle('Mesmerize - ' + self.window_name + ' - ' + str(self.__len__()))
        super(WindowClass, self).append(window)

    def get_selected_window(self) -> QtWidgets.QMainWindow:
        return self._selected_window

    def set_selected_window(self, item: QtWidgets.QListWidgetItem):
        i = int(item.data(0))
        self._selected_window = self.__getitem__(i)

    def _show_window(self):
        self._selected_window.show()

    def __delitem__(self, key):
        window = self.__getitem__(key)
        window.deleteLater()
        super(WindowClass, self).__delitem__(key)

    def __getitem__(self, item) -> QtWidgets.QMainWindow:
        return super(WindowClass, self).__getitem__(item)
