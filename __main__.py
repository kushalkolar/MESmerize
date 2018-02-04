#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 21:14:51 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, USE_PYSIDE
from MesmerizeCore import ProjBrowser
from MesmerizeCore import configwindow
from pyqtgraphCore.graphicsItems.InfiniteLine import *
import pyqtgraphCore
import numpy as np
import pickle
import sys
import ast
from MesmerizeCore import packager
from shutil import copyfile
import time
import pandas as pd
from MesmerizeCore.startWindow import startGUI
import os
from functools import partial


'''
Main file to be called. The intent is that if no arguments are passed the standard desktop application loads.
I intend to create a headless mode for doing certain things on a cluster/supercomputer

The instance of desktopApp is useful for communicating between the Viewer & Project Browser
'''

# class main():
#     def __init__(self, args=None):
#         if args is None:
#             self.app = QtGui.QApplication([])
#
#             self.viewer = None
#             self.projName = None

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        # QtGui.QMainWindow.__init__(self)
        super().__init__()
        self.viewer = None
        self.projBrowserWin = None
        self.projName = None
        self.setWindowTitle('Mesmerize')
        self.initMenuBar()
    def initMenuBar(self):
        self.menubar = self.menuBar()

        fileMenu = self.menubar.addMenu('&File')

        mBtnNewProj = fileMenu.addAction('New')
        mBtnNewProj.triggered.connect(self.newProjFileDialog)

        mBtnOpenProj = fileMenu.addAction('Open')
        mBtnOpenProj.triggered.connect(self.openProjFileDialog)


        dataframeMenu = self.menubar.addMenu('&DataFrame')

        saveRootDf = dataframeMenu.addAction('Save Root')

        saveChild = dataframeMenu.addAction('Save Current Child')

        saveChildAs = dataframeMenu.addAction('Save Current Child As...')

        saveAllChildren = dataframeMenu.addAction('Save All Children')

        saveAsNewProj = dataframeMenu.addAction('New Project from Current Child')

        deleteChild = dataframeMenu.addAction('Delete Current Child')



        editMenu = self.menubar.addMenu('&Edit')

        changeConfig = editMenu.addAction('Project Configuration')
        changeConfig.triggered.connect(self.openCfgWindow)


    def newProjFileDialog(self):
        parentPath = QtGui.QFileDialog.getExistingDirectory(self, 'Choose location for new project')
        if parentPath == '':
            return

        projName, start = QtGui.QInputDialog.getText(self, '', 'Project Name:', QtGui.QLineEdit.Normal, '')

        if start and projName != '':
            self.projPath = parentPath + '/' + projName
            os.mkdir(self.projPath)

            self.newProj()
            # self.projDf = packager.empty_df()


