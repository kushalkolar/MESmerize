# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        self.menuDataframe = QtWidgets.QMenu(self.menubar)
        self.menuDataframe.setObjectName("menuDataframe")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockConsole = QtWidgets.QDockWidget(MainWindow)
        self.dockConsole.setMinimumSize(QtCore.QSize(42, 200))
        self.dockConsole.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setObjectName("dockConsole")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockConsole.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockConsole)
        self.actionDataframe_editor = QtWidgets.QAction(MainWindow)
        self.actionDataframe_editor.setObjectName("actionDataframe_editor")
        self.actionConsole = QtWidgets.QAction(MainWindow)
        self.actionConsole.setCheckable(True)
        self.actionConsole.setObjectName("actionConsole")
        self.menuDataframe.addAction(self.actionDataframe_editor)
        self.menuView.addAction(self.actionConsole)
        self.menubar.addAction(self.menuDataframe.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        self.actionConsole.toggled['bool'].connect(self.dockConsole.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuDataframe.setTitle(_translate("MainWindow", "Dataframe"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.dockConsole.setWindowTitle(_translate("MainWindow", "Console: Project Browser"))
        self.actionDataframe_editor.setText(_translate("MainWindow", "Dataframe editor"))
        self.actionConsole.setText(_translate("MainWindow", "Console"))

