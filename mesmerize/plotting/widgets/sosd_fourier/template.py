# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './template.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1038, 533)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBoxControls = QtWidgets.QGroupBox(Form)
        self.groupBoxControls.setObjectName("groupBoxControls")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBoxControls)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBoxControls)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBoxDataColumn = QtWidgets.QComboBox(self.groupBoxControls)
        self.comboBoxDataColumn.setObjectName("comboBoxDataColumn")
        self.verticalLayout.addWidget(self.comboBoxDataColumn)
        self.pushButtonStart = QtWidgets.QPushButton(self.groupBoxControls)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.verticalLayout.addWidget(self.pushButtonStart)
        self.progressBar = QtWidgets.QProgressBar(self.groupBoxControls)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        spacerItem = QtWidgets.QSpacerItem(20, 336, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.groupBoxControls)
        self.groupBoxPlot = QtWidgets.QGroupBox(Form)
        self.groupBoxPlot.setObjectName("groupBoxPlot")
        self.horizontalLayout.addWidget(self.groupBoxPlot)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 7)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBoxControls.setTitle(_translate("Form", "Controls"))
        self.label.setText(_translate("Form", "Data column"))
        self.pushButtonStart.setText(_translate("Form", "Start"))
        self.groupBoxPlot.setTitle(_translate("Form", "Plot"))

