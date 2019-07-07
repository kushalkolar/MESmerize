#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from PyQt5 import QtCore, QtWidgets


class ListWidgetDialog(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.label = QtWidgets.QLabel()
        self.vertical_layout.addWidget(self.label)

        self.listWidget = QtWidgets.QListWidget()
        self.vertical_layout.addWidget(self.listWidget)

        self.btnCancel = QtWidgets.QPushButton()
        self.btnCancel.setText('Cancel')
        self.vertical_layout.addWidget(self.btnCancel)

        self.btnOK = QtWidgets.QPushButton()
        self.btnOK.setText('OK')
        self.vertical_layout.addWidget(self.btnOK)
        self.show()
        self.resize(400, 300)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    lwd = ListWidgetDialog()
    lw = QtWidgets.QListWidget()
    lwd.insert_list_widget(lw)


    app.exec_()