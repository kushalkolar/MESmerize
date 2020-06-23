# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/suite2p_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidgetSuite2p(object):
    def setupUi(self, DockWidgetSuite2p):
        DockWidgetSuite2p.setObjectName("DockWidgetSuite2p")
        DockWidgetSuite2p.resize(735, 386)
        DockWidgetSuite2p.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_dir = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_dir.setObjectName("pushButton_dir")
        self.horizontalLayout_2.addWidget(self.pushButton_dir)
        self.label_dir = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_dir.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.label_dir.setObjectName("label_dir")
        self.horizontalLayout_2.addWidget(self.label_dir)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.spinBox_Fneu_sub = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBox_Fneu_sub.setMaximum(100)
        self.spinBox_Fneu_sub.setSingleStep(10)
        self.spinBox_Fneu_sub.setProperty("value", 70)
        self.spinBox_Fneu_sub.setObjectName("spinBox_Fneu_sub")
        self.horizontalLayout_10.addWidget(self.spinBox_Fneu_sub)
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.horizontalLayout_10.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.checkBox_use_iscell = QtWidgets.QCheckBox(self.dockWidgetContents)
        self.checkBox_use_iscell.setObjectName("checkBox_use_iscell")
        self.verticalLayout.addWidget(self.checkBox_use_iscell)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_import = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButton_import.setObjectName("pushButton_import")
        self.horizontalLayout_3.addWidget(self.pushButton_import)
        spacerItem2 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        DockWidgetSuite2p.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetSuite2p)
        QtCore.QMetaObject.connectSlotsByName(DockWidgetSuite2p)
        DockWidgetSuite2p.setTabOrder(self.pushButton_dir, self.spinBox_Fneu_sub)
        DockWidgetSuite2p.setTabOrder(self.spinBox_Fneu_sub, self.checkBox_use_iscell)
        DockWidgetSuite2p.setTabOrder(self.checkBox_use_iscell, self.pushButton_import)

    def retranslateUi(self, DockWidgetSuite2p):
        _translate = QtCore.QCoreApplication.translate
        DockWidgetSuite2p.setWindowTitle(_translate("DockWidgetSuite2p", "S&uite2p importer"))
        self.label_2.setText(_translate("DockWidgetSuite2p", "Select the directory which contains the Suite2p output data that corresponds to the current image sequence.\n"
"\n"
"The dir must contain the following files:\n"
"  F.npy\n"
"  Fneu.npy\n"
"  stat.npy\n"
"  ops.npy\n"
"  iscell.npy"))
        self.pushButton_dir.setToolTip(_translate("DockWidgetSuite2p", "Choose a dir containing suite2p output data"))
        self.pushButton_dir.setText(_translate("DockWidgetSuite2p", "select dir"))
        self.label_dir.setText(_translate("DockWidgetSuite2p", "<not selected>"))
        self.spinBox_Fneu_sub.setToolTip(_translate("DockWidgetSuite2p", "substracts this much of Fneu from F to get the final trace"))
        self.label.setText(_translate("DockWidgetSuite2p", "Fneu substraction (%)"))
        self.checkBox_use_iscell.setText(_translate("DockWidgetSuite2p", "only import ROIs that were classified as cells by suite2p (uses iscell.npy)"))
        self.pushButton_import.setText(_translate("DockWidgetSuite2p", "Import"))

