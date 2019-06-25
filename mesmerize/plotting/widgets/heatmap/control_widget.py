# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'control_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ControlWidget(object):
    def setupUi(self, ControlWidget):
        ControlWidget.setObjectName("ControlWidget")
        ControlWidget.resize(301, 679)
        self.verticalLayout = QtWidgets.QVBoxLayout(ControlWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(ControlWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.comboBoxDataColumn = QtWidgets.QComboBox(ControlWidget)
        self.comboBoxDataColumn.setObjectName("comboBoxDataColumn")
        self.verticalLayout.addWidget(self.comboBoxDataColumn)
        self.label_3 = QtWidgets.QLabel(ControlWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.comboBoxLabelsColumn = QtWidgets.QComboBox(ControlWidget)
        self.comboBoxLabelsColumn.setObjectName("comboBoxLabelsColumn")
        self.verticalLayout.addWidget(self.comboBoxLabelsColumn)
        self.label_5 = QtWidgets.QLabel(ControlWidget)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.comboBoxDPTCurveColumn = QtWidgets.QComboBox(ControlWidget)
        self.comboBoxDPTCurveColumn.setObjectName("comboBoxDPTCurveColumn")
        self.verticalLayout.addWidget(self.comboBoxDPTCurveColumn)
        self.label = QtWidgets.QLabel(ControlWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidgetColorMaps = ColormapListWidget(ControlWidget)
        self.listWidgetColorMaps.setObjectName("listWidgetColorMaps")
        self.verticalLayout.addWidget(self.listWidgetColorMaps)
        self.pushButtonPlot = QtWidgets.QPushButton(ControlWidget)
        self.pushButtonPlot.setMinimumSize(QtCore.QSize(0, 46))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonPlot.setFont(font)
        self.pushButtonPlot.setCheckable(True)
        self.pushButtonPlot.setObjectName("pushButtonPlot")
        self.verticalLayout.addWidget(self.pushButtonPlot)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonSave = QtWidgets.QPushButton(ControlWidget)
        self.pushButtonSave.setMinimumSize(QtCore.QSize(0, 46))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonSave.setFont(font)
        self.pushButtonSave.setCheckable(False)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.horizontalLayout.addWidget(self.pushButtonSave)
        self.pushButtonLoad = QtWidgets.QPushButton(ControlWidget)
        self.pushButtonLoad.setMinimumSize(QtCore.QSize(0, 46))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonLoad.setFont(font)
        self.pushButtonLoad.setCheckable(False)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        self.horizontalLayout.addWidget(self.pushButtonLoad)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.checkBoxShowStimuli = QtWidgets.QCheckBox(ControlWidget)
        self.checkBoxShowStimuli.setObjectName("checkBoxShowStimuli")
        self.verticalLayout.addWidget(self.checkBoxShowStimuli)

        self.retranslateUi(ControlWidget)
        QtCore.QMetaObject.connectSlotsByName(ControlWidget)

    def retranslateUi(self, ControlWidget):
        _translate = QtCore.QCoreApplication.translate
        ControlWidget.setWindowTitle(_translate("ControlWidget", "Form"))
        self.label_2.setText(_translate("ControlWidget", "Data columns"))
        self.label_3.setText(_translate("ControlWidget", "Labels column"))
        self.label_5.setText(_translate("ControlWidget", "DPT curve column"))
        self.label.setText(_translate("ControlWidget", "Colormap:"))
        self.pushButtonPlot.setText(_translate("ControlWidget", "Plot with live updates"))
        self.pushButtonSave.setText(_translate("ControlWidget", "Save"))
        self.pushButtonLoad.setText(_translate("ControlWidget", "Load"))
        self.checkBoxShowStimuli.setText(_translate("ControlWidget", "Show Stimuli"))

from ...utils import ColormapListWidget
