# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './add_to_project_dialog_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(311, 446)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lineEditAnimalID = QtWidgets.QLineEdit(Form)
        self.lineEditAnimalID.setObjectName("lineEditAnimalID")
        self.verticalLayout.addWidget(self.lineEditAnimalID)
        self.lineEditTrialID = QtWidgets.QLineEdit(Form)
        self.lineEditTrialID.setObjectName("lineEditTrialID")
        self.verticalLayout.addWidget(self.lineEditTrialID)
        self.textBoxComments = QtWidgets.QPlainTextEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBoxComments.sizePolicy().hasHeightForWidth())
        self.textBoxComments.setSizePolicy(sizePolicy)
        self.textBoxComments.setObjectName("textBoxComments")
        self.verticalLayout.addWidget(self.textBoxComments)
        self.radioButtonAddToDataFrame = QtWidgets.QRadioButton(Form)
        self.radioButtonAddToDataFrame.setChecked(True)
        self.radioButtonAddToDataFrame.setObjectName("radioButtonAddToDataFrame")
        self.verticalLayout.addWidget(self.radioButtonAddToDataFrame)
        self.radioButtonSaveChanges = QtWidgets.QRadioButton(Form)
        self.radioButtonSaveChanges.setObjectName("radioButtonSaveChanges")
        self.verticalLayout.addWidget(self.radioButtonSaveChanges)
        self.checkBoxSaveChanges = QtWidgets.QCheckBox(Form)
        self.checkBoxSaveChanges.setEnabled(False)
        self.checkBoxSaveChanges.setObjectName("checkBoxSaveChanges")
        self.verticalLayout.addWidget(self.checkBoxSaveChanges)
        self.checkBoxOverwriteImage = QtWidgets.QCheckBox(Form)
        self.checkBoxOverwriteImage.setEnabled(False)
        self.checkBoxOverwriteImage.setChecked(True)
        self.checkBoxOverwriteImage.setObjectName("checkBoxOverwriteImage")
        self.verticalLayout.addWidget(self.checkBoxOverwriteImage)
        self.btnProceed = QtWidgets.QPushButton(Form)
        self.btnProceed.setObjectName("btnProceed")
        self.verticalLayout.addWidget(self.btnProceed)

        self.retranslateUi(Form)
        self.radioButtonSaveChanges.toggled['bool'].connect(self.checkBoxSaveChanges.setEnabled)
        self.radioButtonSaveChanges.toggled['bool'].connect(self.checkBoxSaveChanges.setVisible)
        self.radioButtonSaveChanges.toggled['bool'].connect(self.checkBoxOverwriteImage.setEnabled)
        self.radioButtonSaveChanges.toggled['bool'].connect(self.checkBoxOverwriteImage.setVisible)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lineEditAnimalID.setPlaceholderText(_translate("Form", "*Animal ID"))
        self.lineEditTrialID.setPlaceholderText(_translate("Form", "*Trial ID"))
        self.textBoxComments.setPlaceholderText(_translate("Form", "Comments"))
        self.radioButtonAddToDataFrame.setText(_translate("Form", "Add to dataframe"))
        self.radioButtonSaveChanges.setText(_translate("Form", "Save changes (overwrite)"))
        self.checkBoxSaveChanges.setText(_translate("Form", "I\'m sure!"))
        self.checkBoxOverwriteImage.setToolTip(_translate("Form", "If you have not changed the actual image sequence you can save time by selecting this option."))
        self.checkBoxOverwriteImage.setText(_translate("Form", "Overwrite image data"))
        self.btnProceed.setText(_translate("Form", "Proceed"))

