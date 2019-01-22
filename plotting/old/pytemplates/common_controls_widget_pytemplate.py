# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/common_controls_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommonControls(object):
    def setupUi(self, CommonControls):
        CommonControls.setObjectName("CommonControls")
        CommonControls.resize(279, 362)
        self.btnEditColor = QtWidgets.QPushButton(CommonControls)
        self.btnEditColor.setGeometry(QtCore.QRect(9, 323, 80, 26))
        self.btnEditColor.setObjectName("btnEditColor")
        self.label = QtWidgets.QLabel(CommonControls)
        self.label.setGeometry(QtCore.QRect(9, 9, 82, 18))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(CommonControls)
        self.label_2.setGeometry(QtCore.QRect(9, 231, 99, 18))
        self.label_2.setObjectName("label_2")
        self.layoutWidget = QtWidgets.QWidget(CommonControls)
        self.layoutWidget.setGeometry(QtCore.QRect(9, 289, 261, 28))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButtonGroupByTransmissions = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButtonGroupByTransmissions.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.radioButtonGroupByTransmissions.setObjectName("radioButtonGroupByTransmissions")
        self.horizontalLayout_2.addWidget(self.radioButtonGroupByTransmissions)
        self.btnSetIncomingTransmissionsNames = QtWidgets.QPushButton(self.layoutWidget)
        self.btnSetIncomingTransmissionsNames.setObjectName("btnSetIncomingTransmissionsNames")
        self.horizontalLayout_2.addWidget(self.btnSetIncomingTransmissionsNames)
        self.listWidgetDataColumns = QtWidgets.QListWidget(CommonControls)
        self.listWidgetDataColumns.setGeometry(QtCore.QRect(9, 33, 261, 192))
        self.listWidgetDataColumns.setAlternatingRowColors(True)
        self.listWidgetDataColumns.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidgetDataColumns.setObjectName("listWidgetDataColumns")
        self.layoutWidget_3 = QtWidgets.QWidget(CommonControls)
        self.layoutWidget_3.setGeometry(QtCore.QRect(9, 255, 261, 28))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButtonGroupBySingleColumn = QtWidgets.QRadioButton(self.layoutWidget_3)
        self.radioButtonGroupBySingleColumn.setMaximumSize(QtCore.QSize(16, 16777215))
        self.radioButtonGroupBySingleColumn.setText("")
        self.radioButtonGroupBySingleColumn.setObjectName("radioButtonGroupBySingleColumn")
        self.horizontalLayout.addWidget(self.radioButtonGroupBySingleColumn)
        self.comboBoxGrouping = QtWidgets.QComboBox(self.layoutWidget_3)
        self.comboBoxGrouping.setObjectName("comboBoxGrouping")
        self.horizontalLayout.addWidget(self.comboBoxGrouping)
        self.line = QtWidgets.QFrame(CommonControls)
        self.line.setGeometry(QtCore.QRect(10, 350, 261, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(CommonControls)
        QtCore.QMetaObject.connectSlotsByName(CommonControls)

    def retranslateUi(self, CommonControls):
        _translate = QtCore.QCoreApplication.translate
        CommonControls.setWindowTitle(_translate("CommonControls", "Form"))
        self.btnEditColor.setText(_translate("CommonControls", "Edit colors"))
        self.label.setText(_translate("CommonControls", "Data columns"))
        self.label_2.setText(_translate("CommonControls", "Group based on:"))
        self.radioButtonGroupByTransmissions.setText(_translate("CommonControls", "Incoming transmissions"))
        self.btnSetIncomingTransmissionsNames.setText(_translate("CommonControls", "Set Names"))

