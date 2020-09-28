#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerUtils
from .pytemplates.roi_manager_pytemplate import *
from .roi_manager_modules import managers
from .roi_manager_modules.roi_types import *
from functools import partial
import traceback


class ModuleGUI(QtWidgets.QDockWidget):
    """The GUI front-end for the ROI Manager module"""
    def __init__(self, parent, viewer_reference):
        """Instantiate attributes"""
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.manager = managers.ManagerManual(self, self.ui, self.vi) #: The back-end manager instance.
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

        self.ui.listWidgetROIs.currentRowChanged.connect(self.request_zlevel)

        self.ui.pushButtonImportFromImageJ.clicked.connect(self.import_from_imagej)

        self.installEventFilter(self)

        self.ui.lineEditROITag.sig_key_right.connect(self.play_forward)
        self.ui.lineEditROITag.sig_key_left.connect(self.play_backward)

        self.ui.lineEditROITag.sig_key_home.connect(self.img_seq_home)
        self.ui.lineEditROITag.sig_key_end.connect(self.img_seq_end)

        self.ui.horizontalSliderSpotSize.valueChanged.connect(self.set_spot_size)

        for w in \
            [
                self.ui.radioButton_curve_data,
                self.ui.radioButton_dfof,
                self.ui.radioButton_spikes
            ]:
            w.clicked.connect(self.set_curveplot_datatype)

    def eventFilter(self, QObject, QEvent):
        """Set some keyboard shortcuts"""
        if QEvent.type() == QEvent.KeyPress:

            if len(self.manager.roi_list) < 1:
                return super(ModuleGUI, self).eventFilter(QObject, QEvent)

            max_ix = len(self.manager.roi_list) - 1

            if QEvent.key() == QtCore.Qt.Key_PageUp:
                ix = self.manager.roi_list.current_index
                self.ui.listWidgetROIs.setCurrentRow(max(0, ix - 1))

            elif QEvent.key() == QtCore.Qt.Key_PageDown:
                ix = self.manager.roi_list.current_index
                self.ui.listWidgetROIs.setCurrentRow(min(max_ix, ix + 1))

            elif QEvent.key() == QtCore.Qt.Key_Right:
                self.play_forward()

            elif QEvent.key() == QtCore.Qt.Key_Left:
                self.play_backward()

        return super(ModuleGUI, self).eventFilter(QObject, QEvent)

    def play_forward(self):
        self.vi.viewer.play(500)

    def play_backward(self):
        self.vi.viewer.play(-500)

    def img_seq_home(self):
        self.vi.viewer.setCurrentIndex(0)
        self.vi.viewer.play(0)

    def img_seq_end(self):
        self.vi.viewer.setCurrentIndex(self.vi.viewer.getProcessedImage().shape[0] - 1)
        self.vi.viewer.play(0)

    def _list_widget_context_menu_requested(self, p):
        self.list_widget_context_menu.exec_(self.ui.listWidgetROIs.mapToGlobal(p))

    def slot_delete_roi_menu(self):
        """Delete the currently selected ROI"""
        if hasattr(self, 'manager'):
            if isinstance(self.manager, managers.ManagerCNMFROI):
                self.manager.update_idx_components(self.manager.roi_list.current_index)

            del self.manager.roi_list[self.manager.roi_list.current_index]

    def btnAddROI_context_menu_requested(self, p):
        self.btnAddROIMenu.exec_(self.ui.btnAddROI.mapToGlobal(p))

    def start_backend(self, type_str: str):
        """Choose backend, one of the Manager classes in the managers module."""

        if hasattr(self, 'manager'):
            del self.manager

        if type_str == 'Manual':
            self.start_manual_mode()
            self.disable_curve_options(True)
            self.ui.radioButton_curve_data.setChecked(True)
            return

        self.ui.btnAddROI.setDisabled(True)  # only used for manual ROIs
        self.disable_curve_options(False)  # enable dfof and spike options

        backend = f'Manager{type_str}'
        manager = getattr(managers, backend)

        self.manager = manager(self, self.ui, self.vi)
        self.vi.viewer.workEnv.roi_manager = self.manager

        self.ui.btnSwitchToManualMode.setEnabled(True)
        self.ui.radioButton_curve_data.setChecked(True)

        print(f'ROI Manager backend set to: {backend}')

        return self.manager

    def start_manual_mode(self):
        """Start in manual mode. Creates a new back-end manager instance (Uses ManagerManual)"""
        print('ROI back-end set to: ManagerManual')

        if hasattr(self, 'manager'):
            del self.manager
        self.manager = managers.ManagerManual(self, self.ui, self.vi)

        self.ui.btnAddROI.setEnabled(True)
        self.vi.viewer.workEnv.roi_manager = self.manager
        self.ui.btnSwitchToManualMode.setDisabled(True)

    def set_curveplot_datatype(self):
        if self.ui.radioButton_curve_data.isChecked():
            datatype = 'curve'
        elif self.ui.radioButton_dfof.isChecked():
            datatype = 'dfof'
        elif self.ui.radioButton_spikes.isChecked():
            datatype = 'spike'

        if isinstance(self.manager, managers.ManagerVolMultiCNMFROI):
            for roi in self.manager.roi_list:
                roi.curve_data_type = datatype
                if roi.visible:
                    roi.set_viewer_curveplot(datatype)

        else:
            for roi in self.manager.roi_list:
                roi.set_viewer_curveplot(datatype)

    def disable_curve_options(self, b):
        self.ui.radioButton_curve_data.setDisabled(b)
        self.ui.radioButton_dfof.setDisabled(b)
        self.ui.radioButton_spikes.setDisabled(b)

    def add_manual_roi(self, shape: str):
        """Add a manual ROI. Just calls ManagerManual.add_roi"""
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
        """
        Gets all the ROI states so that they can be packaged along with
        the rest of the work environment to be saved as a project Sample
        """

        states = self.manager.get_all_states()
        return states

    def set_all_from_states(self, states: dict):
        """Set all the ROIs from a states dict. Instantiates the appropriate back-end Manager"""
        if 'roi_type' not in states.keys():
            raise TypeError('`roi_type` not specified in states dict')

        roi_class = states["roi_type"]

        if roi_class not in globals().keys():
            raise TypeError(f'Specified ROI type <{roi_class}> not found in available ROI types.')

        # All scatter types, CNMF(E), Suite2p, VolCNMF etc.
        if issubclass(globals()[roi_class], ScatterROI):
            self.start_backend(states['roi_type'])
            self.manager.restore_from_states(states)

        # Manual ROI classes
        elif issubclass(globals()[roi_class], ManualROI):
            self.start_manual_mode()
            self.manager.restore_from_states(states)

    def import_from_imagej(self):
        """Import ROIs from ImageJ zip file"""
        path = QtWidgets.QFileDialog.getOpenFileName(None, 'Import ImageJ ROIs', '', '(*.zip)')
        if path == '':
            return
        self.start_manual_mode()
        try:
            self.manager.import_from_imagej(path[0])
        except:
            QtWidgets.QMessageBox.warning(None, 'File open Error',
                                          'Could not open the chosen file.\n'
                                          'It might not be an ImageJ ROIs file' + traceback.format_exc())

    def set_spot_size(self, size: int):
        if hasattr(self.manager, 'set_spot_size'):
            self.manager.set_spot_size(size)

    def request_zlevel(self, roi_ix):
        if not hasattr(self, 'manager'):
            return

        if not isinstance(self.manager, managers.ManagerVolROI):
            return

        roi = self.manager.roi_list[roi_ix]

        if not roi.visible:
            self.vi.viewer.ui.verticalSliderZLevel.setValue(roi.zcenter)
