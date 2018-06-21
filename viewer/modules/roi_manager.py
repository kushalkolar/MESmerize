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
from functools import partial


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.manager = managers.ManagerManual(self.ui, self.vi)
        self.vi.viewer.workEnv.rois = self.manager.roi_list
        self.vi.viewer.ui.splitter.setEnabled(True)

        action_add_ellipse_roi = QtWidgets.QWidgetAction(self)
        action_add_ellipse_roi.setText('Add Ellipse ROI')
        action_add_ellipse_roi.triggered.connect(partial(self.add_manual_roi, 'EllipseROI'))

        self.btnAddROIMenu = QtWidgets.QMenu(self)
        self.btnAddROIMenu.addAction(action_add_ellipse_roi)

        self.ui.btnAddROI.clicked.connect(partial(self.add_manual_roi, 'PolyLineROI'))
        self.ui.btnAddROI.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.btnAddROI.customContextMenuRequested.connect(self.btnAddROI_context_menu_requested)

        self.ui.btnSwitchToManualMode.clicked.connect(self.start_manual_mode)

        # self.ui.btnSetROITag.clicked.connect(self.set_roi_tag)
    def btnAddROI_context_menu_requested(self, p):
        self.btnAddROIMenu.exec_(self.ui.btnAddROI.mapToGlobal(p))

    def start_cnmfe_mode(self, cnmA, cnmC, idx_components, dims):
        print('staring cnmfe mode in roi manager')
        if len(self.manager.roi_list) > 0:
            if QtWidgets.QMessageBox.warning(self, 'Discard ROIs?',
                                             'You have unsaved ROIs in your work environment.'
                                             'Would you like to discard them and continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            else:
                del self.manager

        self.ui.btnAddROI.setDisabled(True)
        self.manager = managers.ManagerCNMFE(self.ui, self.vi, cnmA, cnmC, idx_components, dims)
        self.manager.add_all_components()
        self.vi.viewer.workEnv.rois = self.manager.roi_list
        self.ui.btnSwitchToManualMode.setEnabled(True)

    def start_manual_mode(self):
        if len(self.manager.roi_list) > 0:
            if QtWidgets.QMessageBox.warning(self, 'Discard ROIs?',
                                             'You have unsaved ROIs in your work environment.'
                                             'Would you like to discard them and continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            elif not isinstance(self.manager, managers.ManagerManual):
                del self.manager

                self.manager = managers.ManagerManual(self.ui, self.vi)

        self.ui.btnAddROI.setEnabled(True)
        self.vi.viewer.workEnv.rois = self.manager.roi_list
        self.ui.btnSwitchToManualMode.setDisabled(True)

    def add_manual_roi(self, shape):
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self,
                                          'Empty Work Environment',
                                          'You cannot add ROIs to an empty work environment')
            return
        self.manager.add_roi(shape)

    # def set_roi_tag(self):
    #     if self.manager.roi_list.list_widget_tags.currentRow() == -1 or self.manager.roi_list.list_widget.currentRow() == -1:
    #         QtWidgets.QMessageBox.question(self, 'Message',
    #                                        'Select an ROI Definition from the list if you want to add tags ',
    #                                        QtWidgets.QMessageBox.Ok)
    #         return
    #
    #     tag = self.ui.lineEditROITag.text()
    #     self.manager.roi_list.set_tag(tag)
    #
    #     self.ui.lineEditROITag.clear()
    #
    #     max_ix = self.manager.roi_list.list_widget_tags.count() - 1
    #     next_ix = self.manager.roi_list.list_widget_tags.currentRow() + 1
    #     self.manager.roi_list.list_widget_tags.setCurrentRow(max(max_ix, next_ix))

    def add_roi_tags_list_text(self):
        pass

    def show_all_rois(self):
        pass

    def package_for_project(self):
        pass