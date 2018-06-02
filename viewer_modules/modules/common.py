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
from pyqtgraphCore import imageview
from MesmerizeCore.packager import viewerWorkEnv
import numpy as np
# import abc
# import multiprocessing


class ViewerInterface:
    def __init__(self, viewer_ref):
        assert isinstance(viewer_ref, imageview.ImageView)
        self.viewer_ref = viewer_ref

    def VIEWER_update_workEnv(self):
        self.viewer_ref.setImage(self.viewer_ref.workEnv.imgdata.seq.T, pos=(0, 0), scale=(1, 1),
                                   xvals=np.linspace(1, self.viewer_ref.workEnv.imgdata.seq.T.shape[0],
                                                     self.viewer_ref.workEnv.imgdata.seq.T.shape[0]))

    def VIEWER_enable_ui(self, b):
        self.viewer_ref.ui.splitter.setEnabled(b)

    def VIEWER_discard_workEnv(self, clear_sample_id=False):
        if self.viewer_ref.workEnv.isEmpty:
            return True
        if (self.viewer_ref.workEnv.saved is False) and (QtWidgets.QMessageBox.warning(self.viewer_ref, 'Warning!',
                         'You have unsaved work in your environment. Would you like to discard them and continue?',
                         QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)) == QtWidgets.QMessageBox.No:
            return False
        self._clear_workEnv(clear_sample_id)
        return True

    def _clear_workEnv(self, clear_sample_id=False):
        # Remove any ROIs and associated curves on the plot
        for i in range(0, len(self.viewer_ref.workEnv.ROIList)):
            self.viewer_ref.delROI(self.viewer_ref.workEnv.ROIList[0])
            '''calls delROI method to remove the ROIs from the list.
            You cannot simply reset the list to ROI = [] because objects must be removed from the scene
            and curves removed from the plot. This is what delROI() does. Removes the 0th once in each
            iteration, number of iterations = len(ROIlist)'''

        self.viewer_ref.priorlistwROIsSelection = None

        # In case the user decided to add some of their own curves that don't correspond to the ROIs
        if len(self.viewer_ref.workEnv.CurvesList) != 0:
            for i in range(0, len(self.viewer_ref.workEnv.CurvesList)):
                self.viewer_ref.workEnv.CurvesList[i].clear()

        # re-initialize ROI and curve lists
        self.viewer_ref.workEnv.dump()
        # self.viewer_ref.setImage(np.array([0]))
        #        self.viewer_ref._remove_workEnv_observer()
        self.viewer_ref.ui.comboBoxStimMaps.setDisabled(True)

        # Remove the background bands showing stimulus times.
        if len(self.viewer_ref.currStimMapBg) > 0:
            for item in self.viewer_ref.currStimMapBg:
                self.viewer_ref.ui.roiPlot.removeItem(item)

            self.viewer_ref.currStimMapBg = []

        # self.viewer_ref.initROIPlot()
        self.viewer_ref.enableUI(False, clear_sample_id)

    # def VIEWER_workEnv_checkSaved(self):
    #     if self.viewer_ref.watcherStarted:
    #         return
    #
    #     for ui_element in self.viewer_ref.ui.tabBatchParams.children():
    #         if type(ui_element) != QtWidgets.QLabel:
    #             if type(
    #                     ui_element) == QtWidgets.QSpinBox:  # or QtWidgets.QPushButton or QtWidgets.QCheckBox or QtWidgets.QSpinBox or QtWidgets.QSlider):
    #                 ui_element.valueChanged['int'].connect(self.viewer_ref._workEnv_changed)
    #                 print(self.viewer_ref.workEnv.saved)
    #             elif type(ui_element) == QtWidgets.QLineEdit:
    #                 ui_element.textChanged.connect(self.viewer_ref._workEnv_changed)
    #             elif type(ui_element) == QtWidgets.QSlider:
    #                 ui_element.valueChanged['int'].connect(self.viewer_ref._workEnv_changed)
    #     for ui_element in self.viewer_ref.ui.tabROIs.children():
    #         if type(ui_element) == QtWidgets.QLineEdit:
    #             ui_element.textChanged.connect(self.viewer_ref._workEnv_changed)
    #         elif type(ui_element) == QtWidgets.QPlainTextEdit:
    #             ui_element.textChanged.connect(self.viewer_ref._workEnv_changed)
    #     self.viewer_ref.watcherStarted = True

    def VIEWER_workEnv_changed(self, element=None):
        if self.viewer_ref.workEnv is not None:
            self.viewer_ref.workEnv.saved = False

# class BatchRunSignals(QtCore.QObject):
#     sigFinished = QtCore.pyqtSignal()
#
#
# # Base Batch Run Interface abstract class.
# class BatchRunInterface(multiprocessing.Process, QtCore.QObject):
#
#
#     def __init__(self):
#         multiprocessing.Process.__init__(self)
#         QtCore.QObject.__init__(self)
#         # super(BatchRunInterface, self).__init__()
#         # self.signals = BatchRunSignals()
#         self.output_params = {'output': 'fail',
#                               'output_info': ''
#                               }
#
#     # abstract method, MUST be included if you use this to create your own module
#     # def run(self):
#     #     pass
#
#     def set_inputs(self, q, input_workEnv, input_params):
#         self.q = q
#         self.input_workEnv = input_workEnv
#         self.input_params = input_params
#         print('************** Item inputs set **************')
#
#     # abstract method, MUST be included if you use this to create your own module
#     # def get_output(self):
#     #     pass
#
#     # abstract method, MUST be included if you use this to create your own module
#     @staticmethod
#     def show_output(output_workEnv, output_params):
#         pass
