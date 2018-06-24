#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 19 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.imageview import ImageView
from ..core.viewer_work_environment import ViewerWorkEnv
import numpy as np
# import abc
# import multiprocessing


class ViewerInterface:
    def __init__(self, viewer_reference):
        """
        :type viewer_reference: ImageView
        """
        # assert isinstance(viewer_reference, ImageView)
        self.viewer = viewer_reference
        self.work_env = self.viewer.workEnv
        self.roi_manager = None

    def update_workEnv(self):
        self.viewer.status_bar_label.showMessage('Updating work environment, please wait...')

        self.viewer.setImage(self.viewer.workEnv.imgdata.seq.T, pos=(0, 0), scale=(1, 1),
                                   xvals=np.linspace(1, self.viewer.workEnv.imgdata.seq.T.shape[0],
                                                     self.viewer.workEnv.imgdata.seq.T.shape[0]))
        self.viewer.workEnv.roi_manager = self.viewer.parent().roi_manager.manager
        self.viewer.status_bar_label.showMessage('Finished updating work environment.')

    def enable_ui(self, b):
        self.viewer.ui.splitter.setEnabled(b)

    def discard_workEnv(self, clear_sample_id=False):
        if self.viewer.workEnv.isEmpty:
            return True
        if (self.viewer.workEnv.saved is False) and (QtWidgets.QMessageBox.warning(self.viewer, 'Warning!',
                         'You have the following unsaved changes in your work environment. '
                         'Would you like to discard them and continue?\n\n' +
                             ' > '.join(self.viewer.workEnv.changed_items),
                         QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)) == QtWidgets.QMessageBox.No:
            self.viewer.status_bar_label.showMessage('Work environment left unchanged.')

            return False
        self._clear_workEnv(clear_sample_id)
        return True

    def _clear_workEnv(self, clear_sample_id=False):
        if self.viewer.workEnv.roi_manager is not None:
            self.viewer.workEnv.roi_manager.clear()
        # re-initialize ROI and curve lists
        self.viewer.workEnv.dump()
        # self.viewer.setImage(np.array([0]))
        #        self.viewer._remove_workEnv_observer()
        self.viewer.ui.comboBoxStimMaps.setDisabled(True)

        # Remove the background bands showing stimulus times.
        if len(self.viewer.currStimMapBg) > 0:
            for item in self.viewer.currStimMapBg:
                self.viewer.ui.roiPlot.removeItem(item)

            self.viewer.currStimMapBg = []
        self.viewer.workEnv.saved = True

        self.viewer.status_bar_label.showMessage('Work environment cleared.')

        # self.viewer.initROIPlot()
        # self.viewer.enableUI(False, clear_sample_id)

    def workEnv_changed(self, element=None):
        if self.viewer.workEnv is not None:
            self.viewer.workEnv.saved = False

        if element is not None:
            self.viewer.workEnv.changed_items.append(element)
