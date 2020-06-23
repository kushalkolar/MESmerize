# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './caiman_importer_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(595, 154)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_select_file = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_select_file.setObjectName("pushButton_select_file")
        self.horizontalLayout_2.addWidget(self.pushButton_select_file)
        self.label_file = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_file.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_file.setObjectName("label_file")
        self.horizontalLayout_2.addWidget(self.label_file)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_import = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_import.setObjectName("pushButton_import")
        self.horizontalLayout_3.addWidget(self.pushButton_import)
        spacerItem1 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Cai&man HDF5 Importer"))
        self.label.setText(_translate("DockWidget", "Import an HDF5 results file produced by Caiman to place ROIs in the current work environment"))
        self.pushButton_select_file.setToolTip(_translate("DockWidget", "Choose a dir containing suite2p output data"))
        self.pushButton_select_file.setText(_translate("DockWidget", "select file"))
        self.label_file.setText(_translate("DockWidget", "<not selected>"))
        self.pushButton_import.setText(_translate("DockWidget", "Import"))

