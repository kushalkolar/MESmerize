# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        MainWidget.setObjectName("MainWidget")
        MainWidget.resize(607, 500)
        MainWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 5)
        self.btnImport = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnImport.setObjectName("btnImport")
        self.gridLayout.addWidget(self.btnImport, 1, 0, 1, 1)
        self.btnExport = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnExport.setObjectName("btnExport")
        self.gridLayout.addWidget(self.btnExport, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(242, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.btnCancel = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnCancel.setObjectName("btnCancel")
        self.gridLayout.addWidget(self.btnCancel, 1, 3, 1, 1)
        self.btnSetAllMaps = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSetAllMaps.setObjectName("btnSetAllMaps")
        self.gridLayout.addWidget(self.btnSetAllMaps, 1, 4, 1, 1)
        MainWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(MainWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("MainWidget", "Stimulus Mapping"))
        self.btnImport.setText(_translate("MainWidget", "Import"))
        self.btnExport.setText(_translate("MainWidget", "Export"))
        self.btnCancel.setText(_translate("MainWidget", "Cancel"))
        self.btnSetAllMaps.setText(_translate("MainWidget", "Set all maps"))

