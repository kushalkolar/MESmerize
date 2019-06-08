import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from mesmerize.__main__ import App
from mesmerize.common import get_window_manager, get_project_manager
from mesmerize.viewer import ViewerWindow
from mesmerize.common.welcome_window import MainWindow
from mesmerize.analysis.flowchart import Window as FlowchartWindow
import os

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

app = App([])

class BaseWelcomeWindowTest(unittest.TestCase):
    # @classmethod
    # def setup(cls):
    #     cls.welcome_window = MainWindow()
    #     QTest.qWaitForWindowExposed(cls.welcome_window)

    @classmethod
    def setUpClass(cls):
        if cls is BaseWelcomeWindowTest:
            raise unittest.SkipTest("Skipping BaseWelcomeWindowTest")

        cls.welcome_window = MainWindow()
        get_window_manager().welcome_window = cls.welcome_window
        QTest.qWaitForWindowExposed(cls.welcome_window)
        super(BaseWelcomeWindowTest, cls).setUpClass()

    # def test_launch_welcome_window(self):
    #     self.welcome_window.show()


class TestViewerLaunch(BaseWelcomeWindowTest):
    def test_launch_viewer(self):
        num_viewers = len(get_window_manager().viewers)
        # QtTest.QTest.qWaitForWindowExposed(self.welcome_window)
        QTest.mouseClick(self.welcome_window.ui.btnViewer, Qt.LeftButton)
        self.assertEqual(len(get_window_manager().viewers) - 1, num_viewers,
                         'No window has been appended to WindowManager.viewers instance')
        self.assertIsInstance(get_window_manager().viewers[-1], ViewerWindow)
        QTest.qWaitForWindowExposed(get_window_manager().viewers[-1])


class TestFlowchartLauncher(BaseWelcomeWindowTest):
    def test_launch_flowchart(self):
        num_flowcharts = len(get_window_manager().flowcharts)
        QTest.mouseClick(self.welcome_window.ui.btnFlowchart, Qt.LeftButton)
        self.assertEqual(len(get_window_manager().flowcharts) - 1, num_flowcharts,
                         'Flowchart window not appended to WindowMnager.flowchart instance')
        self.assertIsInstance(get_window_manager().flowcharts[-1], FlowchartWindow)
        QTest.qWaitForWindowExposed(get_window_manager().flowcharts[-1])

    # def _start_window_manager(self):
    #     self.get_window_manager =


if __name__ == '__main__':
    unittest.main()
