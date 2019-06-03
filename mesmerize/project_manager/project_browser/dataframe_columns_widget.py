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
from .column_widget import ColumnWidget


class DataFrameColumnsWidget(QtWidgets.QWidget):
    # signal_filter_requested = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        # self.tab_name = tab_name

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.scrollAreaWidgetContents = QtWidgets.QWidget()

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

    def add_column(self, column_widget: ColumnWidget):
        # column_widget.signal_apply_clicked.connect(self.filter_requested)
        self.horizontalLayout.addWidget(column_widget)

    def add_horizontal_spacer(self):
        spacer = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacer)

    # @QtCore.pyqtSlot(dict)
    # def filter_requested(self, d):
    #     self.signal_filter_requested.emit(d)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = DataFrameColumnsWidget(parent=None, tab_name='bah', filter_history='')

    cols = []
    for i in range(0,12):
        cols.append(ColumnWidget(parent=w, tab_name=w.tab_name, column_name='', column_type=str))
        w.add_column(cols[-1])
    w.resize(min(len(cols) * 215, 1920), 400)
    w.show()
    app.exec_()