# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'link_viewers_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(204, 320)
        self.listWidgetSource = QtWidgets.QListWidget(Form)
        self.listWidgetSource.setGeometry(QtCore.QRect(10, 30, 61, 221))
        self.listWidgetSource.setObjectName("listWidgetSource")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 10, 41, 18))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(130, 10, 58, 18))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.listWidgetReceivers = QtWidgets.QListWidget(Form)
        self.listWidgetReceivers.setGeometry(QtCore.QRect(130, 30, 61, 221))
        self.listWidgetReceivers.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetReceivers.setObjectName("listWidgetReceivers")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(70, 100, 61, 71))
        font = QtGui.QFont()
        font.setPointSize(52)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.btnSet = QtWidgets.QPushButton(Form)
        self.btnSet.setGeometry(QtCore.QRect(110, 280, 80, 26))
        self.btnSet.setObjectName("btnSet")
        self.btnDisconnect = QtWidgets.QPushButton(Form)
        self.btnDisconnect.setGeometry(QtCore.QRect(10, 280, 80, 26))
        self.btnDisconnect.setObjectName("btnDisconnect")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Source"))
        self.label_2.setText(_translate("Form", "Receivers"))
        self.label_3.setText(_translate("Form", "→"))
        self.btnSet.setText(_translate("Form", "Set"))
        self.btnDisconnect.setText(_translate("Form", "Disconnect"))

