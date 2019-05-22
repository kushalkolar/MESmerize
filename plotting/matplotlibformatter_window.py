# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'matplotlibformatter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(680, 316)
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_xylabels = QtWidgets.QGroupBox(Form)
        self.groupBox_xylabels.setObjectName("groupBox_xylabels")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_xylabels)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(self.groupBox_xylabels)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.listWidget_xlabels_edit = QtWidgets.QListWidget(self.groupBox_xylabels)
        self.listWidget_xlabels_edit.setObjectName("listWidget_xlabels_edit")
        self.gridLayout.addWidget(self.listWidget_xlabels_edit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_xylabels)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_xylabels)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 1, 1, 1)
        self.listWidget_xlabels_orig = QtWidgets.QListWidget(self.groupBox_xylabels)
        self.listWidget_xlabels_orig.setObjectName("listWidget_xlabels_orig")
        self.gridLayout.addWidget(self.listWidget_xlabels_orig, 1, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_xylabels)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.listWidget_ylabels_orig = QtWidgets.QListWidget(self.groupBox_xylabels)
        self.listWidget_ylabels_orig.setObjectName("listWidget_ylabels_orig")
        self.gridLayout.addWidget(self.listWidget_ylabels_orig, 3, 0, 1, 1)
        self.listWidget_ylabels_edit = QtWidgets.QListWidget(self.groupBox_xylabels)
        self.listWidget_ylabels_edit.setObjectName("listWidget_ylabels_edit")
        self.gridLayout.addWidget(self.listWidget_ylabels_edit, 3, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_xylabels)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 4, 0, 1, 2)
        self.gridLayout_3.addWidget(self.groupBox_xylabels, 0, 0, 1, 1)
        self.groupBox_xticklabels = QtWidgets.QGroupBox(Form)
        self.groupBox_xticklabels.setObjectName("groupBox_xticklabels")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_xticklabels)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_xticklabels)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)
        self.listWidget_xticklabels_orig = QtWidgets.QListWidget(self.groupBox_xticklabels)
        self.listWidget_xticklabels_orig.setObjectName("listWidget_xticklabels_orig")
        self.gridLayout_2.addWidget(self.listWidget_xticklabels_orig, 1, 0, 1, 1)
        self.listWidget_xticklabels_edit = QtWidgets.QListWidget(self.groupBox_xticklabels)
        self.listWidget_xticklabels_edit.setObjectName("listWidget_xticklabels_edit")
        self.gridLayout_2.addWidget(self.listWidget_xticklabels_edit, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_xticklabels)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_xticklabels, 0, 1, 1, 1)
        self.pushButton_Apply = QtWidgets.QPushButton(Form)
        self.pushButton_Apply.setObjectName("pushButton_Apply")
        self.gridLayout_3.addWidget(self.pushButton_Apply, 1, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox_xylabels.setTitle(_translate("Form", "XY Labels"))
        self.label_5.setText(_translate("Form", "Original Y-label"))
        self.label_3.setText(_translate("Form", "Original X-label "))
        self.label_6.setText(_translate("Form", "User-defined Y-label"))
        self.label_4.setText(_translate("Form", "User-defined X-label"))
        self.checkBox.setText(_translate("Form", "CheckBox"))
        self.groupBox_xticklabels.setTitle(_translate("Form", "Tick Labels"))
        self.label_2.setText(_translate("Form", "User-defined"))
        self.listWidget_xticklabels_edit.setToolTip(_translate("Form", "<html><head/><body><p>double-click to edit.</p></body></html>"))
        self.label.setText(_translate("Form", "Original"))
        self.pushButton_Apply.setText(_translate("Form", "Apply Changes"))


