#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerInterface
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.roi_manager_pytemplate import *
import numpy as np
from common import configuration
from ..core.viewer_work_environment import ViewerWorkEnv
from pyqtgraphCore.graphicsItems import ROI
from .roi_manager_modules import managers


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.manager = managers.ManagerManual(self.vi)

        self.ui.btnAddROI.clicked.connect(self.add_roi)
        self.ui.btnSetROITag.clicked.connect(self.set_roi_tag)

    def _generate_roi_list_ui(self):
        self.ui.verticalLayoutROIList.addWidget(self.manager.roi_list.show_all_checkbox)
        self.ui.verticalLayoutROIList.addWidget(self.manager.roi_list.live_plot_checkbox)
        self.ui.verticalLayoutROIList.addWidget(self.manager.roi_list.list_widget)
        self.ui.verticalLayoutTags.addWidget(self.manager.roi_list.list_widget_tags)
        if isinstance(self.manager, managers.ManagerManual):
            self.ui.verticalLayoutROIList.addWidget(self.manager.roi_list.live_plot_checkbox.setEnabled(True))

    def _delete_roi_list_ui(self):
        self.manager.roi_list.show_all_checkbox.deleteLater()
        self.manager.roi_list.list_widget.deleteLater()
        self.manager.roi_list.live_plot_checkbox.deleteLater()
        self.manager.roi_list.list_widget_tags.deleteLater()

    def start_cnmfe_mode(self, cnmA, cnmC, idx_components, dims):
        if len(self.manager.roi_list) > 0:
            if QtWidgets.QMessageBox.warning(self, 'Discard ROIs?',
                                             'You have unsaved ROIs in your work environment.'
                                             'Would you like to discard them and continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            else:
                self._delete_roi_list_ui()
                del self.manager

            self.ui.btnAddROI.setDisabled(True)
            self.manager = managers.ManagerCNMFE(self.vi, cnmA, cnmC, idx_components, dims)
            self._generate_roi_list_ui()
            self.manager.add_all_components()

    def start_manual_mode(self):
        if len(self.manager.roi_list) > 0:
            if QtWidgets.QMessageBox.warning(self, 'Discard ROIs?',
                                             'You have unsaved ROIs in your work environment.'
                                             'Would you like to discard them and continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            elif not isinstance(self.manager, managers.ManagerManual):
                self._delete_roi_list_ui()
                del self.manager

                self.manager = managers.ManagerManual(self.vi)

        self.ui.btnAddROI.setEnabled(True)
        self._generate_roi_list_ui()

    def add_roi(self):
        self.manager.add_roi()

    def set_roi_tag(self):
        if self.manager.roi_list.list_widget_tags.currentRow() == -1 or self.manager.roi_list.list_widget.currentRow() == -1:
            QtWidgets.QMessageBox.question(self, 'Message',
                                           'Select an ROI Definition from the list if you want to add tags ',
                                           QtWidgets.QMessageBox.Ok)
            return

        tag = self.ui.lineEditROITag.text()
        self.manager.roi_list.set_tag(tag)

        self.ui.lineEditROITag.clear()

        max_ix = self.manager.roi_list.list_widget_tags.count() - 1
        next_ix = self.manager.roi_list.list_widget_tags.currentRow() + 1
        self.manager.roi_list.list_widget_tags.setCurrentRow(max(max_ix, next_ix))

    def add_roi_tags_list_text(self):
        pass

    def show_all_rois(self):
        pass

    def package_for_project(self):
        pass