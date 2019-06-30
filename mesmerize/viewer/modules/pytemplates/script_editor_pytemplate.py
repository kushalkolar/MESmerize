# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_files/script_editor.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ViewerScriptEditor(object):
    def setupUi(self, ViewerScriptEditor):
        ViewerScriptEditor.setObjectName("ViewerScriptEditor")
        ViewerScriptEditor.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(ViewerScriptEditor)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 2)
        ViewerScriptEditor.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ViewerScriptEditor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        ViewerScriptEditor.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ViewerScriptEditor)
        self.statusbar.setObjectName("statusbar")
        ViewerScriptEditor.setStatusBar(self.statusbar)
        self.actionNew = QtWidgets.QAction(ViewerScriptEditor)
        self.actionNew.setObjectName("actionNew")
        self.actionOpen = QtWidgets.QAction(ViewerScriptEditor)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(ViewerScriptEditor)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_as = QtWidgets.QAction(ViewerScriptEditor)
        self.actionSave_as.setObjectName("actionSave_as")
        self.actionRun = QtWidgets.QAction(ViewerScriptEditor)
        self.actionRun.setObjectName("actionRun")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_as)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionRun)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(ViewerScriptEditor)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(ViewerScriptEditor)

    def retranslateUi(self, ViewerScriptEditor):
        _translate = QtCore.QCoreApplication.translate
        ViewerScriptEditor.setWindowTitle(_translate("ViewerScriptEditor", "MainWindow"))
        self.menuFile.setTitle(_translate("ViewerScriptEditor", "&File"))
        self.actionNew.setText(_translate("ViewerScriptEditor", "&New"))
        self.actionNew.setShortcut(_translate("ViewerScriptEditor", "Ctrl+N"))
        self.actionOpen.setText(_translate("ViewerScriptEditor", "&Open"))
        self.actionOpen.setShortcut(_translate("ViewerScriptEditor", "Ctrl+O"))
        self.actionSave.setText(_translate("ViewerScriptEditor", "&Save"))
        self.actionSave.setShortcut(_translate("ViewerScriptEditor", "Ctrl+S"))
        self.actionSave_as.setText(_translate("ViewerScriptEditor", "S&ave as"))
        self.actionSave_as.setShortcut(_translate("ViewerScriptEditor", "Ctrl+Shift+S"))
        self.actionRun.setText(_translate("ViewerScriptEditor", "&Run"))
        self.actionRun.setShortcut(_translate("ViewerScriptEditor", "F5"))

