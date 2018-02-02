# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stimMap_one_row.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore import ColorButton

class Ui_Form(object):
    def setupUi(self, Form, voltList, channel, proj_channel_names):
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

        self.titleLabelChannel = QtWidgets.QLabel(Form)
        self.titleLabelChannel.setGeometry(QtCore.QRect(18, 21, 120, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.titleLabelChannel.setFont(font)
        self.titleLabelChannel.setText(channel+' : ')
        self.titleLabelChannel.setObjectName(channel)



        self.lineEdChannelName = QtWidgets.QLineEdit(Form)
        self.lineEdChannelName.setGeometry(QtCore.QRect(130, 16, 200, 30))
        self.lineEdChannelName.setToolTip("Enter a name for the this Auxiliary channel")
        self.lineEdChannelName.setPlaceholderText("Enter Channel Name")
        autocompleter = QtGui.QCompleter(proj_channel_names, self.lineEdChannelName)
        self.lineEdChannelName.setCompleter(autocompleter)
        self.lineEdChannelName.setObjectName("lineEdChannelName")

        self.checkBoxAutoColor = QtWidgets.QCheckBox(Form)
        self.checkBoxAutoColor.setGeometry(QtCore.QRect(463, 30, 15, 15))

        self.checkBoxAutoColor_label = QtWidgets.QLabel(Form)
        self.checkBoxAutoColor_label.setGeometry(390, 27, 70, 20)
        self.checkBoxAutoColor_label.setText('Auto Color :')
        self.checkBoxAutoColor.setChecked(True)

        self.titleLabelColor = QtWidgets.QLabel(Form)
        self.titleLabelColor.setGeometry(QtCore.QRect(433, 50, 40, 18))
        self.titleLabelColor.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabelColor.setObjectName("titleLabelColor")

        self.titleLabelStimulus = QtWidgets.QLabel(Form)
        self.titleLabelStimulus.setGeometry(QtCore.QRect(90, 50, 58, 18))
        self.titleLabelStimulus.setObjectName("titleLabelStimulus")

        self.setMapBtn = QtWidgets.QPushButton(Form)
        self.setMapBtn.setGeometry(QtCore.QRect(315, (113 + (len(voltList) - 1) * 30), 181, 26))
        self.setMapBtn.setObjectName("setMapBtn")
        self.setMapBtn.setToolTip("This will set the entered Maps for EVERY CHANNEL, NOT just for < " + channel + " > on the current page.")

        self.exportBtn = QtWidgets.QPushButton(Form)
        self.exportBtn.setGeometry(QtCore.QRect(63, (113 + (len(voltList) -1) * 30), 60, 26))
        self.exportBtn.setObjectName("exportBtn")
        self.exportBtn.setText("Export")
        self.exportBtn.setToolTip("Export this map as a pickle?")

        self.importBtn = QtWidgets.QPushButton(Form)
        self.importBtn.setGeometry(QtCore.QRect(132, (113 + (len(voltList) - 1) * 30), 60, 26))
        self.importBtn.setObjectName("importBtn")
        self.importBtn.setText("Import")
        self.importBtn.setToolTip("Import a map you've saved?")

      #  self.checkBoxSetAll.se
        self.widget = []
        self.horizontalLayout = []
        self.labelVoltage = []
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
            self.labelVoltage.append(QtWidgets.QLabel(self.widget[r]))
            self.labelVoltage[r].setToolTip("Voltage pulled from the opened mes file")
            self.labelVoltage[r].setAlignment(QtCore.Qt.AlignCenter)
            self.labelVoltage[r].setObjectName("labelVoltage"+str(r))
            self.labelVoltage[r].setText(str(voltList[r]))
            self.horizontalLayout[r].addWidget(self.labelVoltage[r])
            self.aux_1_stimBox.append(QtWidgets.QComboBox(self.widget[r]))
            self.aux_1_stimBox[r].setMinimumSize(QtCore.QSize(160, 0))
            self.aux_1_stimBox[r].setMaxVisibleItems(20)
            self.aux_1_stimBox[r].setObjectName("aux_1_stimBox"+str(r))
            self.horizontalLayout[r].addWidget(self.aux_1_stimBox[r])

            self.stimLineEdit.append(QtWidgets.QLineEdit(self.widget[r]))
            self.stimLineEdit[r].setToolTip("Enter stimulus if it\'s not already in the drop-down menu")
            self.stimLineEdit[r].setPlaceholderText("New Stim")
            self.stimLineEdit[r].setObjectName("stimLineEdit")
            self.stimLineEdit[r].setMinimumSize(QtCore.QSize(150,0))
            self.horizontalLayout[r].addWidget(self.stimLineEdit[r])

            self.aux_1_colorBtn.append(ColorButton())
            sizePolicy.setHeightForWidth(self.aux_1_colorBtn[r].sizePolicy().hasHeightForWidth())
            self.aux_1_colorBtn[r].setSizePolicy(sizePolicy)
            self.aux_1_colorBtn[r].setMinimumSize(QtCore.QSize(10, 0))
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
        self.setMapBtn.setText(_translate("Form", "Set ALL Maps!"))