#            self.projDf.to_csv(self.projDfFilePath, index=False)


    def newProj(self):
        self.setupProjPaths()

        self.config = configwindow

        self.config.newConfig(self.projCfgPath)

        self.openCfgWindow()

        self.cfgWindow.tabs.widget(0).ui.btnSave.clicked.connect(self.createNewDf)

    def setupProjPaths(self, checkPaths=False):

        self.projDfsDir = self.projPath + '/dataframes'
        self.projCfgPath = self.projPath + '/config.cfg'
        self.projRootDfPath = self.projDfsDir + '/root.mzp'
        self.projName = self.projPath.split('/')[-1]


        if checkPaths:
            if os.path.isdir(self.projDfsDir) == False:
                QtGui.QMessageBox.warning(self, 'Project DataFrame Directory not found!', 'The selected directory is ' +\
                    'not a valid Mesmerize Project since it doesn\'t contain a DataFrame directory!',
                                          QtGui.QMessageBox.Ok)
                return False
            if (os.path.isfile(self.projRootDfPath) == False):
                QtGui.QMessageBox.warning(self, 'Project Root DataFrame not found!',
                                           'The selected directory does Not contain a Root DataFrame!', QtGui.QMessageBox.Ok)
                return False

            if os.path.isfile(self.projCfgPath) == False:
                if QtGui.QMessageBox.warning(self, 'Project Config file not found!', 'The selected project does not ' +\
                                            'contain a config file. Would you like to create one now?\nYou cannot proceed'
                                            'without a config file.',
                                          QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    return False

        if checkPaths == False:
            os.mkdir(self.projDfsDir)
            os.mkdir(self.projPath + '/images')
            os.mkdir(self.projPath + '/curves')

        self.setWindowTitle('Mesmerize - ' + self.projName)

    def createNewDf(self):
        include = self.config.cfg.options('INCLUDE')
        exclude = self.config.cfg.options('EXCLUDE')

        cols = include + exclude

        self.projDf = packager.empty_df(cols)
        assert isinstance(self.projDf, pd.DataFrame)
        self.projDf.to_pickle(self.projRootDfPath, protocol=4)

        self.cfgWindow.tabs.widget(0).ui.btnSave.clicked.disconnect(self.createNewDf)

        # Start the Project Browser loaded with the dataframe columns in the listwidget
        self.initProjBrowser()


    def openCfgWindow(self):
        self.cfgWindow = self.config.Window(self.projCfgPath)
        self.cfgWindow.tabs.widget(0).ui.btnSave.clicked.connect(self.updateCurrentConfiguration)
        self.cfgWindow.resize(593, 617)
        self.cfgWindow.show()

    def updateCurrentConfiguration(self):
        if self.viewer is not None:
            self.viewer.ui.listwROIDefs.clear()
            self.viewer.ui.listwROIDefs.addItems(self.config.cfg.options('ROI_DEFS'))
            self.viewer.setSelectedROI()

        if self.projBrowserWin is not None:
            self.projBrowserWin.updateCfg(self.config)

        ''' >>> ALSO UPDATE DATAFRAME COLUMNS ACCORDING TO UPDATED CONFIGURATION'''

    def openProjFileDialog(self):
        if (self.viewer is not None):
            if QtGui.QMessageBox.warning(self, 'Close Viewer Window?', 'Would you like to discard any ' +\
                                                                     'unsaved work in your Viewer window?',
                                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.viewerWindow.close()
                self.viewer = None
            else:
                return

        if (self.projBrowserWin is not None):
            if QtGui.QMessageBox.warning(self, 'Close Current Project?', 'You currently have a project open, would you' +\
                                          'like to discard any unsaved work and open another project?',
                                         QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.projBrowserWin.close()
                self.projBrowserWin = None
            else:
                return

        self.projPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select Project Folder')

        if self.projPath == '':
            return

        if self.setupProjPaths(checkPaths=True) is not False:
            self.openProj()
        
    def openProj(self):
        self.projDf = pd.read_pickle(self.projRootDfPath)
        assert isinstance(self.projDf, pd.DataFrame)
        self.config = configwindow
        self.config.openConfig(self.projCfgPath)
        self.projName = self.projPath.split('/')[-1][:-4]
        # Start the Project Browser loaded with the dataframe columns in the listwidget
        self.initProjBrowser()
        
    def initProjBrowser(self):
        special = {'Timings': self.config.cfg.options('STIM_DEFS')}

        self.projBrowserWin = ProjBrowser.Window(self.projDf, exclude=self.config.cfg.options('EXCLUDE'), special=special)

        self.setCentralWidget(self.projBrowserWin)

        # self.projBrowser.resize(1000,840)
        # self.projBrowser.show()
        
        ## Create window with Project Explorer widget
#        self.projectWindow = QtGui.QMainWindow()
#        self.projectWindow.resize(1000,800)
#        self.projectWindow.setWindowTitle('Mesmerize - Project Browser')
#        self.projBrowser = ProjBrowser()
#        self.projectWindow.setCentralWidget(self.projBrowser)
#        exclude = ['ImgPath', 'ROIhandles', 'ImgInfoPath', 'CurvePath']
#        
#        special = {'Timings': 'StimSet'}
#        self.projBrowser.setupGUI(projDataFrame, exclude, special)
#        self.projectWindow.show()
        if self.viewer is None:
            self.initViewer()
        #self.projBrowser.ui.openViewerBtn.clicked.connect(self.viewerWindow.show())
        self.viewer.projPath = self.projPath

    def initViewer(self):
        # Interpret image data as row-major instead of col-major
        pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
    
        ## Create window with ImageView widget
        self.viewerWindow = QtGui.QMainWindow()
        self.viewerWindow.resize(1458,931)
        self.viewer = pyqtgraphCore.ImageView()
        self.viewerWindow.setCentralWidget(self.viewer)
#        self.projBrowser.ui.openViewerBtn.clicked.connect(self.showViewer)
        self.viewerWindow.setWindowTitle('Mesmerize - Viewer')
        
        ## Set a custom color map
        colors = [
            (0, 0, 0),
            (45, 5, 61),
            (84, 42, 55),
            (150, 87, 60),
            (208, 171, 141),
            (255, 255, 255)
        ]
        cmap = pyqtgraphCore.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
        self.viewer.setColorMap(cmap)
        
        # self.viewer.ui.btnAddCurrEnvToProj.clicked.connect(self.addWorkEnvToProj)
        self.viewer.ui.btnAddToBatch.clicked.connect(self.viewerAddToBatch)
        self.viewer.ui.btnOpenBatch.clicked.connect(self.viewerOpenBatch)
        self.viewerWindow.show()

        self.viewer.ui.listwROIDefs.addItems([roi_def + ': ' for roi_def in self.config.cfg.options('ROI_DEFS')])
        self.viewer.proj_stim_channel_names = self.config.cfg.options('STIM_DEFS')
        self.viewer.ui.btnAddCurrEnvToProj.clicked.connect(self.addWorkEnvToProj)

        viewMenu = self.menubar.addMenu('&View')
        showViewer = viewMenu.addAction('Show Viewer')
        showViewer.triggered.connect(self.viewerWindow.show)

    def isProjLoaded(self):
        if self.projName is None:
            answer = QtGui.QMessageBox.question(self.viewer, 'Message', 
                        'You don''t have any project open! ' +\
                        'Would you like to start a new project (Yes) or Open a project?', 
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.Open)
            if answer == QtGui.QMessageBox.Yes:
                self.newProjFileDialog()
            elif answer == QtGui.QMessageBox.Open:
                self.openProjFileDialog()
                
            return False
        
        else:
            return True
    
    def viewerAddToBatch(self):
        if self.isProjLoaded():
            self.viewer.addToBatch()
    
    def viewerOpenBatch(self):
        if self.isProjLoaded():
            self.viewer.openBatch()
    
    def addWorkEnvToProj(self):
        if self.isProjLoaded():
            r, d = self.viewer.workEnv.to_pandas(self.projPath)
            if r is False:
                return
            copyfile(self.projRootDfPath, self.projRootDfPath + '_BACKUP' + str(time.time()))


            self.projDf = self.projDf.append(pd.DataFrame(d), ignore_index=True)

            self.projDf.to_pickle(self.projRootDfPath, protocol=4)
            self.projBrowserWin.tabs.widget(0).df = self.projDf
            self.projBrowserWin.tabs.widget(0).updateDf()
            
            
if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = MainWindow()
    gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
