import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from .welcome_window import TestViewerLaunch, get_window_manager, data_dir
from mesmerize.viewer.modules.batch_manager import ModuleGUI as BatchManagerGUI
import os
from shutil import rmtree


class BaseBatchManager(TestViewerLaunch):
    @classmethod
    def setUpClass(cls):
        cls.batch_path = os.path.join(data_dir, 'test_batch')
        if cls is BaseBatchManager:
            raise unittest.SkipTest("Skipping BaseWelcomeWindowTest")

        super(BaseBatchManager, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.batch_path)


class CreateNewBatch(BaseBatchManager):
    def test_new_batch(self):
        # viewer_window = get_window_manager().viewers[-1]
        # bm = viewer_window.get_batch_manager()
        bm = self.welcome_window.get_batch_manager(testing=True)
        bm.create_new_batch(self.batch_path)
        self.assertIsInstance(bm, BatchManagerGUI)

        self.assertTrue(os.path.isfile(os.path.join(self.batch_path, 'dataframe.batch')))


if __name__ == '__main__':
    unittest.main()
