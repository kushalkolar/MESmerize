import unittest
from .welcome_window import TestViewerLaunch, get_window_manager, App, data_dir
from mesmerize.viewer.modules.tiff_io import ModuleGUI as TiffModuleGUI
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
import os
import tifffile
import json
import numpy


class ImageIOModules(TestViewerLaunch):
    def test_tiff_module(self):
        viewer_window = get_window_manager().viewers[-1]
        for m in viewer_window.running_modules:
            self.assertNotIsInstance(m, TiffModuleGUI, 'Tiff module already running after viewer launcher')
        viewer_window.ui.actionTiff_file.trigger()

        if not any(isinstance(m, TiffModuleGUI) for m in viewer_window.running_modules):
            self.fail('Tiff module not appended to running modules of viewer window')

        tm = viewer_window.run_module('tiff_io')

        self.assertIsInstance(tm, TiffModuleGUI, 'Getting Tiff by str reference failed')
        assert isinstance(tm, TiffModuleGUI)

        QTest.qWaitForWindowExposed(tm)

        # Check tiff module defaults
        self.assertFalse(tm.ui.radioButtonImread.isChecked())
        self.assertFalse(tm.ui.radioButtonAsarray.isChecked())
        tm.ui.radioButtonImread.click()
        self.assertTrue(tm.ui.radioButtonImread.isChecked())

        tiff_file = os.path.join(data_dir, 'tiff', 'test_imread.tiff')
        json_file = os.path.join(data_dir, 'tiff', 'test_imread.json')

        tm._tiff_file_path = tiff_file

        tm.check_meta_path()

        # Check that meta data is deteted
        self.assertEqual(tm._meta_file_path, json_file)

        # Load image
        QTest.mouseClick(tm.ui.btnLoadIntoWorkEnv, Qt.LeftButton)

        # Check the image arrays
        seq = tifffile.imread(tiff_file)

        numpy.testing.assert_array_equal(seq, viewer_window.viewer_reference.workEnv.imgdata.seq.T, 'Output of tifffile.imread does not match ViewerWorkEnv.ImgData.seq.T')
        numpy.testing.assert_array_equal(seq, viewer_window.viewer_reference.image, 'ImageView.image array does not equal output of tifffile.imread')

        # Check the meta data file
        meta = viewer_window.viewer_reference.workEnv.imgdata.meta
        self.assertFalse({} == meta, "ViewerWorkEnv dict appears to be empty")
        print(f"ViewerWorkEnv meta data dict\n{meta}")



if __name__ == '__main__':
    unittest.main()
