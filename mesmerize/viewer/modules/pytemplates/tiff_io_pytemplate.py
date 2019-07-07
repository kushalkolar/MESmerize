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
        DockWidget.resize(389, 276)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnSelectTiff = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSelectTiff.setMaximumSize(QtCore.QSize(90, 32))
        self.btnSelectTiff.setObjectName("btnSelectTiff")
        self.horizontalLayout.addWidget(self.btnSelectTiff)
        self.labelFileTiff = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelFileTiff.setText("")
        self.labelFileTiff.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.labelFileTiff.setObjectName("labelFileTiff")
        self.horizontalLayout.addWidget(self.labelFileTiff)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnSelectMetaFile = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnSelectMetaFile.setMaximumSize(QtCore.QSize(130, 32))
        self.btnSelectMetaFile.setObjectName("btnSelectMetaFile")
        self.horizontalLayout_3.addWidget(self.btnSelectMetaFile)
        self.labelFileMeta = QtWidgets.QLabel(self.dockWidgetContents)
        self.labelFileMeta.setText("")
        self.labelFileMeta.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.labelFileMeta.setObjectName("labelFileMeta")
        self.horizontalLayout_3.addWidget(self.labelFileMeta)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.radioButtonAsArray = QtWidgets.QRadioButton(self.dockWidgetContents)
        self.radioButtonAsArray.setObjectName("radioButtonAsArray")
        self.verticalLayout.addWidget(self.radioButtonAsArray)
        self.radioButtonAsArrayMulti = QtWidgets.QRadioButton(self.dockWidgetContents)
        self.radioButtonAsArrayMulti.setObjectName("radioButtonAsArrayMulti")
        self.verticalLayout.addWidget(self.radioButtonAsArrayMulti)
        self.radioButtonImread = QtWidgets.QRadioButton(self.dockWidgetContents)
        self.radioButtonImread.setObjectName("radioButtonImread")
        self.verticalLayout.addWidget(self.radioButtonImread)
        self.btnLoadIntoWorkEnv = QtWidgets.QPushButton(self.dockWidgetContents)
        self.btnLoadIntoWorkEnv.setObjectName("btnLoadIntoWorkEnv")
        self.verticalLayout.addWidget(self.btnLoadIntoWorkEnv)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)
        DockWidget.setTabOrder(self.btnSelectTiff, self.btnSelectMetaFile)
        DockWidget.setTabOrder(self.btnSelectMetaFile, self.radioButtonAsArrayMulti)
        DockWidget.setTabOrder(self.radioButtonAsArrayMulti, self.btnLoadIntoWorkEnv)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Tiff file &I/O"))
        self.btnSelectTiff.setText(_translate("DockWidget", "Select file"))
        self.btnSelectMetaFile.setText(_translate("DockWidget", "Select meta data"))
        self.label.setText(_translate("DockWidget", "Load method:"))
        self.radioButtonAsArray.setToolTip(_translate("DockWidget", "Usually faster alternative to imread"))
        self.radioButtonAsArray.setText(_translate("DockWidget", "asarray"))
        self.radioButtonAsArrayMulti.setToolTip(_translate("DockWidget", "Use if tiff was created in append mode"))
        self.radioButtonAsArrayMulti.setText(_translate("DockWidget", "asarray - multi series"))
        self.radioButtonImread.setToolTip(_translate("DockWidget", "Should work for most tiffs if they were not created in append mode."))
        self.radioButtonImread.setText(_translate("DockWidget", "i&mread"))
        self.btnLoadIntoWorkEnv.setText(_translate("DockWidget", "Load into workEnv"))

