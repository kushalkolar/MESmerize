#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 16 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from common import welcome_window, configuration
# from common.window_manager import WindowManager
import pyqtgraphCore
from viewer import main_window as viewer_main_window
# from viewer.core.viewer_work_environment import ViewerWorkEnv
# from viewer.modules import tiff_io
from analysis.flowchart import Window as FlowchartWindow
# from analysis.stats_gui import StatsWindow
from project_manager.project_browser.project_browser_window import ProjectBrowserWindow
# import json
from uuid import UUID


def window_manager():
    configuration.window_manager.initalize()

def main():
    w = welcome_window.MainWindow()
    configuration.window_manager.welcome_window = w
    w.show()

def background_batch(run_batch: list):
    configuration.window_manager.get_batch_manager(run_batch)

def project_browser():
    project_browser_window = ProjectBrowserWindow()
    configuration.window_manager.project_browsers.append(project_browser_window)
    num_columns = len(project_browser_window.project_browser.tabs['root'].columns)
    project_browser_window.resize(min(1920, num_columns * 240), 600)


def load_child_dataframes_gui():
    configuration.window_manager.project_browsers[0].reload_all_tabs()


def viewer(file: str = None, sample_id: str = None, uuid: UUID = None):
    # Interpret image daifigOptions(imageAxisOrder='row-major')
    pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
    ## Create window with ImageView widget
    viewerWindow = viewer_main_window.MainWindow()
    configuration.window_manager.viewers.append(viewerWindow)

    viewerWindow.resize(1460, 950)
    # TODO: INTEGRATE VIEWER initiation INTO VIEWERWINDOW __init__
    viewer_widget = pyqtgraphCore.ImageView(parent=viewerWindow)
    viewer_widget.setPredefinedGradient('flame')

    viewerWindow.viewer_reference = viewer_widget
    viewerWindow.setCentralWidget(viewer_widget)
    viewerWindow.setWindowTitle('Mesmerize - Viewer - ' + str(len(configuration.window_manager.viewers)))

    configuration.window_manager.viewers[-1].show()

    # if file is not None:
    #     if file.endswith('.tiff') or file.endswith('.tif'):
    #         viewerWindow.run_module(tiff_io.ModuleGUI)
    #         tm = viewerWindow.running_modules[-1]
    #         assert isinstance(tm, tiff_io.ModuleGUI)
    #         tm.ui.labelFileTiff.setText(file)
    #     elif file.endswith('.mes'):
    #         pass
    #     elif file.endswith('.vwe'):
    #         viewer_widget.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=file)
    #     else:
    #         raise ValueError('File extension not supported')
    # elif sample_id is not None:
    #     pass
    # elif uuid is not None:
    #     pass


def flowchart(file=None):
    configuration.window_manager.flowcharts.append(FlowchartWindow())
    configuration.window_manager.flowcharts[-1].show()

    if file is None:
        return

    elif file.endswith('.fc'):
        pass

    elif file.endswith('.fcd.'):
        pass


# def plots(file=None):
#     configuration.window_manager.plots.append(StatsWindow())
#     configuration.window_manager.plots[-1].show()
#
#     if file is None:
#         return
#
#     elif file.endswith('.strn'):
#         pass
#
#     elif file.endswith('.gtrn'):
#         pass
