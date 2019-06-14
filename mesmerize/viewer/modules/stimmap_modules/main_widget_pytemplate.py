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
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.comboBoxShowTimelineChoice = QtWidgets.QComboBox(self.dockWidgetContents)
        self.comboBoxShowTimelineChoice.setObjectName("comboBoxShowTimelineChoice")
        self.gridLayout.addWidget(self.comboBoxShowTimelineChoice, 0, 2, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 6)
        self.btnImport = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnImport.setObjectName("btnImport")
        self.gridLayout.addWidget(self.btnImport, 2, 0, 1, 1)
        self.btnExport = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnExport.setObjectName("btnExport")
        self.gridLayout.addWidget(self.btnExport, 2, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(242, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 1)
        self.btnCancel = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnCancel.setObjectName("btnCancel")
        self.gridLayout.addWidget(self.btnCancel, 2, 4, 1, 1)
        self.btnSetAllMaps = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSetAllMaps.setObjectName("btnSetAllMaps")
        self.gridLayout.addWidget(self.btnSetAllMaps, 2, 5, 1, 1)
        MainWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(MainWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("MainWidget", "Stimulus Mapping"))
        self.label.setText(_translate("MainWidget", "Show on timeline: "))
        self.btnImport.setText(_translate("MainWidget", "Import"))
        self.btnExport.setText(_translate("MainWidget", "Export"))
        self.btnCancel.setText(_translate("MainWidget", "Cancel"))
        self.btnSetAllMaps.setText(_translate("MainWidget", "Set all maps"))

