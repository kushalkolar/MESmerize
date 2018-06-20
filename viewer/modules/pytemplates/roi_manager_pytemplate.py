# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './roi_manager_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(644, 511)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.tabStandard = QtWidgets.QWidget()
        self.tabStandard.setObjectName("tabStandard")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tabStandard)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnAddROI = QtWidgets.QPushButton(self.tabStandard)
        self.btnAddROI.setObjectName("btnAddROI")
        self.gridLayout_2.addWidget(self.btnAddROI, 0, 0, 1, 1)
        self.verticalLayoutROIList = QtWidgets.QVBoxLayout()
        self.verticalLayoutROIList.setObjectName("verticalLayoutROIList")
        self.label = QtWidgets.QLabel(self.tabStandard)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayoutROIList.addWidget(self.label)
        self.gridLayout_2.addLayout(self.verticalLayoutROIList, 1, 0, 1, 1)
        self.verticalLayoutTags = QtWidgets.QVBoxLayout()
        self.verticalLayoutTags.setObjectName("verticalLayoutTags")
        self.label_2 = QtWidgets.QLabel(self.tabStandard)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayoutTags.addWidget(self.label_2)
        self.gridLayout_2.addLayout(self.verticalLayoutTags, 1, 1, 1, 1)
        self.lineEditROITag = QtWidgets.QLineEdit(self.tabStandard)
        self.lineEditROITag.setObjectName("lineEditROITag")
        self.gridLayout_2.addWidget(self.lineEditROITag, 2, 0, 1, 2)
        self.btnSetROITag = QtWidgets.QPushButton(self.tabStandard)
        self.btnSetROITag.setObjectName("btnSetROITag")
        self.gridLayout_2.addWidget(self.btnSetROITag, 3, 0, 1, 2)
        self.tabWidget.addTab(self.tabStandard, "")
        self.tabMetaROI = QtWidgets.QWidget()
        self.tabMetaROI.setObjectName("tabMetaROI")
        self.tabWidget.addTab(self.tabMetaROI, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.tabWidget.setCurrentIndex(0)
        self.lineEditROITag.returnPressed.connect(self.btnSetROITag.click)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "ROI Manager"))
        self.btnAddROI.setText(_translate("DockWidget", "Add ROI"))
        self.label.setText(_translate("DockWidget", "ROIs"))
        self.label_2.setText(_translate("DockWidget", "Tags"))
        self.lineEditROITag.setPlaceholderText(_translate("DockWidget", "Add Tag to ROI Definition"))
        self.btnSetROITag.setText(_translate("DockWidget", "Set ROI tag"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStandard), _translate("DockWidget", "Standard ROIs"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMetaROI), _translate("DockWidget", "Meta ROIs"))

