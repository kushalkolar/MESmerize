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
        DockWidget.resize(707, 579)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.tabStandard = QtWidgets.QWidget()
        self.tabStandard.setObjectName("tabStandard")
        self.gridLayout = QtWidgets.QGridLayout(self.tabStandard)
        self.gridLayout.setObjectName("gridLayout")
        self.btnAddROI = QtWidgets.QPushButton(self.tabStandard)
        self.btnAddROI.setObjectName("btnAddROI")
        self.gridLayout.addWidget(self.btnAddROI, 0, 0, 1, 1)
        self.checkBoxShowAll = QtWidgets.QCheckBox(self.tabStandard)
        self.checkBoxShowAll.setObjectName("checkBoxShowAll")
        self.gridLayout.addWidget(self.checkBoxShowAll, 0, 1, 1, 2)
        self.checkBoxLivePlot = QtWidgets.QCheckBox(self.tabStandard)
        self.checkBoxLivePlot.setObjectName("checkBoxLivePlot")
        self.gridLayout.addWidget(self.checkBoxLivePlot, 0, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(414, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.verticalLayoutROIList = QtWidgets.QVBoxLayout()
        self.verticalLayoutROIList.setObjectName("verticalLayoutROIList")
        self.label = QtWidgets.QLabel(self.tabStandard)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayoutROIList.addWidget(self.label)
        self.listWidgetROIs = QtWidgets.QListWidget(self.tabStandard)
        self.listWidgetROIs.setMaximumSize(QtCore.QSize(120, 16777215))
        self.listWidgetROIs.setObjectName("listWidgetROIs")
        self.verticalLayoutROIList.addWidget(self.listWidgetROIs)
        self.gridLayout.addLayout(self.verticalLayoutROIList, 1, 0, 1, 2)
        self.verticalLayoutTags = QtWidgets.QVBoxLayout()
        self.verticalLayoutTags.setObjectName("verticalLayoutTags")
        self.label_2 = QtWidgets.QLabel(self.tabStandard)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayoutTags.addWidget(self.label_2)
        self.listWidgetROITags = QtWidgets.QListWidget(self.tabStandard)
        self.listWidgetROITags.setObjectName("listWidgetROITags")
        self.verticalLayoutTags.addWidget(self.listWidgetROITags)
        self.gridLayout.addLayout(self.verticalLayoutTags, 1, 2, 1, 3)
        self.lineEditROITag = QtWidgets.QLineEdit(self.tabStandard)
        self.lineEditROITag.setObjectName("lineEditROITag")
        self.gridLayout.addWidget(self.lineEditROITag, 2, 0, 1, 5)
        self.btnSetROITag = QtWidgets.QPushButton(self.tabStandard)
        self.btnSetROITag.setObjectName("btnSetROITag")
        self.gridLayout.addWidget(self.btnSetROITag, 3, 0, 1, 1)
        self.tabWidget.addTab(self.tabStandard, "")
        self.tabMetaROI = QtWidgets.QWidget()
        self.tabMetaROI.setObjectName("tabMetaROI")
        self.tabWidget.addTab(self.tabMetaROI, "")
        self.verticalLayout.addWidget(self.tabWidget)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.tabWidget.setCurrentIndex(0)
        self.lineEditROITag.returnPressed.connect(self.btnSetROITag.click)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "ROI Manager"))
        self.btnAddROI.setText(_translate("DockWidget", "Add ROI"))
        self.checkBoxShowAll.setText(_translate("DockWidget", "Show all"))
        self.checkBoxLivePlot.setText(_translate("DockWidget", "Live plot"))
        self.label.setText(_translate("DockWidget", "ROIs"))
        self.label_2.setText(_translate("DockWidget", "Tags"))
        self.lineEditROITag.setPlaceholderText(_translate("DockWidget", "Add Tag to ROI Definition"))
        self.btnSetROITag.setText(_translate("DockWidget", "Set ROI tag"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStandard), _translate("DockWidget", "Standard ROIs"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMetaROI), _translate("DockWidget", "Meta ROIs"))

