#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtGui, QtWidgets
from .pytemplates.script_editor_pytemplate import Ui_ViewerScriptEditor
from .script_editor_modules.syntax_editor import Highlighter
import os
from ...common.qdialogs import *
from ...common.configuration import HOME


class ModuleGUI(QtWidgets.QMainWindow):
    def __init__(self, parent, viewer_reference):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.parent = parent
        self.console = parent.console
        self.ui = Ui_ViewerScriptEditor()
        self.ui.setupUi(self)
        self.open_temp_script()

        self.connect_actions()

        # self.ui.pushButtonRun.clicked.connect(self.run_in_console)
        self.ui.actionRun.triggered.connect(self.run_in_console)
        self.setWindowTitle('Viewer - Script editor')

    def connect_actions(self):
        self.ui.actionNew.triggered.connect(self.new_file)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave.triggered.connect(self.save_file)

    def run_in_console(self):
        text = self.ui.tabWidget.currentWidget().toPlainText()
        self.console.runCmd(text)

    def create_editor(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        editor = QtWidgets.QTextEdit()
        editor.setFont(font)

        return editor

    def add_tab(self, file_path) -> QtWidgets.QTextEdit:
        editor = self.create_editor()
        self.ui.tabWidget.addTab(editor, file_path)
        self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count() - 1)
        if not os.path.isfile(file_path):
            open(file_path, 'w').close()
            text = ''
        elif os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                text = f.read()
        else:
            QtWidgets.QMessageBox.warning(self, 'Invalid file', 'The file path is invalid, maybe it is a directory')
        self.ui.tabWidget.currentWidget().highlighter = Highlighter(editor.document())
        self.ui.tabWidget.currentWidget().setPlainText(text)
        return self.ui.tabWidget.currentWidget()

    def open_temp_script(self):
        home_dir = os.environ['HOME']
        tmp_script = home_dir + '/mtemp.py'
        if not os.path.isfile(tmp_script):
            open(tmp_script, 'w').close()
        self.add_tab(tmp_script)

    def save_file(self):
        path = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        text = self.ui.tabWidget.currentWidget().toPlainText()
        with open(path, 'w') as f:
            f.write(text)

    def new_file(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create a new file', os.environ[HOME], '(*.py)')
        if path == '':
            return
        if path[0].endswith('.py'):
            path = path[0]
        else:
            path = path[0] + '.py'

        self.add_tab(path)

    def open_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', os.environ[HOME], '(*.py)')
        if path == '':
            return
        self.add_tab(path[0])

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ModuleGUI()
    w.show()
    app.exec_()