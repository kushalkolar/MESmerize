# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/datapoint_tracer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DatapointTracer(object):
    def setupUi(self, DatapointTracer):
        DatapointTracer.setObjectName("DatapointTracer")
        DatapointTracer.resize(437, 547)
        self.verticalLayout = QtWidgets.QVBoxLayout(DatapointTracer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(DatapointTracer)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.labelUUID = QtWidgets.QLabel(DatapointTracer)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelUUID.setFont(font)
        self.labelUUID.setText("")
        self.labelUUID.setObjectName("labelUUID")
        self.horizontalLayout.addWidget(self.labelUUID)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = QtWidgets.QPushButton(DatapointTracer)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(DatapointTracer)
        QtCore.QMetaObject.connectSlotsByName(DatapointTracer)

    def retranslateUi(self, DatapointTracer):
        _translate = QtCore.QCoreApplication.translate
        DatapointTracer.setWindowTitle(_translate("DatapointTracer", "Form"))
        self.label.setText(_translate("DatapointTracer", "UUID:"))
        self.pushButton.setText(_translate("DatapointTracer", "Open in viewer"))

