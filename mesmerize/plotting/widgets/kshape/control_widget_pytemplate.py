# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './control_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KShapeControl(object):
    def setupUi(self, KShapeControl):
        KShapeControl.setObjectName("KShapeControl")
        KShapeControl.resize(321, 834)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBoxKShapeParams = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.groupBoxKShapeParams.setObjectName("groupBoxKShapeParams")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBoxKShapeParams)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButtonReconnectFlowchartInput = QtWidgets.QPushButton(self.groupBoxKShapeParams)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.pushButtonReconnectFlowchartInput.setFont(font)
        self.pushButtonReconnectFlowchartInput.setObjectName("pushButtonReconnectFlowchartInput")
        self.verticalLayout_3.addWidget(self.pushButtonReconnectFlowchartInput)
        self.labelConnectedToFlowchart = QtWidgets.QLabel(self.groupBoxKShapeParams)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelConnectedToFlowchart.setFont(font)
        self.labelConnectedToFlowchart.setAlignment(QtCore.Qt.AlignCenter)
        self.labelConnectedToFlowchart.setObjectName("labelConnectedToFlowchart")
        self.verticalLayout_3.addWidget(self.labelConnectedToFlowchart)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_8 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_12.addWidget(self.label_8)
        self.comboBoxDataColumn = QtWidgets.QComboBox(self.groupBoxKShapeParams)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxDataColumn.sizePolicy().hasHeightForWidth())
        self.comboBoxDataColumn.setSizePolicy(sizePolicy)
        self.comboBoxDataColumn.setObjectName("comboBoxDataColumn")
        self.horizontalLayout_12.addWidget(self.comboBoxDataColumn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.verticalLayout_3.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBoxN_clusters = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxN_clusters.setMinimum(2)
        self.spinBoxN_clusters.setProperty("value", 3)
        self.spinBoxN_clusters.setObjectName("spinBoxN_clusters")
        self.horizontalLayout.addWidget(self.spinBoxN_clusters)
        self.horizontalLayout_6.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.spinBoxMaxIter = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxMaxIter.setMaximum(9999)
        self.spinBoxMaxIter.setSingleStep(50)
        self.spinBoxMaxIter.setProperty("value", 300)
        self.spinBoxMaxIter.setObjectName("spinBoxMaxIter")
        self.horizontalLayout_2.addWidget(self.spinBoxMaxIter)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.spinBoxRandom = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxRandom.setEnabled(False)
        self.spinBoxRandom.setMaximum(999)
        self.spinBoxRandom.setObjectName("spinBoxRandom")
        self.horizontalLayout_5.addWidget(self.spinBoxRandom)
        self.checkBoxRandom = QtWidgets.QCheckBox(self.groupBoxKShapeParams)
        self.checkBoxRandom.setChecked(True)
        self.checkBoxRandom.setObjectName("checkBoxRandom")
        self.horizontalLayout_5.addWidget(self.checkBoxRandom)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.spinBoxTol = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxTol.setMinimum(-20)
        self.spinBoxTol.setMaximum(10)
        self.spinBoxTol.setSingleStep(1)
        self.spinBoxTol.setProperty("value", -6)
        self.spinBoxTol.setObjectName("spinBoxTol")
        self.horizontalLayout_3.addWidget(self.spinBoxTol)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.spinBoxN_init = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxN_init.setMinimum(1)
        self.spinBoxN_init.setObjectName("spinBoxN_init")
        self.horizontalLayout_4.addWidget(self.spinBoxN_init)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_7)
        spacerItem3 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_11 = QtWidgets.QLabel(self.groupBoxKShapeParams)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_15.addWidget(self.label_11)
        self.spinBoxTrainSubsetPercentage = QtWidgets.QSpinBox(self.groupBoxKShapeParams)
        self.spinBoxTrainSubsetPercentage.setMinimum(30)
        self.spinBoxTrainSubsetPercentage.setMaximum(100)
        self.spinBoxTrainSubsetPercentage.setSingleStep(10)
        self.spinBoxTrainSubsetPercentage.setObjectName("spinBoxTrainSubsetPercentage")
        self.horizontalLayout_15.addWidget(self.spinBoxTrainSubsetPercentage)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_15.addItem(spacerItem4)
        self.verticalLayout_3.addLayout(self.horizontalLayout_15)
        self.verticalLayout_4.addWidget(self.groupBoxKShapeParams)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.pushButtonStart = QtWidgets.QPushButton(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonStart.setFont(font)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.horizontalLayout_11.addWidget(self.pushButtonStart)
        self.pushButtonAbort = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButtonAbort.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonAbort.setFont(font)
        self.pushButtonAbort.setObjectName("pushButtonAbort")
        self.horizontalLayout_11.addWidget(self.pushButtonAbort)
        self.verticalLayout_4.addLayout(self.horizontalLayout_11)
        self.label_6 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_4.addWidget(self.label_6)
        self.textBrowser = QtWidgets.QTextBrowser(self.dockWidgetContents)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_4.addWidget(self.textBrowser)
        self.groupBoxPlotParams = QtWidgets.QGroupBox(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.groupBoxPlotParams.setFont(font)
        self.groupBoxPlotParams.setObjectName("groupBoxPlotParams")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxPlotParams)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_7 = QtWidgets.QLabel(self.groupBoxPlotParams)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_14.addWidget(self.label_7)
        self.listWidgetClusterNumber = QtWidgets.QListWidget(self.groupBoxPlotParams)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidgetClusterNumber.sizePolicy().hasHeightForWidth())
        self.listWidgetClusterNumber.setSizePolicy(sizePolicy)
        self.listWidgetClusterNumber.setMinimumSize(QtCore.QSize(0, 33))
        self.listWidgetClusterNumber.setMaximumSize(QtCore.QSize(16777215, 33))
        self.listWidgetClusterNumber.setProperty("showDropIndicator", False)
        self.listWidgetClusterNumber.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.listWidgetClusterNumber.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listWidgetClusterNumber.setFlow(QtWidgets.QListView.LeftToRight)
        self.listWidgetClusterNumber.setObjectName("listWidgetClusterNumber")
        self.horizontalLayout_14.addWidget(self.listWidgetClusterNumber)
        self.verticalLayout_2.addLayout(self.horizontalLayout_14)
        self.line = QtWidgets.QFrame(self.groupBoxPlotParams)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.label_12 = QtWidgets.QLabel(self.groupBoxPlotParams)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_2.addWidget(self.label_12)
        self.checkBoxShowKShapeCenters = QtWidgets.QCheckBox(self.groupBoxPlotParams)
        self.checkBoxShowKShapeCenters.setObjectName("checkBoxShowKShapeCenters")
        self.verticalLayout_2.addWidget(self.checkBoxShowKShapeCenters)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_9 = QtWidgets.QLabel(self.groupBoxPlotParams)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_13.addWidget(self.label_9)
        self.spinBoxMaxNumCurves = QtWidgets.QSpinBox(self.groupBoxPlotParams)
        self.spinBoxMaxNumCurves.setMaximum(1000)
        self.spinBoxMaxNumCurves.setSingleStep(25)
        self.spinBoxMaxNumCurves.setProperty("value", 100)
        self.spinBoxMaxNumCurves.setObjectName("spinBoxMaxNumCurves")
        self.horizontalLayout_13.addWidget(self.spinBoxMaxNumCurves)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout_13)
        self.label_13 = QtWidgets.QLabel(self.groupBoxPlotParams)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.verticalLayout_2.addWidget(self.label_13)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_10 = QtWidgets.QLabel(self.groupBoxPlotParams)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_16.addWidget(self.label_10)
        self.comboBoxErrorBand = QtWidgets.QComboBox(self.groupBoxPlotParams)
        self.comboBoxErrorBand.setObjectName("comboBoxErrorBand")
        self.comboBoxErrorBand.addItem("")
        self.comboBoxErrorBand.addItem("")
        self.comboBoxErrorBand.addItem("")
        self.horizontalLayout_16.addWidget(self.comboBoxErrorBand)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_16)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_14 = QtWidgets.QLabel(self.groupBoxPlotParams)
        self.label_14.setObjectName("label_14")
        self.verticalLayout.addWidget(self.label_14)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.radioButtonXZeroZero = QtWidgets.QRadioButton(self.groupBoxPlotParams)
        self.radioButtonXZeroZero.setChecked(True)
        self.radioButtonXZeroZero.setObjectName("radioButtonXZeroZero")
        self.horizontalLayout_17.addWidget(self.radioButtonXZeroZero)
        self.radioButtonXZeroMaxima = QtWidgets.QRadioButton(self.groupBoxPlotParams)
        self.radioButtonXZeroMaxima.setObjectName("radioButtonXZeroMaxima")
        self.horizontalLayout_17.addWidget(self.radioButtonXZeroMaxima)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_17.addItem(spacerItem7)
        self.verticalLayout.addLayout(self.horizontalLayout_17)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.pushButtonApplyPlotOptions = QtWidgets.QPushButton(self.groupBoxPlotParams)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonApplyPlotOptions.setFont(font)
        self.pushButtonApplyPlotOptions.setObjectName("pushButtonApplyPlotOptions")
        self.verticalLayout_2.addWidget(self.pushButtonApplyPlotOptions)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonSave = QtWidgets.QPushButton(self.groupBoxPlotParams)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.gridLayout.addWidget(self.pushButtonSave, 0, 0, 1, 1)
        self.pushButtonLoad = QtWidgets.QPushButton(self.groupBoxPlotParams)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        self.gridLayout.addWidget(self.pushButtonLoad, 0, 1, 1, 1)
        self.pushButtonExportMeans = QtWidgets.QPushButton(self.groupBoxPlotParams)
        self.pushButtonExportMeans.setObjectName("pushButtonExportMeans")
        self.gridLayout.addWidget(self.pushButtonExportMeans, 1, 0, 1, 1)
        self.pushButtonExportRaw = QtWidgets.QPushButton(self.groupBoxPlotParams)
        self.pushButtonExportRaw.setObjectName("pushButtonExportRaw")
        self.gridLayout.addWidget(self.pushButtonExportRaw, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.verticalLayout_4.addWidget(self.groupBoxPlotParams)
        KShapeControl.setWidget(self.dockWidgetContents)

        self.retranslateUi(KShapeControl)
        QtCore.QMetaObject.connectSlotsByName(KShapeControl)

    def retranslateUi(self, KShapeControl):
        _translate = QtCore.QCoreApplication.translate
        KShapeControl.setWindowTitle(_translate("KShapeControl", "Co&ntrols"))
        self.groupBoxKShapeParams.setTitle(_translate("KShapeControl", "KShape params"))
        self.pushButtonReconnectFlowchartInput.setText(_translate("KShapeControl", "Reconnect flowchart input"))
        self.labelConnectedToFlowchart.setText(_translate("KShapeControl", "INPUT CONNECTED TO FLOWCHART"))
        self.label_8.setText(_translate("KShapeControl", "data_column"))
        self.label.setText(_translate("KShapeControl", "n_clusters:"))
        self.label_2.setText(_translate("KShapeControl", "max_iter:"))
        self.label_5.setText(_translate("KShapeControl", "random_state:"))
        self.checkBoxRandom.setText(_translate("KShapeControl", "random"))
        self.label_3.setText(_translate("KShapeControl", "tol: 10 ^"))
        self.label_4.setText(_translate("KShapeControl", "n_init:"))
        self.label_11.setText(_translate("KShapeControl", "training subset (%)"))
        self.pushButtonStart.setText(_translate("KShapeControl", "Start"))
        self.pushButtonAbort.setText(_translate("KShapeControl", "Abort"))
        self.label_6.setText(_translate("KShapeControl", "Status:"))
        self.textBrowser.setHtml(_translate("KShapeControl", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Noto Sans\';\"><br /></p></body></html>"))
        self.groupBoxPlotParams.setTitle(_translate("KShapeControl", "Plot Options"))
        self.label_7.setText(_translate("KShapeControl", "Plot cluster:"))
        self.label_12.setText(_translate("KShapeControl", "Raw plots"))
        self.checkBoxShowKShapeCenters.setText(_translate("KShapeControl", "Show centers"))
        self.label_9.setText(_translate("KShapeControl", "max num curves:"))
        self.label_13.setText(_translate("KShapeControl", "Mean plots"))
        self.label_10.setText(_translate("KShapeControl", "Error band"))
        self.comboBoxErrorBand.setItemText(0, _translate("KShapeControl", "confidence interval"))
        self.comboBoxErrorBand.setItemText(1, _translate("KShapeControl", "standard deviation"))
        self.comboBoxErrorBand.setItemText(2, _translate("KShapeControl", "None"))
        self.label_14.setText(_translate("KShapeControl", "Set x = 0 at:"))
        self.radioButtonXZeroZero.setText(_translate("KShapeControl", "Zero"))
        self.radioButtonXZeroMaxima.setText(_translate("KShapeControl", "Maxima"))
        self.pushButtonApplyPlotOptions.setText(_translate("KShapeControl", "Apply Options"))
        self.pushButtonSave.setText(_translate("KShapeControl", "Save"))
        self.pushButtonLoad.setText(_translate("KShapeControl", "Load"))
        self.pushButtonExportMeans.setText(_translate("KShapeControl", "Export means"))
        self.pushButtonExportRaw.setText(_translate("KShapeControl", "Export raw"))
