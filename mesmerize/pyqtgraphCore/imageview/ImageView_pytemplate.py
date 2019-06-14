# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImageViewTemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(888, 742)
        self.gridLayout_10 = QtWidgets.QGridLayout(Form)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.splitterHighest = QtWidgets.QSplitter(Form)
        self.splitterHighest.setOrientation(QtCore.Qt.Vertical)
        self.splitterHighest.setObjectName("splitterHighest")
        self.splitterFilesImage = QtWidgets.QSplitter(self.splitterHighest)
        self.splitterFilesImage.setOrientation(QtCore.Qt.Vertical)
        self.splitterFilesImage.setObjectName("splitterFilesImage")
        self.splitter = QtWidgets.QSplitter(self.splitterFilesImage)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.btnExportWorkEnv = QtWidgets.QPushButton(self.layoutWidget)
        self.btnExportWorkEnv.setObjectName("btnExportWorkEnv")
        self.gridLayout_8.addWidget(self.btnExportWorkEnv, 1, 4, 1, 1)
        self.histogram = HistogramLUTWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.histogram.sizePolicy().hasHeightForWidth())
        self.histogram.setSizePolicy(sizePolicy)
        self.histogram.setMinimumSize(QtCore.QSize(150, 0))
        self.histogram.setMaximumSize(QtCore.QSize(150, 16777215))
        self.histogram.setObjectName("histogram")
        self.gridLayout_8.addWidget(self.histogram, 2, 4, 2, 1)
        self.graphicsView = GraphicsView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout_8.addWidget(self.graphicsView, 1, 0, 4, 4)
        self.label_curr_img_seq_name = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_curr_img_seq_name.setFont(font)
        self.label_curr_img_seq_name.setText("")
        self.label_curr_img_seq_name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_curr_img_seq_name.setObjectName("label_curr_img_seq_name")
        self.gridLayout_8.addWidget(self.label_curr_img_seq_name, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label.setObjectName("label")
        self.gridLayout_8.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem, 0, 2, 1, 1)
        self.roiPlot = PlotWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.roiPlot.sizePolicy().hasHeightForWidth())
        self.roiPlot.setSizePolicy(sizePolicy)
        self.roiPlot.setMinimumSize(QtCore.QSize(0, 40))
        self.roiPlot.setObjectName("roiPlot")
        self.gridLayout_10.addWidget(self.splitterHighest, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.roiPlot, self.histogram)
        Form.setTabOrder(self.histogram, self.graphicsView)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btnExportWorkEnv.setText(_translate("Form", "Export workEnv"))
        self.label.setText(_translate("Form", "Current image sequence:"))

from ..widgets.GraphicsView import GraphicsView
from ..widgets.HistogramLUTWidget import HistogramLUTWidget
from ..widgets.PlotWidget import PlotWidget
