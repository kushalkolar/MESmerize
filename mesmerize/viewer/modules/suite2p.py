#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...common.qdialogs import *
from ...common.configuration import proj_cfg
from ..core.common import ViewerUtils
from ..core.viewer_work_environment import ViewerWorkEnv
from .pytemplates.suite2p_pytemplate import *
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
from .roi_manager_modules.managers import ManagerScatterROI
from tqdm import tqdm
from typing import *


class Suite2pData:
    attrs = ['F', 'Fneu', 'Fneu_sub', 'stat', 'ops', 'iscell']

    def __init__(self):
        self.path = None
        self.F = None
        self.Fneu = None
        self.stat = None
        self.ops = None
        self.iscell = None

        self.use_iscell = True
        self.Fneu_sub = None

    def set_dir(self, path: Union[Path, str]):
        self.clear()
        self.path = Path(path)

        for f in ['F', 'Fneu', 'stat', 'ops', 'iscell']:
            f_path = self.path.joinpath(f"{f}.npy")

            print(f'checking: {f_path}')

            if not f_path.is_file():
                raise FileNotFoundError(f"The selected directory does not have the '{f}.npy' file.")

            setattr(self, f, np.load(f_path, allow_pickle=True))

    def clear(self):
        for attr in self.attrs:
            delattr(self, attr)
            setattr(self, attr, None)


def get_vertices(s: np.ndarray):
    """
    Uses the stat array that contains a collection of all points contained by the ROI
    and uses a k-neighbors tree to only keep the edge points of the ROI
    """
    xs = s['xpix']
    ys = s['ypix']

    points = np.array((xs, ys)).T

    kdt = cKDTree(points)
    vertices = []

    for p in points:
        if len(kdt.query_ball_point(p, 1)) < 5:
            vertices.append(p)

    vs = np.vstack(vertices)

    return vs


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidgetSuite2p()
        self.ui.setupUi(self)

        self.ui.pushButton_dir.clicked.connect(self.select_dir)
        self.ui.pushButton_import.clicked.connect(self.import_rois)

        self.data = Suite2pData()

    @present_exceptions('Invalid dir', '')
    @use_open_dir_dialog('Select dir containing Suite2p output')
    def select_dir(self, path, *args):
        self.ui.label_dir.setText('<not selected>')

        self.vi.viewer.status_bar_label.showMessage('Checking Suite2p output data, please wait...')
        self.data.set_dir(path)
        self.vi.viewer.status_bar_label.showMessage('Finished checking Suite2p output data.')

        self.data.Fneu_sub = (self.ui.spinBox_Fneu_sub.value() / 100)

        self.ui.label_dir.setText(path)

    def import_rois(self):
        if 's2p_iscell' not in proj_cfg.options('ROI_DEFS'):
            QMessageBox.warning(self, 'Missing `s2p_iscell` column',
                                'You have not created an `s2p_iscell` ROI Type column in your project configuration, '
                                'so you will not see the probabilities from the Suite2p classifier.')

            self.has_iscell_column = False
        else:
            self.has_iscell_column = True

        if (len(self.data.stat) > 100) and (not self.ui.checkBox_use_iscell.isChecked()):
            if QMessageBox.warning(self, 'Large Import Warning!',
                                      f'This will import {len(self.data.stat)} ROIs which may take a few minutes.\n'
                                      f'You may want to consider importing only ROIs classified as cells '
                                      f'by the suite2p classifier.\n\n'
                                      f'Continue anyways?', QMessageBox.Yes, QMessageBox.No) == QMessageBox.No:
                return

        if len(self.vi.viewer.workEnv.roi_manager.roi_list) > 0:
            if QMessageBox.warning(self, 'Clear ROI Manager?',
                                             'Importing Suite2p ROIs will clear the ROI Manager, proceed anyway?',
                                             QMessageBox.Yes, QMessageBox.No) \
                    == QMessageBox.No:
                return

        # get the GUI ROI Manager module and set it in manual mode
        self.vi.viewer.parent().get_module('roi_manager').start_backend('ScatterROI')

        # get the backend ROI manager
        roi_manager = self.vi.viewer.workEnv.roi_manager
        assert isinstance(roi_manager, ManagerScatterROI)

        # the data
        F = self.data.F
        Fneu = self.data.Fneu
        stat = self.data.stat
        iscell = self.data.iscell

        # if import only ROIs which Suite2p classified as cells
        if self.ui.checkBox_use_iscell.isChecked():
            mask = self.data.iscell[:, 0] == 1

            F = F[mask]
            Fneu = Fneu[mask]
            stat = stat[mask]
            iscell = iscell[mask]

        # substract neuropil contribution
        Fc = F - (self.data.Fneu_sub * Fneu)

        for ix in tqdm(range(len(stat))):
            self.vi.viewer.status_bar_label.showMessage(f'Importing ROIs from Suite2p output data. {ix} / {len(stat)}')

            pos = get_vertices(stat[ix])
            xs = pos[:, 0]
            ys = pos[:, 1]

            y = Fc[ix]

            roi = roi_manager.add_roi(
                curve=y,
                xs=xs,
                ys=ys,
                metadata=stat[ix]
            )

            # x = np.arange(y.size + 1, dtype=np.float64)[1:]
            #
            # # set curve data
            # roi.curve_data = (x, y)


            # set is_cell data
            if self.has_iscell_column:
                roi.set_tag('s2p_iscell', f"{int(iscell[ix][0])} | {iscell[ix][1]}")

        log = {'Fneu_subtraction': self.data.Fneu_sub,
               'ops': self.data.ops}

        self.vi.viewer.workEnv.history_trace.append({'suite_2p_import': log})

        self.vi.viewer.status_bar_label.showMessage('Finished importing ROIs from Suite2p output data!')
