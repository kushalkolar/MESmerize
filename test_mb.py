#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 03:11:43 2018

@author: kushal
"""
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

class QuestionBox(QtWidgets.QDialog):
    def __init__(self):
        super(QuestionBox, self).__init__()

        self.setWindowTitle('Show Correlation & PNR image or CNMFE')
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel()
        label.setText('Would you like to look at the correlation & PNR image or view the CNMFE output?')
        layout.addWidget(label)

        btnCP = QtWidgets.QPushButton()
        btnCP.setText('Corr PNR Img')
        layout.addWidget(btnCP)

        btnCNMFE = QtWidgets.QPushButton()
        btnCNMFE.setText('CNMFE')
        layout.addWidget(btnCNMFE)

        self.setLayout(layout)

app = QtWidgets.QApplication([])
mb = QuestionBox()
mb.show()
app.exec_()