#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 21:13:39 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import sys
sys.path.append('..')

from pyqtgraphCore.Qt import QtCore, QtGui

if __name__ == '__main__':
    from startWindow_pytemplate import *
else:
    from .startWindow_pytemplate import *

class startGUI(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
if __name__ == '__main__':
    app = QtGui.QApplication([]) 
    startWin = QtGui.QMainWindow()
    startWin.resize(448,88)
    startgui = startGUI()
    startWin.setCentralWidget(startgui)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()