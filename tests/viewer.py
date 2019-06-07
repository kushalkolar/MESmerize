import unittest
from .welcome_window import TestViewerLaunch, get_window_manager
from mesmerize.viewer.modules.tiff_io import ModuleGUI as TiffModuleGUI
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import os

class ImageIOModules(TestViewerLaunch):
    def test_tiff_module(self):
        viewer_window = get_window_manager().viewer[-1]
        for m in viewer_window.running_modules:
            self.assertNotIsInstance(m, TiffModuleGUI, 'Tiff module already running after viewer launcher')
        viewer_window.actionTiff_file.trigger()

        if not any(isinstance(m, TiffModuleGUI) for m in viewer_window.running_modules):
            self.fail('Tiff module not appended to running modules of viewer window')

        tm = viewer_window.get_module('tiff_io')

        self.assertIsInstance(tm, TiffModuleGUI, 'Getting Tiff by str reference failed')

        # Check tiff module defaults
        self.assertFalse(tm.ui.radioButtonImread.isChecked())
        self.assertFalse(tm.ui.radioButtonAsarray.isChecked())
        QTest.mouseClick(tm.ui.radioButtonImread, Qt.LeftButton)

        data_dir = os.path.join(os.path.abspath(__file__), 'data')

        