#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 5 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import pyqtgraphCore
from .welcome_window_pytemplate import *
from viewer_modules import main_window as viewer_main_window
from . import configuration


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Mesmerize - Main Window')

        self.ui.btnNew.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_1327089_cc.png'))
        self.ui.btnNew.setIconSize(QtCore.QSize(100,100))

        self.ui.btnOpen.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_1327109_cc.png'))
        self.ui.btnOpen.setIconSize(QtCore.QSize(100,100))

        self.ui.btnViewer.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_38902_cc.png'))
        self.ui.btnViewer.setIconSize(QtCore.QSize(100,100))
        self.ui.btnViewer.clicked.connect(self.spawn_new_viewer)

        self.ui.btnFlowchart.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_907242_cc.png'))
        self.ui.btnFlowchart.setIconSize(QtCore.QSize(100,100))

        self.ui.btnPlot.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_635936_cc.png'))
        self.ui.btnPlot.setIconSize(QtCore.QSize(100,100))

        self.ui.btnClustering.setIcon(QtGui.QIcon('./MesmerizeCore/icons/noun_195949_cc.png'))
        self.ui.btnClustering.setIconSize(QtCore.QSize(100,100))

        self.viewers = []

        configuration.projPath = '/home/kushal/mesmerize_test_proj'

    def create_new_project(self):
        pass

    def open_project(self):
        pass

    def find_recent_projects(self):
        pass

    def populate_recent_projects_list(self):
        pass

    def spawn_new_viewer(self):
        # Interpret image data as row-major instead of col-major
        pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
        ## Create window with ImageView widget
        viewerWindow = viewer_main_window.MainWindow()  # QtWidgets.QMainWindow()
        viewerWindow.resize(1460, 950)
        viewer = pyqtgraphCore.ImageView(parent=viewerWindow)
        viewerWindow.viewer_reference = viewer
        assert isinstance(viewer, pyqtgraphCore.ImageView)
        viewerWindow.setCentralWidget(viewer)
        #        self.projBrowser.ui.openViewerBtn.clicked.connect(self.showViewer)
        viewerWindow.setWindowTitle('Mesmerize - Viewer -' + str(len(self.viewers)))
        self.ui.listWidgetViewers.addItem(str(len(self.viewers)))

        self.viewers.append(viewerWindow)
        self.ui.listWidgetViewers.itemDoubleClicked.connect(self.show_selected_viewer)
        self.viewers[-1].show()

    def show_selected_viewer(self, s: QtWidgets.QListWidgetItem):
        # i = self.ui.listWidgetViewers.indexFromItem(s)
        # assert isinstance(i, QtCore.QModelIndex)
        # i = i.column(0)
        # i = self.ui.listWidgetViewers.currentIndex()
        i = int(s.data(0))
        self.viewers[i].show()

    def spawn_new_flowchart(self):
        pass

    def spawn_new_plot_gui(self):
        pass

    def spawn_new_clustering_gui(self):
        pass
