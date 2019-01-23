#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 1 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore import LineSegmentROI, ROI
import numpy as np
from .resize import ResizeDialogBox
from ..core.common import ViewerInterface
from math import sqrt
from .image_projections import display_projection


class ImageMenu:
    def __init__(self, viewer_interface):
        assert isinstance(viewer_interface, ViewerInterface)
        self.vi = viewer_interface

        self.measure_line = None
        self.measure_line_ = None
        self.crop_roi = None

    def reset_scale(self):
        self.vi.update_workEnv()

    def resize(self):
        if not hasattr(self, 'resize_dialog'):
            self.resize_dialog = ResizeDialogBox(self.vi)
        self.resize_dialog.show()

    def crop(self):
        if self.crop_roi is None:
            self.vi.viewer.status_bar_label.showMessage('Create your crop region and then click on "Crop" again in the '
                                                      '"Image" menu to crop to the selected region')
            self.crop_roi = ROI(pos=[0, 0], size=(0.5 * np.mean([self.vi.viewer.image.shape[1],
                                                                 self.vi.viewer.image.shape[2]])), removable=True)
            self.crop_roi.sigRemoveRequested.connect(self.remove_crop_roi)
            self.crop_roi.addScaleHandle([1, 1], [0, 0])
            self.crop_roi.addScaleHandle([0, 0], [0, 0])
            self.vi.viewer.view.addItem(self.crop_roi)
        else:
            self.vi.viewer.status_bar_label.showMessage('Cropping to your selection, please wait...')
            point_l = self.vi.viewer.getImageItem().mapFromScene(self.crop_roi.getSceneHandlePositions()[1][1])
            point_r = self.vi.viewer.getImageItem().mapFromScene(self.crop_roi.getSceneHandlePositions()[0][1])

            pl = (int(point_l.x()), int(point_l.y()))
            pr = (int(point_r.x()), int(point_r.y()))
            self.remove_crop_roi()

            seq = self.vi.viewer.image[:, pl[1]:pr[1], pl[0]:pr[0]]
            self.vi.viewer.workEnv.imgdata.seq = seq.T
            self.vi.update_workEnv()
            self.vi.viewer.status_bar_label.showMessage('Cropping completed!')

    def remove_crop_roi(self):
        self.vi.viewer.view.removeItem(self.crop_roi)
        self.crop_roi = None
        self.vi.viewer.status_bar_label.clearMessage()

    def draw_measure_line(self, ev):
        if self.measure_line_ is None:
            self.measure_line_ = self.vi.viewer.view.mapSceneToView(ev.pos())
            self.vi.viewer.status_bar_label.showMessage('Click on a second point in the image to '
                                                      'finish drawing the line')
            # for item in self.vi.viewer.view.items:
            #     if isinstance(item, LineSegmentROI):
            #         self.vi.viewer.view.removeItem(item)

        else:
            self.measure_line = LineSegmentROI(positions=(self.measure_line_,
                                                         self.vi.viewer.view.mapSceneToView(ev.pos())))
            self.vi.viewer.view.addItem(self.measure_line)

            self.vi.viewer.scene.sigMouseClicked.disconnect(self.draw_measure_line)
            self.vi.viewer.status_bar_label.showMessage('Now click "Measure" in the "Image" menu once again to get '
                                                      'your measurements')

    def measure_tool(self, ev=False):
        if self.measure_line is None:
            self.vi.viewer.status_bar_label.showMessage('Click on a point in the image to draw the first point of a line')
            self.vi.viewer.scene.sigMouseClicked.connect(self.draw_measure_line)
            return False

        elif self.measure_line is not None:
            dx = abs(self.measure_line.listPoints()[0][0] - self.measure_line.listPoints()[1][0])
            dy = abs(self.measure_line.listPoints()[0][1] - self.measure_line.listPoints()[1][1])
            dist = sqrt((dx**2 + dy**2))
            self.vi.viewer.scene.removeItem(self.measure_line)
            self.measure_line = None
            self.measure_line_ = None
            QtWidgets.QMessageBox.information(None, 'Measurements',
                                              '\ndx = ' + str(dx) +\
                                              '\ndy = ' + str(dy) +\
                                              '\ndistance = ' + str(dist))
            return True

    def mean_projection(self):
        display_projection('mean', self.vi.viewer.workEnv.imgdata.seq, self.vi.viewer.ui.label_curr_img_seq_name)

    def max_projection(self):
        display_projection('max', self.vi.viewer.workEnv.imgdata.seq, self.vi.viewer.ui.label_curr_img_seq_name)

    def std_projection(self):
        display_projection('std', self.vi.viewer.workEnv.imgdata.seq, self.vi.viewer.ui.label_curr_img_seq_name)
