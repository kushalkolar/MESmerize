# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'control_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(295, 332)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.listWidgetColorMaps = QtWidgets.QListWidget(self.dockWidgetContents)
        self.listWidgetColorMaps.setGeometry(QtCore.QRect(10, 40, 256, 192))
        self.listWidgetColorMaps.setObjectName("listWidgetColorMaps")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 18))
        self.label.setObjectName("label")
        self.checkBoxShowStimuli = QtWidgets.QCheckBox(self.dockWidgetContents)
        self.checkBoxShowStimuli.setGeometry(QtCore.QRect(10, 250, 121, 22))
        self.checkBoxShowStimuli.setObjectName("checkBoxShowStimuli")
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Heat&map Controls"))
        self.label.setText(_translate("DockWidget", "Colormap:"))
        self.checkBoxShowStimuli.setText(_translate("DockWidget", "Show Stimuli"))

