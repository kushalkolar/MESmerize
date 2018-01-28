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
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.graphicsItems.InfiniteLine import *
import pyqtgraphCore
import numpy as np
import os
from PyQt5.QtGui import QIcon
import pickle
import pandas as pd
#from .packager import *
from itertools import chain
import ast
from functools import partial


class TabPage(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)
        self.filtLog = ''
        self.filtLogPandas = ''
        
    def setupGUI(self, df, exclude=[], special={}):
        
        self.df = df
        self.ui = Ui_Form()
        self.ui.setupUi(self, self.df, exclude, special)
        
        self.ui.BtnCopyFilters.clicked.connect(self.copyFilterClipboard)
        
        self.ui.BtnResetFilters.clicked.connect(self.clearAllLineEdFilters)
#        self.addBtn()
                
#    def addBtn(self):
#        self.ui.BtnConsole2 = QtWidgets.QPushButton(self)
#        self.ui.BtnConsole2.setGeometry(QtCore.QRect(200, 740, 80, 26))
#        self.ui.BtnConsole2.setObjectName("BtnConsole2")
#        self.ui.BtnConsole2.setText("bahh")
    def clearAllLineEdFilters(self):
        for lineEd in self.ui.lineEdFilter_:
            lineEd.clear()
        for listw in self.ui.listw_:
            listw.clearSelection()
            
    def updateDf(self):
        if self.df.size < 1:
            self.emptyDf()
            self.disablePlotBtns()
            return
        
        self.enablePlotBtns()
        self.minIndex = self.df.index.values.min()
        
        for col in self.ui.listw_:
            col.clear()
        
        for col in self.ui.listw_:
            try:
                print(col)
                if type(ast.literal_eval(self.df[col.objectName()][self.minIndex])) == set:
                    self.setExtract(col)
                elif type(ast.literal_eval(self.df[col.objectName()][self.minIndex])) == int:
                    self.numExtract(col)
                    
            except (ValueError, SyntaxError):
                if type(self.df[col.objectName()][self.minIndex]) == str:
                    self.strExtract(col)
                elif type(self.df[col.objectName()][self.minIndex]) is np.int64:
                    self.numExtract(col)
                elif type(self.df[col.objectName()][self.minIndex]) is np.float64:
                    self.numExtract(col)
                else:
                    self.unsupportedType(col)
    
    def enablePlotBtns(self):
        self.ui.BtnPlot.setEnabled(True)
        self.ui.BtnConsole.setEnabled(True)
        self.ui.BtnResetFilters.setEnabled(True)
        self.ui.BtnJupyter.setEnabled(True)
        self.ui.BtnCopyFilters.setEnabled(True)
        
    def disablePlotBtns(self):
        self.ui.BtnPlot.setDisabled(True)
        self.ui.BtnConsole.setDisabled(True)
        self.ui.BtnResetFilters.setDisabled(True)
        self.ui.BtnJupyter.setDisabled(True)
        self.ui.BtnCopyFilters.setDisabled(True)
        
    def setExtract(self, col):
        # Yes I know this is abominable. I'm open to suggestions!
        col.addItems(list(set(chain(*self.df[col.objectName()].apply(lambda el:list(ast.literal_eval(el)))))))# At this point I'm writing with a lisp.
    
    def strExtract(self, col):
        col.addItems(list(set(self.df[col.objectName()])))

    def numExtract(self, col):
        col.addItems(list(map(str, set(self.df[col.objectName()]))))
    
    def emptyDf(self):
        for col in self.ui.listw_:
            col.addItem('Empty DataFrame')
            col.setDisabled(True)
    def unsupportedType(self, col):
        col.addItems(['Unsupported type: ', str(type(self.df[col.objectName()][0]))])
        col.setDisabled(True)
    def setupWorkEnv(self):
        pass
    def copyFilterClipboard(self):
        cb = QtGui.QApplication.clipboard()
        cb.clear(mode=cb.Clipboard )
        cb.setText('\n'.join(self.filtLogPandas.split('!&&!')), mode=cb.Clipboard)
        
#    def loadFile(self, selection):
#        pass
        
