# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'startwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(448, 88)
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 10, 424, 64))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.newProjBtn = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newProjBtn.sizePolicy().hasHeightForWidth())
        self.newProjBtn.setSizePolicy(sizePolicy)
        self.newProjBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.newProjBtn.setObjectName("newProjBtn")
        self.horizontalLayout.addWidget(self.newProjBtn)
        self.openProjBtn = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openProjBtn.sizePolicy().hasHeightForWidth())
        self.openProjBtn.setSizePolicy(sizePolicy)
        self.openProjBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.openProjBtn.setObjectName("openProjBtn")
        self.horizontalLayout.addWidget(self.openProjBtn)
        self.openViewerBtn = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.openViewerBtn.sizePolicy().hasHeightForWidth())
        self.openViewerBtn.setSizePolicy(sizePolicy)
        self.openViewerBtn.setMaximumSize(QtCore.QSize(100, 16777215))
        self.openViewerBtn.setObjectName("openViewerBtn")
        self.horizontalLayout.addWidget(self.openViewerBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Choose how you want to be Mesmerized!"))
        self.newProjBtn.setText(_translate("Dialog", "New"))
        self.openProjBtn.setText(_translate("Dialog", "Open"))
        self.openViewerBtn.setText(_translate("Dialog", "Open Viewer"))

