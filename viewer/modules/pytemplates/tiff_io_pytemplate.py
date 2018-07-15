# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './tiff_io_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(369, 218)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.btnLoadIntoWorkEnv = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnLoadIntoWorkEnv.setObjectName("btnLoadIntoWorkEnv")
        self.gridLayout.addWidget(self.btnLoadIntoWorkEnv, 5, 0, 1, 1)
        self.radioButtonImread = QtWidgets.QRadioButton(self.dockWidgetContents)
        self.radioButtonImread.setObjectName("radioButtonImread")
        self.gridLayout.addWidget(self.radioButtonImread, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButtonAsarray = QtWidgets.QRadioButton(self.dockWidgetContents)
        self.radioButtonAsarray.setObjectName("radioButtonAsarray")
        self.horizontalLayout_2.addWidget(self.radioButtonAsarray)
        self.checkBox = QtWidgets.QCheckBox(self.dockWidgetContents)
        self.checkBox.setEnabled(False)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnSelectTiff = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSelectTiff.setMaximumSize(QtCore.QSize(70, 26))
        self.btnSelectTiff.setObjectName("btnSelectTiff")
        self.horizontalLayout.addWidget(self.btnSelectTiff)
        self.labelFileTiff = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelFileTiff.setText("")
        self.labelFileTiff.setObjectName("labelFileTiff")
        self.horizontalLayout.addWidget(self.labelFileTiff)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnSelectMetaFile = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSelectMetaFile.setMaximumSize(QtCore.QSize(110, 26))
        self.btnSelectMetaFile.setObjectName("btnSelectMetaFile")
        self.horizontalLayout_3.addWidget(self.btnSelectMetaFile)
        self.labelFileMeta = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelFileMeta.setText("")
        self.labelFileMeta.setObjectName("labelFileMeta")
        self.horizontalLayout_3.addWidget(self.labelFileMeta)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.radioButtonAsarray.toggled['bool'].connect(self.checkBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)
        DockWidget.setTabOrder(self.btnSelectTiff, self.btnSelectMetaFile)
        DockWidget.setTabOrder(self.btnSelectMetaFile, self.radioButtonImread)
        DockWidget.setTabOrder(self.radioButtonImread, self.radioButtonAsarray)
        DockWidget.setTabOrder(self.radioButtonAsarray, self.checkBox)
        DockWidget.setTabOrder(self.checkBox, self.btnLoadIntoWorkEnv)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Tiff file I/O"))
        self.btnLoadIntoWorkEnv.setText(_translate("DockWidget", "Load into workEnv"))
        self.radioButtonImread.setText(_translate("DockWidget", "imread"))
        self.label.setText(_translate("DockWidget", "Load method:"))
        self.radioButtonAsarray.setText(_translate("DockWidget", "asarray"))
        self.checkBox.setText(_translate("DockWidget", "is_nih"))
        self.btnSelectTiff.setText(_translate("DockWidget", "Select file"))
        self.btnSelectMetaFile.setText(_translate("DockWidget", "Select meta data"))

