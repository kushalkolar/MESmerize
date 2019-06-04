# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/system_config.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(663, 531)
        Form.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBoxThreads = QtWidgets.QSpinBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxThreads.sizePolicy().hasHeightForWidth())
        self.spinBoxThreads.setSizePolicy(sizePolicy)
        self.spinBoxThreads.setMinimum(1)
        self.spinBoxThreads.setMaximum(999)
        self.spinBoxThreads.setObjectName("spinBoxThreads")
        self.horizontalLayout.addWidget(self.spinBoxThreads)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.lineEditPythonCall = QtWidgets.QLineEdit(Form)
        self.lineEditPythonCall.setObjectName("lineEditPythonCall")
        self.horizontalLayout_2.addWidget(self.lineEditPythonCall)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.checkBoxUseCUDA = QtWidgets.QCheckBox(Form)
        self.checkBoxUseCUDA.setObjectName("checkBoxUseCUDA")
        self.horizontalLayout_6.addWidget(self.checkBoxUseCUDA)
        self.pushButtonCUDAError = QtWidgets.QPushButton(Form)
        self.pushButtonCUDAError.setObjectName("pushButtonCUDAError")
        self.horizontalLayout_6.addWidget(self.pushButtonCUDAError)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.plainTextEditPreCommands = QtWidgets.QPlainTextEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.plainTextEditPreCommands.sizePolicy().hasHeightForWidth())
        self.plainTextEditPreCommands.setSizePolicy(sizePolicy)
        self.plainTextEditPreCommands.setObjectName("plainTextEditPreCommands")
        self.verticalLayout.addWidget(self.plainTextEditPreCommands)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButtonResetDefaults = QtWidgets.QPushButton(Form)
        self.pushButtonResetDefaults.setObjectName("pushButtonResetDefaults")
        self.horizontalLayout_3.addWidget(self.pushButtonResetDefaults)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.btnReloadConfigFile = QtWidgets.QPushButton(Form)
        self.btnReloadConfigFile.setObjectName("btnReloadConfigFile")
        self.horizontalLayout_3.addWidget(self.btnReloadConfigFile)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.btnClose = QtWidgets.QPushButton(Form)
        self.btnClose.setObjectName("btnClose")
        self.horizontalLayout_3.addWidget(self.btnClose)
        self.btnApply = QtWidgets.QPushButton(Form)
        self.btnApply.setObjectName("btnApply")
        self.horizontalLayout_3.addWidget(self.btnApply)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.spinBoxThreads, self.btnReloadConfigFile)
        Form.setTabOrder(self.btnReloadConfigFile, self.btnClose)
        Form.setTabOrder(self.btnClose, self.btnApply)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Maximum number of threads to use:"))
        self.label_3.setText(_translate("Form", "Python call:"))
        self.lineEditPythonCall.setToolTip(_translate("Form", "Depending on how you have installed Mesmerize \n"
"you may wish to call python or python3.\n"
"Python3 should work in all circumstances.\n"
"In certain situations such as when you have\n"
" installed Mesmerize from a snap there is no \n"
"symbolic link to python3."))
        self.lineEditPythonCall.setText(_translate("Form", "python3"))
        self.checkBoxUseCUDA.setText(_translate("Form", "Use CUDA cores when possible"))
        self.pushButtonCUDAError.setText(_translate("Form", "See details"))
        self.label_2.setText(_translate("Form", "Any prior commands to run for computations performed in separate processes (such as batch items)"))
        self.plainTextEditPreCommands.setPlainText(_translate("Form", "# For example if you are running in an anaconda environment\n"
"# export PATH=\"/home/<user>/anaconda3:$PATH\"\n"
"# source activate my_environment\n"
"# Or if you are using a python virtual environment\n"
"# source /home/<user>/python_envs/my_venv/bin/activate\n"
"# Adjust these according to what\'s optimal for your hardware\n"
"export MKL_NUM_THREADS=1\n"
"export OPENBLAS_NUM_THREADS=1"))
        self.pushButtonResetDefaults.setText(_translate("Form", "Reset defaults"))
        self.btnReloadConfigFile.setText(_translate("Form", "Reload Config File"))
        self.btnClose.setText(_translate("Form", "Close"))
        self.btnApply.setText(_translate("Form", "Apply"))

