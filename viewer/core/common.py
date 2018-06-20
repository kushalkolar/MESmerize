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

    def update_workEnv(self):
        self.viewer.setImage(self.viewer.workEnv.imgdata.seq.T, pos=(0, 0), scale=(1, 1),
                                   xvals=np.linspace(1, self.viewer.workEnv.imgdata.seq.T.shape[0],
                                                     self.viewer.workEnv.imgdata.seq.T.shape[0]))

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
            return False
        self._clear_workEnv(clear_sample_id)
        return True

    def _clear_workEnv(self, clear_sample_id=False):
        # Remove any ROIs and associated curves on the plot
        for i in range(0, len(self.viewer.workEnv.ROIList)):
            self.viewer.delROI(self.viewer.workEnv.ROIList[0])
            '''calls delROI method to remove the ROIs from the list.
            You cannot simply reset the list to ROI = [] because objects must be removed from the scene
            and curves removed from the plot. This is what delROI() does. Removes the 0th once in each
            iteration, number of iterations = len(ROIlist)'''

        self.viewer.priorlistwROIsSelection = None

        # In case the user decided to add some of their own curves that don't correspond to the ROIs
        if len(self.viewer.workEnv.CurvesList) != 0:
            for i in range(0, len(self.viewer.workEnv.CurvesList)):
                self.viewer.workEnv.CurvesList[i].clear()

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

        # self.viewer.initROIPlot()
        self.viewer.enableUI(False, clear_sample_id)

    def workEnv_changed(self, element=None):
        if self.viewer.workEnv is not None:
            self.viewer.workEnv.saved = False

        if element is not None:
            self.viewer.workEnv.changed_items.append(element)
