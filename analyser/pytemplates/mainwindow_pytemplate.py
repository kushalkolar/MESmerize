# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CurvePlotWindow_template.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1209, 696)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1209, 23))
        self.menubar.setObjectName("menubar")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockFcWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockFcWidget.setMinimumSize(QtCore.QSize(264, 36))
        self.dockFcWidget.setFloating(False)
        self.dockFcWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockFcWidget.setObjectName("dockFcWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockFcWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockFcWidget)
        self.dockConsole = QtWidgets.QDockWidget(MainWindow)
        self.dockConsole.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setObjectName("dockConsole")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.dockConsole.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockConsole)
        self.actionConsole = QtWidgets.QAction(MainWindow)
        self.actionConsole.setCheckable(True)
        self.actionConsole.setObjectName("actionConsole")
        self.actionControls_Widgets = QtWidgets.QAction(MainWindow)
        self.actionControls_Widgets.setCheckable(True)
        self.actionControls_Widgets.setChecked(True)
        self.actionControls_Widgets.setObjectName("actionControls_Widgets")
        self.menuView.addAction(self.actionConsole)
        self.menuView.addAction(self.actionControls_Widgets)
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        self.actionConsole.toggled['bool'].connect(self.dockConsole.setVisible)
        self.actionControls_Widgets.toggled['bool'].connect(self.dockFcWidget.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.dockFcWidget.setWindowTitle(_translate("MainWindow", "Control Widgets"))
        self.dockConsole.setWindowTitle(_translate("MainWindow", "Console"))
        self.actionConsole.setText(_translate("MainWindow", "Console"))
        self.actionControls_Widgets.setText(_translate("MainWindow", "Controls Widgets"))

