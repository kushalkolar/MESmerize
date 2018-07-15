# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/datapoint_tracer.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DatapointTracer(object):
    def setupUi(self, DatapointTracer):
        DatapointTracer.setObjectName("DatapointTracer")
        DatapointTracer.resize(1052, 664)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DatapointTracer)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter_2 = QtWidgets.QSplitter(DatapointTracer)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.groupBoxInfo = QtWidgets.QGroupBox(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxInfo.sizePolicy().hasHeightForWidth())
        self.groupBoxInfo.setSizePolicy(sizePolicy)
        self.groupBoxInfo.setObjectName("groupBoxInfo")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBoxInfo)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBoxInfo)
        self.label.setMinimumSize(QtCore.QSize(50, 0))
        self.label.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEditUUID = QtWidgets.QLineEdit(self.groupBoxInfo)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lineEditUUID.setFont(font)
        self.lineEditUUID.setReadOnly(True)
        self.lineEditUUID.setObjectName("lineEditUUID")
        self.horizontalLayout.addWidget(self.lineEditUUID)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pushButton = QtWidgets.QPushButton(self.groupBoxInfo)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.graphicsViewImage = GraphicsLayoutWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(10)
        sizePolicy.setHeightForWidth(self.graphicsViewImage.sizePolicy().hasHeightForWidth())
        self.graphicsViewImage.setSizePolicy(sizePolicy)
        self.graphicsViewImage.setObjectName("graphicsViewImage")
        self.graphicsViewPlot = PlotWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.graphicsViewPlot.sizePolicy().hasHeightForWidth())
        self.graphicsViewPlot.setSizePolicy(sizePolicy)
        self.graphicsViewPlot.setObjectName("graphicsViewPlot")
        self.verticalLayout_2.addWidget(self.splitter_2)

        self.retranslateUi(DatapointTracer)
        QtCore.QMetaObject.connectSlotsByName(DatapointTracer)

    def retranslateUi(self, DatapointTracer):
        _translate = QtCore.QCoreApplication.translate
        DatapointTracer.setWindowTitle(_translate("DatapointTracer", "Form"))
        self.groupBoxInfo.setTitle(_translate("DatapointTracer", "Info"))
        self.label.setText(_translate("DatapointTracer", "UUID:"))
        self.pushButton.setText(_translate("DatapointTracer", "Open in viewer"))

from pyqtgraphCore import GraphicsLayoutWidget, PlotWidget
