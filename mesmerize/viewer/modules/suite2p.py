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
from typing import *


class Suite2pData:
    def __init__(self):
        self.path = None
        self.F = None
        self.stat = None
        self.ops = None
        self.iscell = None

    def set_dir(self, path: Union[Path, str]):
        self.path = Path(path)
        for f in ['F', 'stat', 'ops', 'iscell']:
            f_path = self.path.joinpath(f"{f}.npy")

            if not f_path.is_file():
                raise FileNotFoundError(f"The selected directory does not have the '{f}.npy' file.")

            setattr(self, f, np.load(f_path))


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidgetSuite2p()
        self.ui.setupUi(self)

    def clear_ui(self):
        self.ui.label_dir.clear()
        self.ui.label_F.clear()

    def select_dir(self):
        pass

    def import_rois(self):
        pass