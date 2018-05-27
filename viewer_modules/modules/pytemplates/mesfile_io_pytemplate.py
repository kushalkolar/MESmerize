# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mesfile_io_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(560, 335)
        DockWidget.setFloating(True)
        DockWidget.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.listwMesfile = QtWidgets.QListWidget(self.dockWidgetContents)
        self.listwMesfile.setEnabled(False)
        self.listwMesfile.setObjectName("listwMesfile")
        self.gridLayout.addWidget(self.listwMesfile, 2, 0, 1, 4)
        self.mesfile_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.mesfile_label.setObjectName("mesfile_label")
        self.gridLayout.addWidget(self.mesfile_label, 1, 0, 1, 2)
        self.btnOpenMesFile = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnOpenMesFile.setObjectName("btnOpenMesFile")
        self.gridLayout.addWidget(self.btnOpenMesFile, 0, 0, 1, 1)
        self.btnStimMapGUI = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnStimMapGUI.setEnabled(False)
        self.btnStimMapGUI.setObjectName("btnStimMapGUI")
        self.gridLayout.addWidget(self.btnStimMapGUI, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(325, 23, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 2)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Mesfile I/O"))
        self.mesfile_label.setText(_translate("DockWidget", "MES file contents:"))
        self.btnOpenMesFile.setText(_translate("DockWidget", "Open mes file"))
        self.btnStimMapGUI.setText(_translate("DockWidget", "Stim Map GUI"))

