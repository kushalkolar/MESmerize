# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferences_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(297, 79)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBoxThreads = QtWidgets.QSpinBox(Form)
        self.spinBoxThreads.setMinimum(1)
        self.spinBoxThreads.setMaximum(999)
        self.spinBoxThreads.setObjectName("spinBoxThreads")
        self.horizontalLayout.addWidget(self.spinBoxThreads)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.btnClose = QtWidgets.QPushButton(Form)
        self.btnClose.setObjectName("btnClose")
        self.gridLayout.addWidget(self.btnClose, 1, 0, 1, 1)
        self.btnApply = QtWidgets.QPushButton(Form)
        self.btnApply.setObjectName("btnApply")
        self.gridLayout.addWidget(self.btnApply, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Maximum number of threads to use:"))
        self.btnClose.setText(_translate("Form", "Close"))
        self.btnApply.setText(_translate("Form", "Apply"))

