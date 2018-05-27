#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 19 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.mesfile_io_pytemplate import *


class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnOpenMesFile.clicked.connect(self.load_mesfile)
        self.ui.listwMesfile.itemDoubleClicked.connect(lambda sel: self.load_mesfile_selection(sel))
        self.ui.btnStimMapGUI.clicked.connect(self.open_stim_map_gui)

    def load_mesfile(self):
        if not self.VIEWER_discard_workEnv():
            return

        filelist = QtWidgets.QFileDialog.getOpenFileNames(self, 'Choose ONE mes file', '.', '(*.mes)')

        if len(filelist) == 0:
            return

        try:
            # Creates an instance of MES, see MesmerizeCore.FileInput
            self.mesfile = ViewerWorkEnv.load_mesfile(filelist[0][0])
            self.ui.listwMesfile.setEnabled(True)

            # Get the references of the images, their descriptions, and add them to the list
            for i in self.mesfile.images:
                j = self.mesfile.image_descriptions[i]
                self.ui.listwMesfile.addItem(i+'//'+j)

            # If Auxiliary voltage info is found in the mes file, ask the user if they want to map these to stimuli
            if len(self.mesfile.voltDict) > 0:
                #self.initMesStimMapGUI()
                self.ui.btnSetStimMap.setEnabled(True)
                if QtWidgets.QMessageBox.question(self, '', 'This .mes file contains auxilliary output voltage ' + \
                              'information, would you like to apply a Stimulus Map now?',
                              QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:

                    self.stimMapWin.show()

        except (IOError, IndexError) as e:
            QtWidgets.QMessageBox.warning(self, 'IOError or IndexError',
                                          "There is an problem with the files you've selected:\n" + str(e),
                                          QtWidgets.QMessageBox.Ok)
        return

    def load_mesfile_selection(self, s):
        if not self.VIEWER_discard_workEnv():
            return
        try:
            self.viewer_ref.workEnv = ViewerWorkEnv.from_mesfile(self.mesfile, s.text().split('//')[0])
        except Exception as e:
            QtWidgets.QMessageBox.information(self, 'Error', 'Error opening the selected ' + \
                                          'image in the currently open mes file.\n' + str(e), QtWidgets.QMessageBox.Ok)
            return
        self.VIEWER_update_workEnv()
        self.VIEWER_enable_ui(True)

    def open_stim_map_gui(self):
        pass
