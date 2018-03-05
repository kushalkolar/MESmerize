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
import scipy
import pandas as pd
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
if __name__ == '__main__':
    import mainwindow_pytemplate as uiWin
    from DataTypes import Transmission
else:
    from . import mainwindow_pytemplate as uiWin
    from .DataTypes import Transmission
from pyqtgraphCore.console import ConsoleWidget


class Window(QtWidgets.QMainWindow, uiWin.Ui_MainWindow):
    def __init__(self, parent=None, *args):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Analyze')

        ns = {'np': np,
              'scipy': scipy,
              'pd': pd,
              }

        txt = "Namespaces:\nTabsWidget as 'w'\nnumpy as 'np'\nEntire " +\
              "tabbed area as 'tabsW'\n\nTo access plots in current tab call curr_tab()\nExample:\n" \
              "tab0 = curr_tab()\ntab0.p1.plot(x, np.sin(x))"

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile='./test_history.pik'))

        self.dockConsole.hide()

        self.fc = Flowchart(terminals={'dataIn': {'io': 'in'}, 'dataOut': {'io': 'out'}})

        self.fc_widget = self.fc.widget()

        self.dockFcWidget.setWidget(self.fc_widget)

        self.setCentralWidget(self.fc_widget.chartWidget)

# class TabsWidget(QtWidgets.QWidget):
#     def __init__(self, parent=None, *args):
#         QtWidgets.QWidget.__init__(self, parent, *args)
#         self.tabs = QtWidgets.QTabWidget()
#
#         # tabs_widget_ref = weakref.ref(self.tabs)
#         # plot_refs.set(self.tabs)
#         # print(plot_refs.tabs_widget_ref)
#
#         layout = QtWidgets.QVBoxLayout(self)
#         layout.addWidget(self.tabs)
#         self.tabs.addTab(TabPage(), 'Root')
#         root = self.tabs.widget(0)
#
#     def addTab(self):
#         self.tabs.addTab(TabPage(), 'bah')
#         self.tabs.setCurrentIndex(self.tabs.count() -1)
#
#
# class TabPage(QtWidgets.QWidget, uiPlots.Ui_Form):
#     def __init__(self, parent=None, *args):
#         QtWidgets.QWidget.__init__(self, parent, *args)
#         self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    analyzer_gui = Window()
    analyzer_gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()