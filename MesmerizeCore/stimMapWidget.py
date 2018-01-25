#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 22:50:23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Just a simple GUI for mapping any auxiliary voltage information to stimulus definitions.
"""

import sys
sys.path.append('..')
if __name__ == '__main__':
    #from stimMap_template import *
    from stimMap_one_row_pytemplate import *
else:
    from .stimMap_one_row_pytemplate import *
from pyqtgraphCore.Qt import QtCore, QtGui, USE_PYSIDE, QtWidgets
import types


class stimMapGUI(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)
        self.ui = Ui_Form()

    # Returns the stimulus definitions as a dictionary where the keys are the voltages.
    def getStimMap(self):
        d = {}
        for i in range(0,len(self.ui.aux_1_volt_label)):
            d[self.ui.aux_1_volt_label[i].text()] = [str(self.ui.aux_1_stimBox[i].currentText()) + 
              str(self.ui.stimLineEdit[i].text()) + '//' + str(self.ui.substimLineEdit[i].text()), 
              self.ui.aux_1_colorBtn[i].color()]
        return d
    
        #bah = ['1', '2', '3']
        #func = getattr(self, 'ui.aux_1_substimBox_5.addItems(["1"])')
        #func()
        #method_to_call = getattr(self, 'ui.aux_1_stimBox_1')
        #method_to_call.addItems(bah)
        
# For testing
if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.resize(520,120)
    gui = stimMapGUI()
    gui.ui.setupUi(gui,[1,2,3,4])
    window.setCentralWidget(gui)
    window.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    