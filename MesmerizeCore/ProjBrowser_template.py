# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProjBrowser_template.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore import PlotWidget

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(708, 661)
        self.newProjBtn = QtWidgets.QPushButton(Form)
        self.newProjBtn.setGeometry(QtCore.QRect(20, 20, 80, 26))
        self.newProjBtn.setObjectName("newProjBtn")
        self.openProjBtn = QtWidgets.QPushButton(Form)
        self.openProjBtn.setGeometry(QtCore.QRect(110, 20, 80, 26))
        self.openProjBtn.setObjectName("openProjBtn")
        self.saveProjBtn = QtWidgets.QPushButton(Form)
        self.saveProjBtn.setGeometry(QtCore.QRect(200, 20, 80, 26))
        self.saveProjBtn.setObjectName("saveProjBtn")
        self.widget = PlotWidget(Form)
        self.widget.setGeometry(QtCore.QRect(70, 410, 611, 231))
        self.widget.setObjectName("widget")
        self.treeView = QtWidgets.QTreeView(Form)
        self.treeView.setGeometry(QtCore.QRect(10, 60, 451, 331))
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.treeView.setObjectName("treeView")
        self.openViewerBtn = QtWidgets.QPushButton(Form)
        self.openViewerBtn.setGeometry(QtCore.QRect(290, 20, 80, 26))
        self.openViewerBtn.setObjectName("openViewerBtn")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.newProjBtn.setText(_translate("Form", "New Project"))
        self.openProjBtn.setText(_translate("Form", "Open"))
        self.saveProjBtn.setText(_translate("Form", "Save"))
        self.openViewerBtn.setText(_translate("Form", "Open Viewer"))

