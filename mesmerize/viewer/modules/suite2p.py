#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...common.qdialogs import *
from ..core.common import ViewerUtils
from ..core.viewer_work_environment import ViewerWorkEnv
from .pytemplates.suite2p_pytemplate import *
import numpy as np
from pathlib import Path
from scipy.spatial import ConvexHull
from .roi_manager_modules.roi_types import Suite2pROI
from tqdm import tqdm
from typing import *


class Suite2pData:
    attrs = ['F', 'Fneu', 'Fneu_sub' 'stat', 'ops', 'iscell']

    def __init__(self):
        self.path = None
        self.F = None
        self.Fneu = None
        self.Fneu_sub = None
        self.stat = None
        self.ops = None
        self.iscell = None
        self.use_iscell = True

    def set_dir(self, path: Union[Path, str]):
        self.clear()
        self.path = Path(path)

        for f in ['F', 'Fneu', 'stat', 'ops', 'iscell']:
            f_path = self.path.joinpath(f"{f}.npy")

            if not f_path.isw_file():
                raise FileNotFoundError(f"The selected directory does not have the '{f}.npy' file.")

            setattr(self, f, np.load(f_path))

    def clear(self):
        for attr in self.attrs:
            delattr(self, attr)
            setattr(self, attr, None)


def get_vertices(stat: np.ndarray):
    """Uses the stat array from stat.npy to get the ROI vertices"""
    vertices = []

    for s in tqdm(stat):
        xs = s['xpix']
        ys = s['ypix']

        a = np.array((xs, ys)).T

        hull = ConvexHull(a, qhull_options='Qs')

        vs = a[hull.vertices]

        vertices.append(vs)

    return vertices


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidgetSuite2p()
        self.ui.setupUi(self)

        self.data = Suite2pData()

        self.ui.spinBox_Fneu_sub.valueChanged.connect(
            lambda val: setattr(self.data, 'Fneu_sub', val)
        )

    @present_exceptions('Invalid dir', '')
    @use_open_dir_dialog('Select dir containing Suite2p output')
    def select_dir(self, path, *args):
        self.ui.label_dir.setText('<not selected>')

        self.data.set_dir(path)
        self.data.use_iscell = self.ui.checkBox_use_iscell.isChecked()

        self.ui.label_dir.setText(path)

    def import_rois(self):
        if len(self.vi.viewer.workEnv.roi_manager.roi_list) > 0:
            if QtWidgets.QMessageBox.warning(self, 'Clear ROI Manager?',
                                             'Importing Suite2p ROIs will clear the ROI Manager proceed anyway?',
                                             QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) \
                    == QtWidgets.QMessageBox.No:
                return

        self.vi.viewer.parent().run_module('roi_manager').start_manual_mode()






