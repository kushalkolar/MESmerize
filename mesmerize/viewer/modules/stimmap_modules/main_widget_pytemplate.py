# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.12
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
        self.comboBoxShowTimelineChoice = QtWidgets.QComboBox(self.dockWidgetContents)
        self.comboBoxShowTimelineChoice.setObjectName("comboBoxShowTimelineChoice")
        self.gridLayout.addWidget(self.comboBoxShowTimelineChoice, 0, 2, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(242, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 5)
        self.btnSetAllMaps = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSetAllMaps.setObjectName("btnSetAllMaps")
        self.gridLayout.addWidget(self.btnSetAllMaps, 2, 4, 1, 1)
        MainWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(MainWidget)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("MainWidget", "Stimulus Mapping"))
        self.label.setText(_translate("MainWidget", "Show on timeline: "))
        self.btnSetAllMaps.setText(_translate("MainWidget", "Set all maps"))


