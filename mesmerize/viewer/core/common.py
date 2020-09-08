#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 19 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from ...pyqtgraphCore.imageview import ImageView
import numpy as np
# import abc
# import multiprocessing


class ViewerUtils(QtCore.QObject):
    """
    Some utility functions for interfacing viewer.core.ViewerWorkEnv with the pyqtgraphCore.ImageView widget
    """
    def __init__(self, viewer_reference: ImageView):
        """
        :type viewer_reference: ImageView
        """
        QtCore.QObject.__init__(self)
        # assert isinstance(viewer_reference, ImageView)
        self.viewer = viewer_reference  #: reference to the pyqtgraph ImageView widget instance (viewer)
        self.work_env = self.viewer.workEnv  #: ViewerWorkEnv instance
        self.roi_manager = None

    def update_workEnv(self):
        """
        Update the ImageView widget with the ViewerWorkEnv
        """

        self.viewer.status_bar_label.showMessage('Updating work environment, please wait...')
        self.viewer.parent().show()

        if self.viewer.workEnv.imgdata.ndim == 4:
            self.viewer.set_zlevel_ui_visible(True)
            self.viewer.ui.verticalSliderZLevel.setMaximum(self.viewer.workEnv.imgdata.z_max)
            self.viewer.ui.verticalSliderZLevel.setValue(0)
            self.viewer.ui.spinBoxZLevel.setMaximum(self.viewer.workEnv.imgdata.z_max)
        else:
            self.viewer.set_zlevel_ui_visible(False)

        self.viewer.setImage(self.viewer.workEnv.imgdata.seq.T, pos=(0, 0), scale=(1, 1),
                                   xvals=np.linspace(1, self.viewer.workEnv.imgdata.seq.T.shape[0],
                                                     self.viewer.workEnv.imgdata.seq.T.shape[0]))

        self.viewer.workEnv.roi_manager = self.viewer.parent().roi_manager.manager
        if self.viewer.workEnv.stim_maps is not None:
            # print(self.viewer.workEnv.stim_maps)
            smm = self.viewer.parent().run_module('stimulus_mapping')
            smm.set_all_data(self.viewer.workEnv.stim_maps)
            try:
                smm.set_timeline(1)
            except:
                pass

        self.viewer.sig_workEnv_changed.emit(self.viewer.workEnv)

        self.viewer.status_bar_label.showMessage('Finished updating work environment.')

    def set_statusbar(self, msg):
        """
        Set the status bar message in the viewer window.

        :param msg: text to display in the status bar
        """
        self.viewer.status_bar_label.showMessage(msg)

    def enable_ui(self, b):
        self.viewer.ui.splitter.setEnabled(b)

    def discard_workEnv(self, clear_sample_id=False):
        """
        Ask the user if they want to discard their work environment. If Yes, calls _clear_workEnv()
        """

        self.viewer.parent().show()

        if self.viewer.workEnv.isEmpty:
            return True

        changes = self.viewer.workEnv.changed_items

        if (self.viewer.workEnv.saved is False) and (QtWidgets.QMessageBox.warning(self.viewer, 'Warning!',
                         'You have the following unsaved changes in your work environment. '
                         'Would you like to discard them and continue?\n\n' +
                             ' > '.join(sorted(set(changes), key=changes.index)),
                         QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)) == QtWidgets.QMessageBox.No:
            self.viewer.status_bar_label.showMessage('Work environment left unchanged.')

            return False
        self._clear_workEnv(clear_sample_id)
        return True

    def _clear_workEnv(self, clear_sample_id=False):
        """
        Cleanup of the ViewerWorkEnv and ImageView widget
        """

        if self.viewer.workEnv.roi_manager is not None:
            self.viewer.workEnv.roi_manager.clear()
        # re-initialize ROI and curve lists
        self.viewer.workEnv.clear()
        self.viewer.clear()
        self.viewer.workEnv.saved = True
        self.viewer.ui.label_curr_img_seq_name.setText('EMPTY')
        self.viewer.set_zlevel_ui_visible(False)
        self.viewer.status_bar_label.showMessage('Work environment cleared.')

    def workEnv_changed(self, element=None):
        if self.viewer.workEnv is not None:
            self.viewer.workEnv.saved = False

        if element is not None:
            self.viewer.workEnv.changed_items.append(element)
