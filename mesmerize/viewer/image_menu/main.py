#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 1 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
from ...pyqtgraphCore import LineSegmentROI, ROI
import numpy as np
from .resize import ResizeDialogBox
from ..core.common import ViewerUtils
from math import sqrt
from .image_projections import display_projection


class ImageMenu:
    def __init__(self, viewer_interface):
        assert isinstance(viewer_interface, ViewerUtils)
        self.vi = viewer_interface

        self.crop_roi = None

        self.projection_windows = []

        self.measure_lines = []
        self._drawing_line = False

        self._prev_mouseclick_pos = None

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

    def action_measure_line_invoked(self):
        if self._drawing_line:
            QtWidgets.QMessageBox.warning(
                self.vi.viewer.parent(),
                'Finish drawing previous line',
                'Click on the image to finish drawing the previous line before drawing a new one',
                QtWidgets.QMessageBox.Ok
            )
            return

        self._drawing_line = True

        self.vi.viewer.status_bar_label.showMessage(
            'Click on a point in the image to draw the first point of a line'
        )

        self.vi.viewer.scene.sigMouseClicked.connect(self.draw_measure_line)

    def draw_measure_line(self, ev):
        self._prev_mouseclick_pos = self.vi.viewer.view.mapSceneToView(ev.pos())

        self.vi.viewer.status_bar_label.showMessage(
            'Click on a second point in the image to finish drawing the line'
        )

        self.vi.viewer.scene.sigMouseClicked.disconnect(self.draw_measure_line)
        self.vi.viewer.scene.sigMouseClicked.connect(self._finish_drawing_measure_line)

    def _finish_drawing_measure_line(self, ev):
        measure_line = LineSegmentROI(
            positions=(
                self._prev_mouseclick_pos,
                self.vi.viewer.view.mapSceneToView(ev.pos())
            ),
            removable=True
        )
        self.vi.viewer.view.addItem(measure_line)

        # changing or hovering on the line will display the distances
        measure_line.sigRegionChanged.connect(self.show_measure_line_distance)
        measure_line.sigHoverEvent.connect(self.show_measure_line_distance)

        # deleting the line
        measure_line.sigRemoveRequested.connect(self.measure_lines.remove)
        measure_line.sigRemoveRequested.connect(self.vi.viewer.scene.removeItem)

        # add to list
        self.measure_lines.append(measure_line)

        self.vi.viewer.scene.sigMouseClicked.disconnect(self._finish_drawing_measure_line)

        self.show_measure_line_distance(measure_line)

        self._drawing_line = False

    def show_measure_line_distance(self, line: LineSegmentROI):
        dx = abs(line.listPoints()[0][0] - line.listPoints()[1][0])
        dy = abs(line.listPoints()[0][1] - line.listPoints()[1][1])
        dist = sqrt((dx ** 2 + dy ** 2))

        self.vi.viewer.status_bar_label.showMessage(
            f"Line distance: dx: {dx:.2f} | dy: {dy:.2f} | distance: {dist:.2f}"
        )

    def mean_projection(self):
        self.vi.viewer.status_bar_label.showMessage('Creating Mean Projection of image sequence, please wait...')
        w = display_projection('mean', self.vi.viewer.workEnv.imgdata.seq,
                               self.vi.viewer.ui.label_curr_img_seq_name.text())
        self.projection_windows.append(w)
        self.vi.viewer.status_bar_label.showMessage('Projection displayed.')

    def max_projection(self):
        self.vi.viewer.status_bar_label.showMessage('Creating Max Projection of image sequence, please wait...')
        w = display_projection('max', self.vi.viewer.workEnv.imgdata.seq,
                               self.vi.viewer.ui.label_curr_img_seq_name.text())
        self.projection_windows.append(w)
        self.vi.viewer.status_bar_label.showMessage('Projection displayed.')

    def std_projection(self):
        self.vi.viewer.status_bar_label.showMessage(
            'Creating Standard Deviation Projection of image sequence, please wait...')
        w = display_projection('std', self.vi.viewer.workEnv.imgdata.seq,
                               self.vi.viewer.ui.label_curr_img_seq_name.text())
        self.projection_windows.append(w)
        self.vi.viewer.status_bar_label.showMessage('Projection displayed.')

    def close_projection_windows(self):
        for w in self.projection_windows:
            w.close()
