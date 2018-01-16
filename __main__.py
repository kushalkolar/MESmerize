#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 21:14:51 2018

@author: kushal
"""

from pyqtgraphCore.Qt import QtCore, QtGui, USE_PYSIDE
from MesmerizeCore.ProjBrowser import ProjBrowser
from pyqtgraphCore.graphicsItems.InfiniteLine import *
import pyqtgraphCore
import numpy as np
import pickle
import sys
import ast

class main():
    def __init__(self, args=None):
        if args is None:
            self.desktopApp()
    def desktopApp(self):
        self.app = QtGui.QApplication([])
        
        ## Create window with Project Explorer widget
        self.projectWindow = QtGui.QMainWindow()
        self.projectWindow.resize(500,500)
        self.projectWindow.setWindowTitle('Mesmerize - Project Explorer')
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
        
        
        self.viewer.ui.btnAddCurrEnvToProj.clicked.connect(self.addImgDataObjtoProj)
        
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
    def showViewer(self, event):
        if self.projBrowser.CurrProjName is not None:
            self.viewer.currProjDir = self.projBrowser.projPath
        self.viewerWindow.show()
        
    def addImgDataObjtoProj(self):
        if self.projBrowser.CurrProjName is not None:
            pickle.dump(self.viewer.currImgDataObj, open(self.projBrowser.filePathSelected +
                 '/' + self.viewer.currImgDataObj.meta["Comment"], 'wb'))

if __name__ == '__main__':
    gui = main()
