# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FlowchartCtrlTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(270, 499)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 2, 0, 2)
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.fileNameLabel = QtWidgets.QLabel(Form)
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.verticalLayout.addWidget(self.fileNameLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loadBtn = QtWidgets.QPushButton(Form)
        self.loadBtn.setObjectName("loadBtn")
        self.horizontalLayout.addWidget(self.loadBtn)
        self.saveBtn = FeedbackButton(Form)
        self.saveBtn.setObjectName("saveBtn")
        self.horizontalLayout.addWidget(self.saveBtn)
        self.saveAsBtn = FeedbackButton(Form)
        self.saveAsBtn.setObjectName("saveAsBtn")
        self.horizontalLayout.addWidget(self.saveAsBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.ctrlList = TreeWidget(Form)
        self.ctrlList.setObjectName("ctrlList")
        self.ctrlList.headerItem().setText(0, "1")
        self.ctrlList.header().setVisible(False)
        self.ctrlList.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.ctrlList)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.reloadBtn = FeedbackButton(Form)
        self.reloadBtn.setEnabled(False)
        self.reloadBtn.setCheckable(False)
        self.reloadBtn.setFlat(False)
        self.reloadBtn.setObjectName("reloadBtn")
        self.horizontalLayout_2.addWidget(self.reloadBtn)
        self.showChartBtn = QtWidgets.QPushButton(Form)
        self.showChartBtn.setCheckable(True)
        self.showChartBtn.setObjectName("showChartBtn")
        self.horizontalLayout_2.addWidget(self.showChartBtn)
        self.BtnResetView = QtWidgets.QPushButton(Form)
        self.BtnResetView.setObjectName("BtnResetView")
        self.horizontalLayout_2.addWidget(self.BtnResetView)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.fileNameLabel.setText(_translate("Form", "Unsaved"))
        self.loadBtn.setText(_translate("Form", "Load.."))
        self.saveBtn.setText(_translate("Form", "Save"))
        self.saveAsBtn.setText(_translate("Form", "Save As.."))
        self.reloadBtn.setText(_translate("Form", "Reload Libs"))
        self.showChartBtn.setText(_translate("Form", "Flowchart"))
        self.BtnResetView.setText(_translate("Form", "Reset view"))

from ..widgets.FeedbackButton import FeedbackButton
from ..widgets.TreeWidget import TreeWidget
