#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys

sys.setrecursionlimit(10000)
from pyqtgraphCore.flowchart import Flowchart
# import pyqtgraphCore as pg
import numpy as np
import pandas as pd
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets


from .pytemplates import mainwindow_pytemplate as uiWin
from .data_types import Transmission
from pyqtgraphCore.console import ConsoleWidget
import pickle
from common import configuration
import os


class Window(QtWidgets.QMainWindow, uiWin.Ui_MainWindow):
    def __init__(self, parent=None, *args):
        super().__init__()
        self.setupUi(self)

        self.dockConsole.hide()

        self.fc = Flowchart(terminals={'dataIn': {'io': 'in'}, 'dataOut': {'io': 'out'}})

        self.fc_widget = self.fc.widget()

        ns = {'np': np,
              'pd': pd,
              'pickle': pickle,
              'get_nodes': self.fc.nodes,
              'main': self
              }

        txt = "Namespaces:\n" \
              "pickle as 'pickle'\n" \
              "numpy as 'np'\n" \
              "self as 'main'\n" \
              "'get_nodes()' to get a dict of all nodes\n"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/flowchart.pik'

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))


        self.dockFcWidget.setWidget(self.fc_widget)

        self.setCentralWidget(self.fc_widget.chartWidget)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    analyzer_gui = Window()
    analyzer_gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()
