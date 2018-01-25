# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stimMap_one_row.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore import ColorButton

class Ui_Form(object):
    def setupUi(self, Form, voltList):
        Form.setObjectName("Form")
        Form.resize(500, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(520, (120 + len(voltList) * 30)))
        self.titleLabelVoltage = QtWidgets.QLabel(Form)
        self.titleLabelVoltage.setGeometry(QtCore.QRect(20, 50, 61, 18))
        self.titleLabelVoltage.setToolTip("")
        self.titleLabelVoltage.setStatusTip("")
        self.titleLabelVoltage.setObjectName("titleLabelVoltage")
        self.titleLabelAUXo1 = QtWidgets.QLabel(Form)
        self.titleLabelAUXo1.setGeometry(QtCore.QRect(190, 20, 111, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.titleLabelAUXo1.setFont(font)
        self.titleLabelAUXo1.setText("")
        self.titleLabelAUXo1.setObjectName("titleLabelAUXo1")
        self.titleLabelColor = QtWidgets.QLabel(Form)
        self.titleLabelColor.setGeometry(QtCore.QRect(452, 50, 40, 18))
        self.titleLabelColor.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabelColor.setObjectName("titleLabelColor")
        self.titleLabelStimulus = QtWidgets.QLabel(Form)
        self.titleLabelStimulus.setGeometry(QtCore.QRect(90, 50, 58, 18))
        self.titleLabelStimulus.setObjectName("titleLabelStimulus")
        self.setMapBtn = QtWidgets.QPushButton(Form)
        self.setMapBtn.setGeometry(QtCore.QRect(150, (120 + (len(voltList) - 1) * 30), 181, 26))
        self.setMapBtn.setObjectName("setMapBtn")
        
        self.checkBoxSetAll = QtWidgets.QCheckBox(Form)
        self.checkBoxSetAll.setGeometry(QtCore.QRect(340, (125 + (len(voltList) -1) * 30), 15, 15))
        self.labelSetAll = QtWidgets.QLabel(Form)
        self.labelSetAll.setGeometry(359, 126 + (len(voltList) -1) * 30, 150, 12)
        self.labelSetAll.setText('Set for entire mes file')
        
        
      #  self.checkBoxSetAll.se
        self.widget = []
        self.horizontalLayout = []
        self.aux_1_volt_label = []
        self.aux_1_stimBox = []
        self.aux_1_colorBtn = []
        self.stimLineEdit = []
        self.substimLineEdit = []
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(40)
        sizePolicy.setVerticalStretch(0)        
        
        for r in range(0,len(voltList)):        
            self.widget.append(QtWidgets.QWidget(Form))
            self.widget[r].setGeometry(QtCore.QRect(40, (70 + r * 30), 455, 28))
            self.widget[r].setObjectName("widget"+str(r))
            self.horizontalLayout.append(QtWidgets.QHBoxLayout(self.widget[r]))
            self.horizontalLayout[r].setContentsMargins(0, 0, 0, 0)
            self.horizontalLayout[r].setObjectName("horizontalLayout"+str(r))
            self.aux_1_volt_label.append(QtWidgets.QLabel(self.widget[r]))
            self.aux_1_volt_label[r].setToolTip("Voltage pulled from the opened mes file")
            self.aux_1_volt_label[r].setAlignment(QtCore.Qt.AlignCenter)
            self.aux_1_volt_label[r].setObjectName("aux_1_volt_label"+str(r))
            self.aux_1_volt_label[r].setText(str(voltList[r]))
            self.horizontalLayout[r].addWidget(self.aux_1_volt_label[r])
            self.aux_1_stimBox.append(QtWidgets.QComboBox(self.widget[r]))
            self.aux_1_stimBox[r].setMinimumSize(QtCore.QSize(120, 0))
            self.aux_1_stimBox[r].setMaxVisibleItems(20)
            self.aux_1_stimBox[r].setObjectName("aux_1_stimBox"+str(r))
            self.horizontalLayout[r].addWidget(self.aux_1_stimBox[r])
            self.stimLineEdit.append(QtWidgets.QLineEdit(self.widget[r]))
            self.stimLineEdit[r].setToolTip("Enter stimulus if it\'s not already in the drop-down menu")
            self.stimLineEdit[r].setPlaceholderText("New Stim")
            self.stimLineEdit[r].setObjectName("stimLineEdit")
            self.horizontalLayout[r].addWidget(self.stimLineEdit[r])
            self.substimLineEdit.append(QtWidgets.QLineEdit(self.widget[r]))
            self.substimLineEdit[r].setToolTip("Enter sub-stimulus if it\'s not already in the drop-down menu")
            self.substimLineEdit[r].setPlaceholderText("Sub-stim")
            self.substimLineEdit[r].setObjectName("substimLineEdit")
            self.horizontalLayout[r].addWidget(self.substimLineEdit[r])
            self.aux_1_colorBtn.append(ColorButton())

            sizePolicy.setHeightForWidth(self.aux_1_colorBtn[r].sizePolicy().hasHeightForWidth())
            self.aux_1_colorBtn[r].setSizePolicy(sizePolicy)
            self.aux_1_colorBtn[r].setMinimumSize(QtCore.QSize(30, 0))
            self.aux_1_colorBtn[r].setToolTip("Open color picker")
            self.aux_1_colorBtn[r].setObjectName("aux_1_colorBtn")
            self.aux_1_colorBtn[r].setText('Auto')
            self.horizontalLayout[r].addWidget(self.aux_1_colorBtn[r])

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.titleLabelVoltage.setText(_translate("Form", "Voltages"))
        self.titleLabelColor.setText(_translate("Form", "Color"))
        self.titleLabelStimulus.setText(_translate("Form", "Stimulus"))
        self.setMapBtn.setText(_translate("Form", "Set Map!"))
