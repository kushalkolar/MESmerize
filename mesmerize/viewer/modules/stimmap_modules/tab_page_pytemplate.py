# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab_page.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TabPage(object):
    def setupUi(self, TabPage):
        TabPage.setObjectName("TabPage")
        TabPage.resize(589, 371)
        self.gridLayout = QtWidgets.QGridLayout(TabPage)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(482, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.btnAddRow = QtWidgets.QPushButton(TabPage)
        self.btnAddRow.setObjectName("btnAddRow")
        self.gridLayout.addWidget(self.btnAddRow, 1, 3, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(TabPage)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 573, 315))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 4)
        self.comboBoxTimeUnits = QtWidgets.QComboBox(TabPage)
        self.comboBoxTimeUnits.setEnabled(False)
        self.comboBoxTimeUnits.setObjectName("comboBoxTimeUnits")
        self.comboBoxTimeUnits.addItem("")
        self.comboBoxTimeUnits.addItem("")
        self.gridLayout.addWidget(self.comboBoxTimeUnits, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(TabPage)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 1, 1, 1)

        self.retranslateUi(TabPage)
        QtCore.QMetaObject.connectSlotsByName(TabPage)

    def retranslateUi(self, TabPage):
        _translate = QtCore.QCoreApplication.translate
        TabPage.setWindowTitle(_translate("TabPage", "Form"))
        self.btnAddRow.setText(_translate("TabPage", "Add Row"))
        self.comboBoxTimeUnits.setItemText(0, _translate("TabPage", "frames"))
        self.comboBoxTimeUnits.setItemText(1, _translate("TabPage", "seconds"))
        self.label.setText(_translate("TabPage", "units: "))

