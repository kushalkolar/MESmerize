#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
import sys
sys.path.append('..')
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
if __name__ == '__main__':
    from configwindow_pytemplate import *
else:
    from .configwindow_pytemplate import *
import configparser


cfg = configparser.RawConfigParser(allow_no_value=True)
cfg.optionxform = str

def saveConfig(path):
    with open(path, 'w') as configfile:
        cfg.write(configfile)

def newConfig(path):
    defaultInclude = ['SampleID', 'Date']
    cfg['INCLUDE'] = dict.fromkeys(defaultInclude)

    defaultExclude = ['CurvePath', 'ImgInfoPath', 'ImgPath']
    cfg['EXCLUDE'] = dict.fromkeys(defaultExclude)

    cfg['ROI_DEFS'] = {}

    cfg['STIM_DEFS'] = {}

    saveConfig(path)

def openConfig(path):
    cfg.read(path)

class ColumnsPage(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)

    def setupGUI(self, path):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.path = path
        openConfig(path)
        self.ui.listwInclude.addItems(cfg.options('INCLUDE'))
        self.ui.listwExclude.addItems(cfg.options('EXCLUDE'))
        self.ui.listwROIDefs.addItems(cfg.options('ROI_DEFS'))
        self.ui.listwStimDefs.addItems(cfg.options('STIM_DEFS'))
        
        self.ui.btnAddNewROICol.clicked.connect(self._addROIDef)
        self.ui.btnAddNewStimCol.clicked.connect(self._addStimDef)

        self.ui.btnSave.clicked.connect(self._saveConfig)

    def _addROIDef(self):
        if self.ui.lineEdNewROIDef.text() != '':
            self.ui.listwROIDefs.addItem(self.ui.lineEdNewROIDef.text())
            self.ui.listwInclude.addItem(self.ui.lineEdNewROIDef.text())
            self.ui.lineEdNewROIDef.clear()
        
    def _addStimDef(self):
        if self.ui.lineEdNewStimCol.text() != '':
            self.ui.listwStimDefs.addItem(self.ui.lineEdNewStimCol.text())
            self.ui.listwInclude.addItem(self.ui.lineEdNewStimCol.text())
            self.ui.lineEdNewStimCol.clear()
    
    def _delROIDef(self):
        pass
    
    def _delStimDef(self):
        pass
    
    def _saveConfig(self):

        include = []
        for i in range(0, self.ui.listwInclude.count()):
            include.append(self.ui.listwInclude.item(i).text())
        cfg['INCLUDE'] = dict.fromkeys(include)
        
        exclude = []
        for i in range(0, self.ui.listwExclude.count()):
            exclude.append(self.ui.listwExclude.item(i).text())
        cfg['EXCLUDE'] = dict.fromkeys(exclude)
        
        roi_defs = []
        for i in range(0, self.ui.listwROIDefs.count()):
            roi_defs.append(self.ui.listwROIDefs.item(i).text())
        cfg['ROI_DEFS'] = dict.fromkeys(roi_defs)
        
        stim_defs = []
        for i in range(0, self.ui.listwStimDefs.count()):
            stim_defs.append(self.ui.listwStimDefs.item(i).text())
        cfg['STIM_DEFS'] = dict.fromkeys(stim_defs)

        saveConfig(self.path)
        self.ui.btnClose.click()

class Window(QtWidgets.QWidget):
    def __init__(self, path):
        super().__init__()
        self.tabs = QtWidgets.QTabWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        
        # Adds a new tab, places an instance of TabPage widget which is displayed in the whole tab.
        self.tabs.addTab(ColumnsPage(self.tabs), 'Columns')
        # Setup the GUI in that tab
        self.tabs.widget(self.tabs.count() - 1).setupGUI(path)

        self.tabs.widget(0).ui.btnClose.clicked.connect(self.close)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Window('/home/kushal/Sars_stuff/github-repos/MESmerize/MesmerizeCore/test-config.cfg')
    win.resize(593, 617)
    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()