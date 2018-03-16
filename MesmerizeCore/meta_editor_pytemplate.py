# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'meta_editor_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_meta_editor_template(object):
    def setupUi(self, meta_editor_template):
        meta_editor_template.setObjectName("meta_editor_template")
        meta_editor_template.resize(248, 133)
        self.gridLayout = QtWidgets.QGridLayout(meta_editor_template)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdHHMMSS = QtWidgets.QLineEdit(meta_editor_template)
        self.lineEdHHMMSS.setMaxLength(6)
        self.lineEdHHMMSS.setObjectName("lineEdHHMMSS")
        self.gridLayout.addWidget(self.lineEdHHMMSS, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(meta_editor_template)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(meta_editor_template)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)
        self.btnSave = QtWidgets.QPushButton(meta_editor_template)
        self.btnSave.setObjectName("btnSave")
        self.gridLayout.addWidget(self.btnSave, 3, 3, 1, 1)
        self.doubleSpinFPS = QtWidgets.QDoubleSpinBox(meta_editor_template)
        self.doubleSpinFPS.setDecimals(4)
        self.doubleSpinFPS.setMaximum(999.99)
        self.doubleSpinFPS.setObjectName("doubleSpinFPS")
        self.gridLayout.addWidget(self.doubleSpinFPS, 0, 1, 1, 3)
        self.label_2 = QtWidgets.QLabel(meta_editor_template)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEdYYYYMMDDD = QtWidgets.QLineEdit(meta_editor_template)
        self.lineEdYYYYMMDDD.setMaxLength(8)
        self.lineEdYYYYMMDDD.setObjectName("lineEdYYYYMMDDD")
        self.gridLayout.addWidget(self.lineEdYYYYMMDDD, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(meta_editor_template)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(meta_editor_template)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)

        self.retranslateUi(meta_editor_template)
        QtCore.QMetaObject.connectSlotsByName(meta_editor_template)

    def retranslateUi(self, meta_editor_template):
        _translate = QtCore.QCoreApplication.translate
        meta_editor_template.setWindowTitle(_translate("meta_editor_template", "Form"))
        self.lineEdHHMMSS.setPlaceholderText(_translate("meta_editor_template", "hhmmss"))
        self.label.setText(_translate("meta_editor_template", "fps"))
        self.label_3.setText(_translate("meta_editor_template", "-"))
        self.btnSave.setText(_translate("meta_editor_template", "Save"))
        self.label_2.setText(_translate("meta_editor_template", "date"))
        self.lineEdYYYYMMDDD.setPlaceholderText(_translate("meta_editor_template", "yyyymmdd"))
        self.label_4.setText(_translate("meta_editor_template", "YYYYMMDD"))
        self.label_5.setText(_translate("meta_editor_template", "HHMMSS"))

