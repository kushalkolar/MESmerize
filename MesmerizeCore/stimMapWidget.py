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


class stimMapWindow(QtWidgets.QWidget):
    def __init__(self, voltagesDict):
        super().__init__()
        self.voltagesDict = voltagesDict
        self.tabs = QtWidgets.QTabWidget()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        for channel in voltagesDict.keys():
            self.tabs.addTab(stimMapGUI(self.tabs), channel)
            # Setup the GUI in that tab
            self.tabs.widget(self.tabs.count() -1).setupGUI(voltagesDict[channel], channel)
            self.tabs.widget(self.tabs.count() -1).ui.setMapBtn.clicked.connect(self.getStimMap)

    def getStimMap(self):
        mes_maps = {}
        for c in range(0,self.tabs.count()):
            d = {}
            for i in range(0,len(self.tabs.widget(c).ui.labelVoltage)):
                d[self.tabs.widget(c).ui.labelVoltage[i].text()] = \
                    [str(self.tabs.widget(c).ui.aux_1_stimBox[i].currentText()) +
                     str(self.tabs.widget(c).ui.stimLineEdit[i].text()),
                     self.tabs.widget(c).ui.aux_1_colorBtn[i].color()]

            mes_maps[self.tabs.widget(c).ui.titleLabelChannel.objectName()] = d
        return mes_maps


class stimMapGUI(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)

    def setupGUI(self, voltList, channel):
        self.ui = Ui_Form()
        self.ui.setupUi(self, voltList, channel)
    # Returns the stimulus definitions as a dictionary where the keys are the voltages.

        #bah = ['1', '2', '3']
        #func = getattr(self, 'ui.aux_1_substimBox_5.addItems(["1"])')
        #func()
        #method_to_call = getattr(self, 'ui.aux_1_stimBox_1')
        #method_to_call.addItems(bah)
        
# For testing
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = stimMapWindow(mesfile.voltDict)
    win.resize(520,120)
    win.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
#    window = QtGui.QMainWindow()
#    window.resize(520,120)
#    gui = stimMapGUI()
#    gui.ui.setupUi(gui,[1,2,3,4])
#    window.setCentralWidget(gui)
#    window.show()
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QtGui.QApplication.instance().exec_()
    