#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 18 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .main_widget import ProjectBrowserWidget
from pyqtgraphCore.console import ConsoleWidget
from .pytemplates.mainwindow_pytemplate import Ui_MainWindow
from spyder.widgets.variableexplorer.dataframeeditor import DataFrameEditor
import pandas as pd
import numpy as np
import pickle
import os
from common import configuration


class ProjectBrowserWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.project_browser = ProjectBrowserWidget(self, configuration.project_manager.dataframe)
        self.setCentralWidget(self.project_browser)

        ns = {'pd': pd,
              'np': np,
              'pickle': pickle,
              'project_browser': self.project_browser,
              'main': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as pickle    \n" \
              "self.window_manager as window_manager     \n" \
              "self as main         \n" \

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/project_browser.pik'

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))

        self.ui.dockConsole.hide()