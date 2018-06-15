#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from PyQt5 import QtCore, QtGui, QtWidgets


class ListWidgetDialog(QtWidgets.QWidget):
    def __init__(self):
        super(ListWidgetDialog, self).__init__()

        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel()
        layout.addWidget(self.label)

        self.listWidget = QtWidgets.QListWidget()
        layout.addWidget(self.label)

        self.btnCancel = QtWidgets.QPushButton()
        self.btnCancel.setText('Cancel')
        layout.addWidget(self.btnCancel)

        self.btnOK = QtWidgets.QPushButton()
        self.btnOK.setText('OK')
        layout.addWidget(self.btnOK)
