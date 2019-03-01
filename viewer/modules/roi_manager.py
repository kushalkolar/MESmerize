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
from .pytemplates.roi_manager_pytemplate import *
from .roi_manager_modules import managers
from functools import partial


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.manager = managers.ManagerManual(self, self.ui, self.vi)
        self.vi.viewer.workEnv.roi_manager = self.manager

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

        action_delete_roi = QtWidgets.QWidgetAction(self)
        action_delete_roi.setText('Delete')
        action_delete_roi.triggered.connect(self.slot_delete_roi_menu)

        self.list_widget_context_menu = QtWidgets.QMenu(self)
        self.list_widget_context_menu.addAction(action_delete_roi)

        self.ui.listWidgetROIs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listWidgetROIs.customContextMenuRequested.connect(self._list_widget_context_menu_requested)

    def _list_widget_context_menu_requested(self, p):
        self.list_widget_context_menu.exec_(self.ui.listWidgetROIs.mapToGlobal(p))

    def slot_delete_roi_menu(self):
        if hasattr(self, 'manager'):
            if isinstance(self.manager, managers.ManagerCNMFE):
                self.manager.update_idx_components(self.manager.roi_list.current_index)

            del self.manager.roi_list[self.manager.roi_list.current_index]

    def btnAddROI_context_menu_requested(self, p):
        self.btnAddROIMenu.exec_(self.ui.btnAddROI.mapToGlobal(p))

    def start_cnmfe_mode(self):
        print('staring cnmfe mode in roi manager')

        if hasattr(self, 'manager'):
            del self.manager

        self.ui.btnAddROI.setDisabled(True)
        self.manager = managers.ManagerCNMFE(self, self.ui, self.vi)
        self.vi.viewer.workEnv.roi_manager = self.manager
        self.ui.btnSwitchToManualMode.setEnabled(True)

    def add_all_cnmfe_components(self, *args, **kwargs):
        assert isinstance(self.manager, managers.ManagerCNMFE)
        self.manager.add_all_components(*args, **kwargs)

    def start_manual_mode(self):
        print('staring manual mode')

        if hasattr(self, 'manager'):
            del self.manager
        self.manager = managers.ManagerManual(self, self.ui, self.vi)

        self.ui.btnAddROI.setEnabled(True)
        self.vi.viewer.workEnv.roi_manager = self.manager
        self.ui.btnSwitchToManualMode.setDisabled(True)

    def add_manual_roi(self, shape: str):
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self,
                                          'Empty Work Environment',
                                          'You cannot add ROIs to an empty work environment')
            return
        self.manager.add_roi(shape)

    def add_roi_tags_list_text(self):
        pass

    def show_all_rois(self):
        pass

    def package_for_project(self) -> dict:
        states = self.manager.get_all_states()
        return states

    def set_all_from_states(self, states: dict):
        if states['roi_type'] == 'CNMFROI':
            self.start_cnmfe_mode()
            self.manager.restore_from_states(states)

        elif states['roi_type'] == 'ManualROI':
            self.start_manual_mode()
            self.manager.restore_from_states(states)
