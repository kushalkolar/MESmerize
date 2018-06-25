# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        MainWidget.setObjectName("MainWidget")
        MainWidget.resize(613, 476)
        self.gridLayout = QtWidgets.QGridLayout(MainWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.btnSetAllMaps = QtWidgets.QPushButton(MainWidget)
        self.btnSetAllMaps.setObjectName("btnSetAllMaps")
        self.gridLayout.addWidget(self.btnSetAllMaps, 2, 4, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(MainWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 5)
        self.btnImport = QtWidgets.QPushButton(MainWidget)
        self.btnImport.setObjectName("btnImport")
        self.gridLayout.addWidget(self.btnImport, 2, 0, 1, 1)
        self.btnCancel = QtWidgets.QPushButton(MainWidget)
        self.btnCancel.setObjectName("btnCancel")
        self.gridLayout.addWidget(self.btnCancel, 2, 3, 1, 1)
        self.btnExport = QtWidgets.QPushButton(MainWidget)
        self.btnExport.setObjectName("btnExport")
        self.gridLayout.addWidget(self.btnExport, 2, 1, 1, 1)

        self.retranslateUi(MainWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("MainWidget", "Form"))
        self.btnSetAllMaps.setText(_translate("MainWidget", "Set all maps"))
        self.btnImport.setText(_translate("MainWidget", "Import"))
        self.btnCancel.setText(_translate("MainWidget", "Cancel"))
        self.btnExport.setText(_translate("MainWidget", "Export"))

