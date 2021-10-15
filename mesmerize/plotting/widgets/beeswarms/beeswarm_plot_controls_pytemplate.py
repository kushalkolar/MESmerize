# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './beeswarm_plot_controls.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BeeswarmControls(object):
    def setupUi(self, BeeswarmControls):
        BeeswarmControls.setObjectName("BeeswarmControls")
        BeeswarmControls.resize(279, 169)
        self.horizontalSliderSpotSize = QtWidgets.QSlider(BeeswarmControls)
        self.horizontalSliderSpotSize.setGeometry(QtCore.QRect(10, 60, 231, 20))
        self.horizontalSliderSpotSize.setMinimum(1)
        self.horizontalSliderSpotSize.setProperty("value", 10)
        self.horizontalSliderSpotSize.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSliderSpotSize.setObjectName("horizontalSliderSpotSize")
        self.btnTraceDatapoint = QtWidgets.QPushButton(BeeswarmControls)
        self.btnTraceDatapoint.setGeometry(QtCore.QRect(10, 90, 120, 36))
        self.btnTraceDatapoint.setObjectName("btnTraceDatapoint")
        self.pushButtonSummaryStats = QtWidgets.QPushButton(BeeswarmControls)
        self.pushButtonSummaryStats.setGeometry(QtCore.QRect(10, 130, 176, 36))
        self.pushButtonSummaryStats.setObjectName("pushButtonSummaryStats")
        self.layoutWidget = QtWidgets.QWidget(BeeswarmControls)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 30, 136, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.labelSpotSize = QtWidgets.QLabel(self.layoutWidget)
        self.labelSpotSize.setObjectName("labelSpotSize")
        self.horizontalLayout_3.addWidget(self.labelSpotSize)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)

        self.retranslateUi(BeeswarmControls)
        self.horizontalSliderSpotSize.valueChanged['int'].connect(self.labelSpotSize.setNum)
        QtCore.QMetaObject.connectSlotsByName(BeeswarmControls)

    def retranslateUi(self, BeeswarmControls):
        _translate = QtCore.QCoreApplication.translate
        BeeswarmControls.setWindowTitle(_translate("BeeswarmControls", "Form"))
        self.btnTraceDatapoint.setText(_translate("BeeswarmControls", "Trace Datapoint"))
        self.pushButtonSummaryStats.setText(_translate("BeeswarmControls", "View Summary Statistics"))
        self.label_3.setText(_translate("BeeswarmControls", "Spot size: "))
        self.labelSpotSize.setText(_translate("BeeswarmControls", "10"))

