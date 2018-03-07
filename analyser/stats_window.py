# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stats_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1008, 632)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setGeometry(QtCore.QRect(10, 50, 80, 26))
        self.pushButton.setObjectName("pushButton")
        self.widget = QtWidgets.QWidget(self.tab)
        self.widget.setGeometry(QtCore.QRect(11, 11, 597, 28))
        self.widget.setObjectName("widget")


        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelTransmission = QtWidgets.QLabel(self.widget)
        self.labelTransmission.setObjectName("labelTransmission")
        self.horizontalLayout.addWidget(self.labelTransmission)
        self.lineEditGroup = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditGroup.sizePolicy().hasHeightForWidth())
        self.lineEditGroup.setSizePolicy(sizePolicy)
        self.lineEditGroup.setMinimumSize(QtCore.QSize(500, 0))
        self.lineEditGroup.setMaximumSize(QtCore.QSize(500, 16777215))
        self.lineEditGroup.setBaseSize(QtCore.QSize(120, 0))
        self.lineEditGroup.setObjectName("lineEditGroup")
        self.horizontalLayout.addWidget(self.lineEditGroup)



        self.tabWidget.addTab(self.tab, "")
        self.violinPlots = QtWidgets.QWidget()
        self.violinPlots.setObjectName("violinPlots")
        self.tabWidget.addTab(self.violinPlots, "")
        self.boxPlots = QtWidgets.QWidget()
        self.boxPlots.setObjectName("boxPlots")
        self.tabWidget.addTab(self.boxPlots, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1008, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget.setMinimumSize(QtCore.QSize(225, 36))
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidget)
        self.actionSave_Statistics_DataFrame = QtWidgets.QAction(MainWindow)
        self.actionSave_Statistics_DataFrame.setObjectName("actionSave_Statistics_DataFrame")
        self.actionSave_Group_Transmissions = QtWidgets.QAction(MainWindow)
        self.actionSave_Group_Transmissions.setObjectName("actionSave_Group_Transmissions")
        self.actionLoad_Groups = QtWidgets.QAction(MainWindow)
        self.actionLoad_Groups.setObjectName("actionLoad_Groups")
        self.menuFile.addAction(self.actionSave_Statistics_DataFrame)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_Group_Transmissions)
        self.menuFile.addAction(self.actionLoad_Groups)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Set Groups"))
        self.labelTransmission.setText(_translate("MainWindow", "Transmission 0"))
        self.lineEditGroup.setPlaceholderText(_translate("MainWindow", "Group names"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Groups"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.violinPlots), _translate("MainWindow", "Violin Plots"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.boxPlots), _translate("MainWindow", "Box Plots"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave_Statistics_DataFrame.setText(_translate("MainWindow", "Save Statistics DataFrame"))
        self.actionSave_Group_Transmissions.setText(_translate("MainWindow", "Save Groups"))
        self.actionLoad_Groups.setText(_translate("MainWindow", "Load Groups"))

