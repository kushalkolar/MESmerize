# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_manager.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(296, 474)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(self.dockWidgetContents)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.listwBatch = QtWidgets.QListWidget(self.widget)
        self.listwBatch.setObjectName("listwBatch")
        self.gridLayout_2.addWidget(self.listwBatch, 0, 0, 1, 3)
        self.btnStart = QtWidgets.QPushButton(self.widget)
        self.btnStart.setObjectName("btnStart")
        self.gridLayout_2.addWidget(self.btnStart, 1, 0, 1, 1)
        self.btnOpen = QtWidgets.QPushButton(self.widget)
        self.btnOpen.setObjectName("btnOpen")
        self.gridLayout_2.addWidget(self.btnOpen, 1, 1, 1, 1)
        self.btnDelete = QtWidgets.QPushButton(self.widget)
        self.btnDelete.setObjectName("btnDelete")
        self.gridLayout_2.addWidget(self.btnDelete, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.scrollArea = QtWidgets.QScrollArea(self.splitter)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 276, 185))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.labelMeta_info = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.labelMeta_info.setText("")
        self.labelMeta_info.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.labelMeta_info.setObjectName("labelMeta_info")
        self.gridLayout.addWidget(self.labelMeta_info, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Batch Manager"))
        self.btnStart.setText(_translate("DockWidget", "Start"))
        self.btnOpen.setText(_translate("DockWidget", "Open"))
        self.btnDelete.setText(_translate("DockWidget", "Delete selection"))