class Window(QtWidgets.QWidget):
    def __init__(self, dfRoot, exclude=[], special={}):
        super().__init__()
        self.tabs = QtWidgets.QTabWidget()
        self.exclude = exclude
        self.special = special
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
#        button = QtWidgets.QToolButton()
#        button.setToolTip('Add New Tab')
#        button.clicked.connect(partial(self.addNewTab, dfRoot, 'Root', self.exclude, self.special))
#        button.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogYesButton))
#        self.tabs.setCornerWidget(button, QtCore.Qt.TopRightCorner)
        self.addNewTab(dfRoot, '>>R', '>>Root', '')
        self.tabs.tabBar().tabCloseRequested.connect(lambda n: self.tabs.removeTab(n))

    def addNewTab(self, df, tabTitle, filtLog, filtLogPandas):
        self.tabs.addTab(TabPage(self.tabs), tabTitle)
        self.tabs.widget(self.tabs.count() - 1).setupGUI(df, self.exclude, self.special)
        self.tabs.widget(self.tabs.count() - 1).updateDf()
        self.tabs.setTabsClosable(True)
        
        bar = self.tabs.tabBar()
        bar.setTabButton(0, bar.RightSide, None)
        
        self.tabs.widget(self.tabs.count() - 1).filtLogPandas = filtLogPandas
        self.tabs.widget(self.tabs.count() - 1).filtLog = '>>' + filtLog
    
        for i in range(0, len(self.tabs.widget(self.tabs.count() - 1).ui.BtnApply_)):
            #print(BtnApply)
            self.tabs.widget(self.tabs.count() - 1).ui.BtnApply_[i].clicked.connect(partial(self.applyFilterBtnPressed, i))
        
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        
    def applyPdFilter(self, df, colNum):
        filt = self.tabs.currentWidget().ui.lineEdFilter_[colNum].text()
        colName = self.tabs.currentWidget().ui.listw_[colNum].objectName()

        if filt.startswith('$'):
            if filt.startswith('$NOT:'):
                filt=filt[5:]
                newDf = df[~df[colName].str.contains(filt)]
                prefix = '~'
        else:
            prefix = ''
            newDf = df[df[colName].str.contains(filt)]
            print(newDf)
        
        filtLog = '&&' + prefix + '{' + colName + '[' + filt + ']}'
        filtLogPandas = "df = df["+prefix+"df['"+colName+"'].str.contains('"+filt+"') !&&!"
        
        tabTitleAdd = prefix + colName + ','
        
        return newDf, filtLog, filtLogPandas, tabTitleAdd
    
    def applyPdFilterAll(self):
        newDf = self.tabs.currentWidget().df
        filtLog = self.tabs.currentWidget().filtLog
        filtLogPandas = self.tabs.currentWidget().filtLogPandas
        
        for colNum in range(0, len(self.tabs.currentWidget().ui.lineEdFilter_)):
            if self.tabs.currentWidget().ui.lineEdFilter_[colNum].text() != '':
                newDf, log, titleAdd = self.applyPdFilter(newDf, colNum)
                filtLog = filtLog + log
                
        return newDf, filtLog, filtLogPandas, titleAdd
                
    def applyFilterBtnPressed(self, colNum):
        key = QtGui.QApplication.keyboardModifiers()
        
        # If Root DataFrame, it will always open the filtered DataFrame in a new tab
        if self.tabs.currentIndex() == 0:
            if key == QtCore.Qt.ShiftModifier:
                df, filtLog, filtLogPandas, titleAdd = self.applyPdFilterAll()
            else:
                df, filtLog, filtLogPandas, title = self.applyPdFilter(self.tabs.currentWidget().df, colNum)
                filtLog = self.tabs.currentWidget().filtLog + filtLog
                filtLogPandas = self.tabs.currentWidget().filtLogPandas + filtLogPandas
            self.addNewTab(df, 'bah', filtLog, filtLogPandas)
            
            return
        
        # Open new tab and filter selected column
        elif key == QtCore.Qt.ControlModifier:
            df, filtLog, filtLogPandas, title = self.applyPdFilter(self.tabs.currentWidget().df, colNum)
            filtLog = self.tabs.currentWidget().filtLog + filtLog
            filtLogPandas = self.tabs.currentWidget().filtLogPandas + filtLogPandas
            self.addNewTab(df, 'bah', filtLog, filtLogPandas)
            
        # Filter all columns in current tab
        elif key == QtCore.Qt.ShiftModifier:
            df, filtLog, filtLogPandas, titleAdd = self.applyPdFilterAll()
            self.tabs.currentWidget().df = df
            self.tabs.currentWidget().filtLog = filtLog
            self.tabs.currentWidget().filtLogPandas = filtLogPandas
            self.tabs.currentWidget().updateDf()
        
        # Open new tab and filter all columns
        elif key == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            df, filtLog, filtLogPandas, titleAdd = self.applyPdFilterAll()
            
            filtLog = self.tabs.currentWidget().filtLog + filtLog
            filtLogPandas = self.tabs.currentWidget().filtLogPandas + filtLogPandas
            self.addNewTab(df, 'bah', filtLog, filtLogPandas)   
        
        # Filter single selected column here
        else:
            df, filtLog, filtLogPandas, title = self.applyPdFilter(self.tabs.currentWidget().df, colNum)
            self.tabs.currentWidget().df = df
            self.tabs.currentWidget().filtLog = self.tabs.currentWidget().filtLog + filtLog
            self.tabs.currentWidget().filtLogPandas = self.tabs.currentWidget().filtLogPandas + filtLogPandas
            self.tabs.currentWidget().updateDf()
            
            

if __name__ == '__main__':
    
    df = pickle.load(open('/home/kushal/Sars_stuff/github-repos/20180118_alldata.pickle', 'rb'))
    #df = pd.read_csv('/home/kushal/Sars_stuff/github-repos/testprojects/testnew/testnew_index.mzp')
    special = {'Timings': 'StimSet'}
    
    app = QtWidgets.QApplication(sys.argv)
    w = Window(df, special=special)
    w.resize(1000,840)
    w.show()
    
#    app = QtGui.QApplication([])
#    ## Create window with Project Explorer widget
#    projectWindow = QtGui.QMainWindow()
#    projectWindow.resize(1000,800)
#    projectWindow.setWindowTitle('Mesmerize - Project Explorer')
#    projBrowser = ProjBrowser()
#    projBrowser.setupGUI(df, special=special)
#    projectWindow.setCentralWidget(projBrowser)
#    projectWindow.show()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
