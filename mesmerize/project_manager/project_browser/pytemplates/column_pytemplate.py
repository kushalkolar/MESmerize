# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/column_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_column_template(object):
    def setupUi(self, column_template):
        column_template.setObjectName("column_template")
        column_template.resize(200, 402)
        column_template.setMinimumSize(QtCore.QSize(200, 0))
        column_template.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gridLayout = QtWidgets.QGridLayout(column_template)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelColumnName = QtWidgets.QLabel(column_template)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelColumnName.sizePolicy().hasHeightForWidth())
        self.labelColumnName.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelColumnName.setFont(font)
        self.labelColumnName.setText("")
        self.labelColumnName.setObjectName("labelColumnName")
        self.verticalLayout.addWidget(self.labelColumnName)
        self.listWidget = QtWidgets.QListWidget(column_template)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.lineEdit = QtWidgets.QLineEdit(column_template)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(67, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnReset = QtWidgets.QPushButton(column_template)
        self.btnReset.setMinimumSize(QtCore.QSize(50, 26))
        self.btnReset.setMaximumSize(QtCore.QSize(50, 26))
        self.btnReset.setObjectName("btnReset")
        self.gridLayout.addWidget(self.btnReset, 1, 1, 1, 1)
        self.btnApply = QtWidgets.QPushButton(column_template)
        self.btnApply.setMinimumSize(QtCore.QSize(50, 26))
        self.btnApply.setMaximumSize(QtCore.QSize(50, 26))
        self.btnApply.setObjectName("btnApply")
        self.gridLayout.addWidget(self.btnApply, 1, 2, 1, 1)

        self.retranslateUi(column_template)
        QtCore.QMetaObject.connectSlotsByName(column_template)

    def retranslateUi(self, column_template):
        _translate = QtCore.QCoreApplication.translate
        column_template.setWindowTitle(_translate("column_template", "Form"))
        self.lineEdit.setPlaceholderText(_translate("column_template", "Filter"))
        self.btnReset.setText(_translate("column_template", "Reset"))
        self.btnApply.setText(_translate("column_template", "Apply"))

