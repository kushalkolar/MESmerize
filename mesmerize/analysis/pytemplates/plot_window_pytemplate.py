# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/plot_window_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 30))
        self.menubar.setObjectName("menubar")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuAdvanced = QtWidgets.QMenu(self.menubar)
        self.menuAdvanced.setObjectName("menuAdvanced")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidgetTransmissions = QtWidgets.QDockWidget(MainWindow)
        self.dockWidgetTransmissions.setMinimumSize(QtCore.QSize(219, 50))
        self.dockWidgetTransmissions.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidgetTransmissions.setObjectName("dockWidgetTransmissions")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockWidgetTransmissions.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidgetTransmissions)
        self.actionTranmissions_Tree = QtWidgets.QAction(MainWindow)
        self.actionTranmissions_Tree.setCheckable(True)
        self.actionTranmissions_Tree.setChecked(True)
        self.actionTranmissions_Tree.setObjectName("actionTranmissions_Tree")
        self.menuView.addAction(self.actionTranmissions_Tree)
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuAdvanced.menuAction())

        self.retranslateUi(MainWindow)
        self.actionTranmissions_Tree.toggled['bool'].connect(self.dockWidgetTransmissions.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuView.setTitle(_translate("MainWindow", "&View"))
        self.menuAdvanced.setTitle(_translate("MainWindow", "Adva&nced"))
        self.dockWidgetTransmissions.setWindowTitle(_translate("MainWindow", "T&ranmissions w/ ordered history"))
        self.actionTranmissions_Tree.setText(_translate("MainWindow", "&Tranmissions Tree"))

from ...pyqtgraphCore import PlotWidget
