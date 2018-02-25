#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
# sys.path.append('..')
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
if __name__ == '__main__':
    import CurvePlotWindow_pytemplate as uiWin
    import CurvePlots_pytemplate as uiPlots
else:
    from . import CurvePlotWindow_pytemplate as uiWin
    from . import CurvePlots_pytemplate as uiPlots

from pyqtgraphCore.console import ConsoleWidget
import numpy as np
import scipy


class Window(QtWidgets.QMainWindow, uiWin.Ui_MainWindow):
    def __init__(self, parent=None, *args):
        super().__init__()
        self.setupUi(self)
        self.tabbed_area = TabsWidget()
        self.setCentralWidget(self.tabbed_area)

        ns = {'np': np,
              'scipy': scipy,
              'curr_tab': self.tabbed_area.tabs.currentWidget,
              'tabsW': self.tabbed_area,
              }

        txt = "Namespaces:\nTabsWidget as 'w'\nnumpy as 'np'\nEntire " +\
              "tabbed area as 'tabsW'\n\nTo access plots in current tab call curr_tab()\nExample:\n" \
              "tab0 = curr_tab()\ntab0.p1.plot(x, np.sin(x))"

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile='./test_history.pik'))



class TabsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.tabs = QtWidgets.QTabWidget()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.tabs.addTab(TabPage(), 'Root')
        root = self.tabs.widget(0)

    def addTab(self):
        self.tabs.addTab(TabPage(), 'bah')
        self.tabs.setCurrentIndex(self.tabs.count() -1)


class TabPage(QtWidgets.QWidget, uiPlots.Ui_Form):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.setupUi(self)




if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    analyzer_gui = Window()
    analyzer_gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
