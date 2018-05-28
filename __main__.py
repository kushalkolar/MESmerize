#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 7 21:14:51 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.console import ConsoleWidget
from mainwindow import Ui_MainWindow
from MesmerizeCore import ProjBrowser
from MesmerizeCore import ConfigWindow
from MesmerizeCore import configuration
from MesmerizeCore import preferences
import pyqtgraphCore
import numpy as np
import tifffile
import pickle
import sys
from MesmerizeCore import packager
from shutil import copyfile
import time
import pandas as pd
import os
from functools import partial
from MesmerizeCore import misc_funcs
import analyser.gui
from analyser.stats_gui import StatsWindow
from copy import deepcopy
import weakref
import viewer_modules.main_window

'''
Main file to be called. The intent is that if no arguments are passed the standard desktop application loads.
I intend to create a headless mode for doing certain things on a cluster/supercomputer

The instance of MainWindow is useful for communicating between the Viewer & Project Browser
'''

# class main():
#     def __init__(self, args=None):
#         if args is None:
#             self.app = QtGui.QApplication([])
#
#             self.viewer = None
#             self.projName = None

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # QtGui.QMainWindow.__init__(self)
        super().__init__()
        self.setupUi(self)
        self.dockWidget.hide()
        self.viewer = None
        self.projBrowserWin = None
        self.projName = None
        self.projDf = None
        self.setWindowTitle('Mesmerize')
        self.resize(700, 400)
        self.analysisWindows = []
        self.statsWindows = []
        self.preferences_gui = preferences.PreferencesGUI()
        if not os.path.exists('./.config/'):
            os.makedirs('./.config/')

        configuration.install_config_path = os.path.abspath('./.config/')

        self.connect_sigs_MenuBar()
        
    def connect_sigs_MenuBar(self):
        self.actionNew.triggered.connect(self.newProjFileDialog)
        self.actionOpen.triggered.connect(self.openProjFileDialog)
        self.actionProject_Configuration.triggered.connect(self.openConfigWindow)
        self.actionNewAnalyzerInstance.triggered.connect(self.initAnalyzer)
        self.actionShow_all_Analyzer_windows.triggered.connect(self.showAllAnalyzerWindows)
        self.actionNew_Stats_Plots_instance.triggered.connect(self.initStatsPlotsWin)
        self.actionShow_all_Stats_Plots_windows.triggered.connect(self.showAllStatWindows)
        self.actionUpdate_children_from_Root.triggered.connect(self.update_children)
        self.actionPreferences.triggered.connect(self.preferences_gui.show)

    def newProjFileDialog(self):
        # Opens a file dialog to selected a parent dir for a new project
        parentPath = QtGui.QFileDialog.getExistingDirectory(self, 'Choose location for new project')
        if parentPath == '':
            return


        projName, start = QtGui.QInputDialog.getText(self, '', 'Project Name:', QtGui.QLineEdit.Normal, '')

        if start and projName != '':
            self.projPath = parentPath + '/' + projName
            try:
                os.mkdir(self.projPath)
            except Exception as e:
                QtGui.QMessageBox.warning(self, 'Error!', 'Could not create the new project.\n' + str(e))
                return

            self.newProj()
            # self.projDf = packager.empty_df()


