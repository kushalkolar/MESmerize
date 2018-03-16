# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'exporter_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_exporter_template(object):
    def setupUi(self, exporter_template):
        exporter_template.setObjectName("exporter_template")
        exporter_template.resize(229, 216)
        self.gridLayout = QtWidgets.QGridLayout(exporter_template)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(exporter_template)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(exporter_template)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.comboBoxFormat = QtWidgets.QComboBox(exporter_template)
        self.comboBoxFormat.setObjectName("comboBoxFormat")
        self.gridLayout.addWidget(self.comboBoxFormat, 0, 1, 1, 3)
        self.labelSlider = QtWidgets.QLabel(exporter_template)
        self.labelSlider.setAlignment(QtCore.Qt.AlignCenter)
        self.labelSlider.setObjectName("labelSlider")
        self.gridLayout.addWidget(self.labelSlider, 1, 1, 1, 3)
        self.label_3 = QtWidgets.QLabel(exporter_template)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 2, 1)
        self.btnChoosePath = QtWidgets.QPushButton(exporter_template)
        self.btnChoosePath.setMaximumSize(QtCore.QSize(31, 16777215))
        self.btnChoosePath.setObjectName("btnChoosePath")
        self.gridLayout.addWidget(self.btnChoosePath, 5, 3, 1, 1)
        self.lineEdPath = QtWidgets.QLineEdit(exporter_template)
        self.lineEdPath.setObjectName("lineEdPath")
        self.gridLayout.addWidget(self.lineEdPath, 5, 0, 1, 3)
        self.sliderFPS_Scaling = QtWidgets.QSlider(exporter_template)
        self.sliderFPS_Scaling.setEnabled(False)
        self.sliderFPS_Scaling.setMinimum(1)
        self.sliderFPS_Scaling.setMaximum(100)
        self.sliderFPS_Scaling.setSingleStep(5)
        self.sliderFPS_Scaling.setProperty("value", 10)
        self.sliderFPS_Scaling.setOrientation(QtCore.Qt.Horizontal)
        self.sliderFPS_Scaling.setObjectName("sliderFPS_Scaling")
        self.gridLayout.addWidget(self.sliderFPS_Scaling, 2, 1, 1, 3)
        self.radioFromViewer = QtWidgets.QRadioButton(exporter_template)
        self.radioFromViewer.setEnabled(False)
        self.radioFromViewer.setObjectName("radioFromViewer")
        self.gridLayout.addWidget(self.radioFromViewer, 4, 1, 1, 3)
        self.radioAuto = QtWidgets.QRadioButton(exporter_template)
        self.radioAuto.setEnabled(False)
        self.radioAuto.setChecked(True)
        self.radioAuto.setObjectName("radioAuto")
        self.gridLayout.addWidget(self.radioAuto, 3, 1, 1, 3)
        self.btnExport = QtWidgets.QPushButton(exporter_template)
        self.btnExport.setObjectName("btnExport")
        self.gridLayout.addWidget(self.btnExport, 6, 1, 1, 1)

        self.retranslateUi(exporter_template)
        QtCore.QMetaObject.connectSlotsByName(exporter_template)
        exporter_template.setTabOrder(self.comboBoxFormat, self.sliderFPS_Scaling)
        exporter_template.setTabOrder(self.sliderFPS_Scaling, self.radioAuto)
        exporter_template.setTabOrder(self.radioAuto, self.radioFromViewer)
        exporter_template.setTabOrder(self.radioFromViewer, self.lineEdPath)
        exporter_template.setTabOrder(self.lineEdPath, self.btnChoosePath)

    def retranslateUi(self, exporter_template):
        _translate = QtCore.QCoreApplication.translate
        exporter_template.setWindowTitle(_translate("exporter_template", "Form"))
        self.label.setText(_translate("exporter_template", "Format"))
        self.label_4.setText(_translate("exporter_template", "fps scaling"))
        self.labelSlider.setText(_translate("exporter_template", "TextLabel"))
        self.label_3.setToolTip(_translate("exporter_template", "Lookup table min & max, only for non-tiff files."))
        self.label_3.setText(_translate("exporter_template", "LUT limits:"))
        self.btnChoosePath.setText(_translate("exporter_template", "..."))
        self.lineEdPath.setPlaceholderText(_translate("exporter_template", "path"))
        self.sliderFPS_Scaling.setToolTip(_translate("exporter_template", "Speed up or slow down the framerate (only for video and gifs)"))
        self.radioFromViewer.setToolTip(_translate("exporter_template", "From the current min & max as set in the viewer window"))
        self.radioFromViewer.setText(_translate("exporter_template", "From viewer"))
        self.radioAuto.setToolTip(_translate("exporter_template", "From meta-data (if any)"))
        self.radioAuto.setText(_translate("exporter_template", "Auto"))
        self.btnExport.setText(_translate("exporter_template", "Export"))

