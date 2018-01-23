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
from MesmerizeCore.ProjBrowser import ProjBrowser
from pyqtgraphCore.graphicsItems.InfiniteLine import *
import pyqtgraphCore
import numpy as np
import pickle
import sys
import ast
from MesmerizeCore.packager import workEnv2pandas
from shutil import copyfile
import time
import pandas as pd

'''
Main file to be called. The intent is that if no arguments are passed the standard desktop application loads.
I intend to create a headless mode for doing certain things on a cluster/supercomputer

The instance of desktopApp is useful for communicating between the Viewer & Project Browser
'''

class main():
    def __init__(self, args=None):
        if args is None:
            self.desktopApp()
    def desktopApp(self):
        self.app = QtGui.QApplication([])
        
        ## Create window with Project Explorer widget
        self.projectWindow = QtGui.QMainWindow()
        self.projectWindow.resize(1000,800)
        self.projectWindow.setWindowTitle('Mesmerize - Project Browser')
        self.projBrowser = ProjBrowser()
        self.projectWindow.setCentralWidget(self.projBrowser)
        self.projectWindow.show()
        
        # ----------------------------------------------------------------------#
        # Initiate viewer
        # ----------------------------------------------------------------------#
        
        # Interpret image data as row-major instead of col-major
        pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
        
        
        ## Create window with ImageView widget
        self.viewerWindow = QtGui.QMainWindow()
        self.viewerWindow.resize(1400,980)
        self.viewer = pyqtgraphCore.ImageView()
        self.viewerWindow.setCentralWidget(self.viewer)
        self.projBrowser.ui.openViewerBtn.clicked.connect(self.showViewer)
        self.viewerWindow.setWindowTitle('Mesmerize - viewer')
        
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
        
        self.viewer.ui.btnAddCurrEnvToProj.clicked.connect(self.addWorkEnvToProj)
        
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
        
    def showViewer(self, event):
        if self.projBrowser.CurrProjName is not None:
            self.viewer.currProjDir = self.projBrowser.projPath
        self.viewerWindow.show()
        
    def addWorkEnvToProj(self):
        print('button works')
        if self.projBrowser.CurrProjName is None:
            QtGui.QMessageBox.question(self.viewer, 'Message', 'You don''t have any project open! Open ' +\
                                       'an existing project or start a new project before trying again', 
                                       QtGui.QMessageBox.Ok)
            print('bah')
        else:
            df = workEnv2pandas(self.projBrowser.projDataFrame,
                                self.projBrowser.projPath,
                                self.viewer.currImgDataObj, 
                                self.viewer.ROIlist,
                                self.viewer.Curveslist)
            print(df)
            # Create backup of index
            copyfile(self.projBrowser.projDataFrameFilePath, 
                     self.projBrowser.projDataFrameFilePath + '.BACKUP_' + str(time.time()))
            
            self.projBrowser.projDataFrame = df
            # Save index
            self.projBrowser.projDataFrame.to_csv(self.projBrowser.projDataFrameFilePath, index=False)
            
                
if __name__ == '__main__':
    gui = main()
    