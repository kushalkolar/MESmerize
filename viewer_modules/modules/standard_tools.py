#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.standard_tools_pytemplate import *
from MesmerizeCore.packager import viewerWorkEnv
from pyqtgraphCore.graphicsItems.ROI import ROI
import numpy as np
from skimage import transform
import numba
from math import sqrt
from pyqtgraphCore import LineSegmentROI


class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnCrop.clicked.connect(self.crop)
        self.ui.btnResizeImgseq.clicked.connect(self.resize_imgseq)
        self.ui.btnResetScale.clicked.connect(self.reset_scale)
        self.ui.btnPlot.clicked.connect(self.live_plot)
        self.ui.btnEditMetaData.clicked.connect(self.edit_meta_data)
        self.ui.btnMeasureTool.clicked.connect(self.measure_tool)
        self.measure_line = None
        self.measure_line_ = None

    def crop(self, ev):
        if ev:
            self.crop_roi = ROI(pos=[0, 0], size=(0.2 * np.mean([self.viewer_ref.image.shape[1], self.viewer_ref.image.shape[2]])))
            self.crop_roi.addScaleHandle([1, 1], [0, 0])
            self.viewer_ref.view.addItem(self.crop_roi)
        else:
            point_r = self.viewer_ref.getImageItem().mapFromScene(self.crop_roi.getSceneHandlePositions()[0][1])
            point_l = self.viewer_ref.getImageItem().mapFromScene(self.crop_roi.getSceneHandlePositions()[1][1])
            self.viewer_ref.view.removeItem(self.crop_roi)
            self.viewer_ref.workEnv.imgdata.seq = self.viewer_ref.workEnv.imgdata[point_l[1]:point_r[1], point_l[0]:point_r[0], :]
            self.VIEWER_update_workEnv()

    # def _resize_fast(self, factor):
    #     self.resize_gui.deleteLater()
    #     try:
    #         self.resize_gui = None
    #     except Exception as e:
    #         print(e)
    #
    #     template = transform.rescale(self.viewer_ref.workEnv.imgdata.seq[:, :, :2], factor)
    #     r = np.zeros((template.shape[0],
    #                   template.shape[1],
    #                   self.viewer_ref.workEnv.imgdata.seq.shape[2]),
    #                  dtype=self.viewer_ref.workEnv.imgdata.seq.dtype)
    #
    #     for i in range(0, self.viewer_ref.workEnv.imgdata.seq[2]):
    #         r[:, :, i] = transform.rescale(self.viewer_ref.workEnv.imgdata.seq[:, :, i], factor, preserve_range=True)
    #
    #     self.viewer_ref.workEnv.imgdata.seq = r
    #     self.VIEWER_update_workEnv()

    # def reset_scale(self):
    #     self.VIEWER_update_workEnv()

    def live_plot(self):
        pass

    def edit_meta_data(self):
        pass

    def draw_measure_line(self, ev):
        if self.measure_line_ is None:
            self.measure_line_ = self.viewer_ref.view.mapSceneToView(ev.pos())
            print(self.measure_line_)
        else:
            self.measure_line = LineSegmentROI(positions=(self.measure_line_,
                                                         self.viewer_ref.view.mapSceneToView(ev.pos())))
            self.viewer_ref.view.addItem(self.measure_line)

            self.viewer_ref.scene.sigMouseClicked.disconnect(self.draw_measure_line)

    def measure_tool(self, ev):
        if ev and self.measure_line is None:
            self.viewer_ref.scene.sigMouseClicked.connect(self.draw_measure_line)

        elif ev is False and self.measure_line is not None:
            dx = abs(self.measure_line.listPoints()[0][0] - self.measure_line.listPoints()[1][0])
            dy = abs(self.measure_line.listPoints()[0][1] - self.measure_line.listPoints()[1][1])
            dist = sqrt((dx**2 + dy**2))
            self.viewer_ref.scene.removeItem(self.measure_line)
            self.measure_line = None
            self.measure_line_ = None
            QtWidgets.QMessageBox.information(self, 'Measurements',
                                              '\ndx = ' + str(dx) +\
                                              '\ndy = ' + str(dy) +\
                                              '\ndistance = ' + str(dist))