#            self.projDf.to_csv(self.projDfFilePath, index=False)

    def newProj(self):
        self.checkProjOpen()  # If a project is already open, prevent loosing unsaved work
        # setup paths for the project files
        self.setupProjPaths()
        # Initialize a configuration for the project
        self.configwin = ConfigWindow
        configuration.newConfig()
        self.openConfigWindow()
        self.configwin.tabs.widget(0).ui.btnSave.clicked.connect(self.createNewDf)

    def checkProjOpen(self):
        # Function to check if any project is already open to prevnet losing unsaved work.
        if (self.viewer is not None):
            if QtGui.QMessageBox.warning(self, 'Close Viewer Window?', 'Would you like to discard any ' +\
                                                'unsaved work in your Viewer window?', QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.viewerWindow.close()
                self.viewer = None
            else:
                return False

        if (self.projBrowserWin is not None):
            if QtGui.QMessageBox.warning(self, 'Close Current Project?', 'You currently have a project open, would you' +\
                                          'like to discard any unsaved work and open another project?',
                                         QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.projBrowserWin.close()
                self.projBrowserWin = None
            else:
                return False

        return True

    def setupProjPaths(self, checkPaths=False):
        # Create important path attributes for the project
        self.projDfsDir = self.projPath + '/dataframes'
        configuration.configpath = self.projPath + '/config.cfg'
        self.projRootDfPath = self.projDfsDir + '/root.mzp'
        self.projName = self.projPath.split('/')[-1]

        # If opening a project check if this is a valid Mesmerize project by checking for paths
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

            if os.path.isfile(configuration.configpath) == False:
                if QtGui.QMessageBox.warning(self, 'Project Config file not found!', 'The selected project does not ' +\
                                            'contain a config file. Would you like to create one now?\nYou cannot proceed'
                                            'without a config file.',
                                          QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    return False
        # create dirs if new project
        if checkPaths == False:
            os.mkdir(self.projDfsDir)
            os.mkdir(self.projPath + '/images')
            os.mkdir(self.projPath + '/curves')

        configuration.projPath = self.projPath

        self.setWindowTitle('Mesmerize - ' + self.projName)

        self.menuEdit.setEnabled(True)
        self.menuDataFrame.setEnabled(True)
        self.actionNewAnalyzerInstance.setEnabled(True)

    def createNewDf(self):
        # Create empty DataFrame
        self.configwin.tabs.widget(0).ui.btnSave.clicked.disconnect(self.createNewDf)

        include = configuration.cfg.options('INCLUDE')
        exclude = configuration.cfg.options('EXCLUDE')

        cols = include + exclude

        self.projDf = misc_funcs.empty_df(cols)
        assert isinstance(self.projDf, pd.DataFrame)
        self.projDf.to_pickle(self.projRootDfPath, protocol=4)

        # Start the Project Browser loaded with the dataframe columns in the listwidget
        self.initProjBrowser()


    def openConfigWindow(self):
        self.configwin = ConfigWindow.Window()
        self.configwin.tabs.widget(0).ui.btnSave.clicked.connect(self.update_all_from_config)
        self.configwin.resize(593, 617)
        self.configwin.show()

    def update_all_from_config(self):
        # To update the project configuration when the user changes the configuration in the middle of a project.
        self.configwin.tabs.widget(0).ui.btnSave.clicked.disconnect(self.update_all_from_config)

        if self.projDf is not None and self.projDf.empty:
            self.projDf = misc_funcs.empty_df(configuration.cfg.options('INCLUDE') + configuration.cfg.options('EXCLUDE'))

        if self.viewer is not None:
            self.viewer.update_from_config()

        if self.projBrowserWin is not None:

            for col in configuration.cfg.options('ROI_DEFS'):
                if col not in self.projDf.columns:
                    self.projDf[col] = 'untagged'

            for col in configuration.cfg.options('STIM_DEFS'):
                if col not in self.projDf.columns:
                    self.projDf[col] = [['untagged']] * len(self.projDf)

            copyfile(self.projRootDfPath, self.projRootDfPath + '_BACKUP' + str(time.time()))
            self.projDf.to_pickle(self.projRootDfPath, protocol=4)
            self.projBrowserWin.close()
            self.projBrowserWin = None
            self.initProjBrowser()
        # QtGui.QMessageBox.information(self, 'Config saved, restart.', 'You must restart Mesmerize and re-open your '
        #                                     'project for changes to take effect.')

    def openProjFileDialog(self):
        # File dialog to open an existing project
        if self.checkProjOpen() is False:
            return
        projPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select Project Folder')

        if projPath == '':
            return

        self.projPath = projPath
        if self.setupProjPaths(checkPaths=True) is not False:
            self.openProj()
        
    def openProj(self):
        self.projDf = pd.read_pickle(self.projRootDfPath)
        assert isinstance(self.projDf, pd.DataFrame)
        configuration.openConfig()
        self.configwin = ConfigWindow
        self.projName = self.projPath.split('/')[-1][:-4]
        # Start the Project Browser loaded with the dataframe columns in the listwidget
        self.initProjBrowser()

    def update_children(self):
        for n in range(1, self.projBrowserWin.tabs.count()):
            self.projBrowserWin.tabs.removeTab(n)

        self.update_child_dfs()

    def update_child_dfs(self):
        for child in configuration.cfg.options('CHILD_DFS'):
            if child == 'R' or child == 'Root':
                continue
            child_filter = configuration.cfg['CHILD_DFS'][child]
            filters = child_filter.split('\n')
            df = self.projDf.copy()
            for filter in filters:
                if filter == '':
                    continue
                df = eval(filter)
            self.projBrowserWin.addNewTab(df, child, '', child_filter)
        
    def initProjBrowser(self):
        self.projBrowserWin = ProjBrowser.Window(self.projDf)
        self.menuDataFrame.setEnabled(True)
        self.update_child_dfs()

        self.setCentralWidget(self.projBrowserWin)
        # self.projScollArea.setWidget(self.projBrowserWin)
        # self.scrollArea.setWidget(self.projBrowserWin)
        # self.scrollArea.setWidgetResizable(True)
        # self.setCentralWidget(self.projBrowserWin)

        ns = {'pd':         pd,
              'np':         np,
              'pickle':     pickle,
              'tifffile':   tifffile,
              'curr_tab':   self.projBrowserWin.tabs.currentWidget,
              'pbwin':      self.projBrowserWin,
              'addTab':     self.projBrowserWin.addNewTab,
              'viewer':     self.viewer,
              'main':       self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "pandas as pd         \n" \
              "pickle as 'pickle    \n" \
              "tifffile as tifffile \n" \
              "viewer as viewer     \n" \
              "self as main         \n" \
              "call curr_tab() to return current tab widget\n" \
              "call addTab(<dataframe>, <title>, <filtLog>, <filtLogPandas>) to add a new tab\n"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/main.pik'

        self.dockWidget.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))

        self.dockWidget.hide()

        if len(configuration.cfg.options('INCLUDE')) > 8:
            self.resize(1900,900)
        else:
            self.resize(1900,600)

        if self.viewer is None:
            self.initViewer()
        #self.projBrowser.ui.openViewerBtn.clicked.connect(self.viewerWindow.show())
        self.viewer.projPath = self.projPath

    def initViewer(self):
        # Interpret image data as row-major instead of col-major
        pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
        ## Create window with ImageView widget
        self.viewerWindow = viewer_modules.main_window.MainWindow() #QtWidgets.QMainWindow()
        self.viewerWindow.resize(1460, 950)
        self.viewer = pyqtgraphCore.ImageView(parent=self.viewerWindow)
        self.viewerWindow.viewer_reference = self.viewer
        assert isinstance(self.viewer, pyqtgraphCore.ImageView)
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

        # self.viewer.ui.btnAddToBatch.clicked.connect(self.viewerAddToBatch)
        # self.viewer.ui.btnOpenBatch.clicked.connect(self.viewerOpenBatch)
        # self.viewerWindow.show()

        # self.viewer.ui.btnAddCurrEnvToProj.clicked.connect(self.addWorkEnvToProj)
        self.viewer.ui.btnSplitSeq.clicked.connect(self.viewer_enter_split_seq)
        self.viewer.ui.btnDoneSplitSeqs.clicked.connect(self.viewer_done_split_seq)

        self.actionShow_Viewer.setEnabled(True)
        self.actionShow_Viewer.triggered.connect(self.viewerWindow.show)

    def isProjLoaded(self):
        if self.projName is None:
            answer = QtGui.QMessageBox.question(self.viewer, 'Message', 
                'You don''t have any project open! Would you like to start a new project (Yes) or Open a project?',
                QtGui.QMessageBox.Yes, QtGui.QMessageBox.Open)
            if answer == QtGui.QMessageBox.Yes:
                self.newProjFileDialog()
            elif answer == QtGui.QMessageBox.Open:
                self.openProjFileDialog()
                
            return False
        
        else:
            return True
    
    # def viewerAddToBatch(self):
    #     if self.isProjLoaded():
    #         self.viewer.addToBatch()
    #
    # def viewerOpenBatch(self):
    #     if self.isProjLoaded():
    #         self.viewer.openBatch()

    def viewer_enter_split_seq(self):
        if self.viewer.splitSeqMode is False:
            if self.viewer.setSampleID() is False:
                return
            if any(self.projDf['SampleID'].str.match(self.viewer.workEnv.imgdata.SampleID)):
                QtGui.QMessageBox.warning(self, 'Sample ID already exists!', 'The following SampleID already exists' + \
                                          ' in your DataFrame. Use a unique Sample ID for each sample.\n' + \
                                          self.viewer.workEnv.imgdata.SampleID, QtGui.QMessageBox.Ok)
        self.viewer.enterSplitSeqMode()

    def viewer_done_split_seq(self):
        self.viewer.splits_seq_mode_done()
        self.addWorkEnvToProj(update_ROIPlots=False)

    def addWorkEnvToProj(self, update_ROIPlots=True):
        if self.isProjLoaded():
            if self.viewer.setSampleID() is False:
                return
            if any(self.projDf['SampleID'].str.match(self.viewer.workEnv.imgdata.SampleID)):
                QtGui.QMessageBox.warning(self, 'Sample ID already exists!', 'The following SampleID already exists'+\
                          ' in your DataFrame. Use a unique Sample ID for each sample.\n' +\
                          self.viewer.workEnv.imgdata.SampleID, QtGui.QMessageBox.Ok)
                return
            if update_ROIPlots:
                for ID in range(0, len(self.viewer.workEnv.ROIList)):
                    self.viewer.updatePlot(ID, force=True)
            # try:
            d = self.viewer.workEnv.to_pandas(self.projPath)
            # except Exception as e:
            #     QtGui.QMessageBox.warning(self, 'Error', 'The following error occured while trying to save the current '
            #                                              'work environment to your project:\n' + str(e))
            #   return
            copyfile(self.projRootDfPath, self.projRootDfPath + '_BACKUP' + str(time.time()))
            self.projDf = self.projDf.append(pd.DataFrame(d), ignore_index=True)
            self.projDf.to_pickle(self.projRootDfPath, protocol=4)
            self.projBrowserWin.tabs.widget(0).df = self.projDf
            self.projBrowserWin.tabs.widget(0).updateDf()

    def initAnalyzer(self):
        self.analysisWindows.append(analyser.gui.Window())
        self.analysisWindows[-1].show()

    def initStatsPlotsWin(self):
        self.statsWindows.append(StatsWindow())
        self.statsWindows[-1].show()

    def showAllAnalyzerWindows(self):
        for win in self.analysisWindows:
            win.show()

    def showAllStatWindows(self):
        for win in self.statsWindows:
            self.statsWindows.show()

            
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = MainWindow()
    gui.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()
#        QtWidgets.QApplication.instance().exec_()
