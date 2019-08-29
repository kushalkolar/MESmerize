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
from PyQt5 import QtWidgets
from PyQt5.QtGui import QCursor
from ..pyqtgraphCore.flowchart import Flowchart
import numpy as np
import pandas as pd
from .pytemplates import mainwindow_pytemplate as uiWin
from ..pyqtgraphCore.console import ConsoleWidget
from ..common import configuration
import os


class Window(QtWidgets.QMainWindow, uiWin.Ui_MainWindow):
    def __init__(self, parent=None, filename: str = None):
        super().__init__()
        self.setupUi(self)

        self.dockConsole.hide()

        self.fc = Flowchart(terminals={'dataIn': {'io': 'in'}, 'dataOut': {'io': 'out'}})

        self.fc_widget = self.fc.widget()
        self.fc.setParent(self)

        ns = {'np': np,
              'pd': pd,
              'get_nodes': self.fc.nodes,
              'this': self
              }

        txt = "Namespaces:\n" \
              "pandas as 'pd'\n" \
              "numpy as 'np'\n" \
              "self as 'this'\n" \
              "'get_nodes()' to get a dict of all nodes\n"

        cmd_history_path = os.path.join(configuration.console_history_path, 'flowchart.pik')

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_path))
        # self.resizeDocks([self.dockConsole], [235], QtCore.Qt.Vertical)

        self.dockFcWidget.setWidget(self.fc_widget)

        self.setCentralWidget(self.fc_widget.chartWidget)

        if filename is not None:
            self.fc.loadFile(filename)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, QDragEnterEvent):
        if QDragEnterEvent.mimeData().hasUrls():
            QDragEnterEvent.accept()
        else:
            QDragEnterEvent.ignore()

    def dropEvent(self, ev):
        files = ev.mimeData().urls()
        if len(files) == 1:
            file = files[0].path()
        else:
            return

        if file.endswith('.trn') or file.endswith('.ptrn'):
            fname = os.path.splitext(os.path.basename(file))[0]
            from_global = self.fc_widget.chartWidget.view.mapFromGlobal(QCursor().pos())
            pos = self.fc_widget.chartWidget.view.mapToScene(from_global)
            self.fc.createNode('LoadFile', name=fname, pos=pos)
            self.fc.nodes()[fname].load_file(file)
