#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 20:16:27 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

The Project Browser GUI. Will be used for sorting/organizing/analysing the Calcium imaging
traces
"""
import sys
sys.path.append('..')

if __name__ == '__main__':
    from ProjBrowser_pytemplate import *
else:
    from .ProjBrowser_pytemplate import *
from pyqtgraphCore.Qt import QtCore, QtGui, USE_PYSIDE
from pyqtgraphCore.graphicsItems.InfiniteLine import *
import pyqtgraphCore
import numpy as np
import os
from PyQt5.QtGui import QIcon
import pickle
import pandas as pd
from .packager import *
from itertools import chain
import ast


class ProjBrowser(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)
        
    def setupGUI(self, df):
        exclude = ['ImgPath', 'ROIhandles', 'ImgInfoPath', 'CurvePath', 
                   'Location', 'NucLocation', 'SubcellLocation']
        
        special = {'Timings': 'StimSet'}
        self.ui = Ui_Form()
        self.ui.setupUi(self, df, exclude, special)
        
        for colNum in range(0, len(self.ui.listw_)):
            if self.ui.labelColumn_[colNum].text() == 'StimSet':
                # Yes I know this is abominable. I'm open to suggestions!
                self.ui.listw_[colNum].addItems(
                                        list(set(
                                            (chain(*df[self.ui.labelColumn_[colNum].text()].apply(
                                                    lambda col:list(
                                                            ast.literal_eval(col))))))))
                
            elif self.ui.labelColumn_[colNum].text() == 'SampleID' or  'Date':
                self.ui.listw_[colNum].addItems(list(set(df[self.ui.labelColumn_[colNum].text()])))
            

        
#        self.CurrProjName = None
#        
#        self.ui.treeView.doubleClicked.connect(self.loadFile)
#        self.ui.treeView.clicked.connect(self.getSelectedPath)

#    def newProj(self):
#        parentPath = QtGui.QFileDialog.getExistingDirectory(self,'Choose location for new project')
#        print('parentPath is: ' + parentPath)
#        projName, start = QtGui.QInputDialog.getText(self, '', 'Project Name:', QtGui.QLineEdit.Normal, '')
##        start = True
##        projName = 'bah'
#        if start and projName != '':
#            self.CurrProjName = projName
#            path = parentPath + '/' + self.CurrProjName
#            os.mkdir(path)
#            self.projDataFrame = empty_df()
#            self.projDataFrameFilePath = path + '/' + self.CurrProjName + '_index.mzp'
#            self.projDataFrame.to_csv(self.projDataFrameFilePath, index=False)
#            self.setupDataframeUI()
#            
#    def openProj(self):
#        path = QtGui.QFileDialog.getOpenFileName(self, 'Select Project Index File', 
#                                                      '.', '(*.mzp)')[0]
#        print(path)
#        if path != '':
#            self.projDataFrameFilePath = path
#            self.projDataFrame = pd.read_csv(path) 
#            self.CurrProjName = path.split('/')[-1][:-4]
#            self.setupDataframeUI()
##            self.setTree('/'.join((path.split('/')[:-1])))
            
    def setupDataframeUI(self):
        self.ui.BtnPlot.setEnabled(True)
        self.ui.BtnResetFilters.setEnabled(True)
        self.ui.setupColumns(self)
        
    def setupWorkEnv(self):
        pass
        
        
#    def loadFile(self, selection):
#        pass
        
if __name__ == '__main__':
    
    app = QtGui.QApplication([])
        
    ## Create window with Project Explorer widget
    projectWindow = QtGui.QMainWindow()
    projectWindow.resize(1000,750)
    projectWindow.setWindowTitle('Mesmerize - Project Explorer')
    projBrowser = ProjBrowser()
    projectWindow.setCentralWidget(projBrowser)
    projectWindow.show()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
