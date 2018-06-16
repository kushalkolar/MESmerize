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
    def __init__(self):
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
    def __init__(self, window_name: str):
        super(WindowClass, self).__init__()
        self.window_name = window_name
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._show_window)

    def append(self, QMainWindow: QtWidgets.QMainWindow):
        self.list_widget.addItem(str(self.__len__()))
        QMainWindow.setWindowTitle('Mesmerize - ' + self.window_name + ' - ' + str(self.__len__()))
        super(WindowClass, self).append(QMainWindow)

    def __delitem__(self, key):
        window = self.__getitem__(key)
        window.deleteLater()
        super(WindowClass, self).__delitem__(key)

    def _show_window(self, item: QtWidgets.QListWidgetItem):
        i = int(item.data(0))
        window = self.__getitem__(i)
        window.show()

    def __getitem__(self, item) -> QtWidgets.QMainWindow:
        return super(WindowClass, self).__getitem__(item)
