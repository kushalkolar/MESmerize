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
from viewer.core.viewer_work_environment import ViewerWorkEnv
from viewer.modules import tiff_io
from analyser.flowchart import Window as FlowchartWindow
from analyser.stats_gui import StatsWindow
import json


def window_manager():
    configuration.window_manager.initalize()


def main():
    w = welcome_window.MainWindow()
    w.show()


def viewer(file=None):
    # Interpret image data as row-major instead of col-major
    pyqtgraphCore.setConfigOptions(imageAxisOrder='row-major')
    ## Create window with ImageView widget
    viewerWindow = viewer_main_window.MainWindow()  # QtWidgets.QMainWindow()
    viewerWindow.resize(1460, 950)
    # TODO: INTEGRATE VIEWER initiation INTO VIEWERWINDOW __init__
    viewer = pyqtgraphCore.ImageView(parent=viewerWindow)
    viewer.setPredefinedGradient('flame')

    if configuration.proj_path is not None:
        viewer.batch_manager = configuration.window_manager.batch_manager

    viewerWindow.viewer_reference = viewer
    viewerWindow.setCentralWidget(viewer)
    viewerWindow.setWindowTitle('Mesmerize - Viewer - ' + str(len(configuration.window_manager.viewers)))

    configuration.window_manager.viewers.append(viewerWindow)
    configuration.window_manager.viewers[-1].show()

    if file is None:
        return
    elif file.endswith('.tiff') or file.endswith('.tif'):
        viewerWindow.run_module(tiff_io.ModuleGUI)
        tm = viewerWindow.running_modules[-1]
        assert isinstance(tm, tiff_io.ModuleGUI)
        tm.ui.labelFileTiff.setText(file)

    elif file.endswith('.mes'):
        pass
    elif file.endswith('.vwe'):
        viewer.workEnv = ViewerWorkEnv.from_pickle(pikPath=file)
    else:
        raise ValueError('File extension not supported')


def flowchart(file=None):
    configuration.window_manager.flowcharts.append(FlowchartWindow())
    configuration.window_manager.flowcharts[-1].show()

    if file is None:
        return

    elif file.endswith('.fc'):
        pass

    elif file.endswith('.fcd.'):
        pass


def plots(file=None):
    configuration.window_manager.plots.append(StatsWindow())
    configuration.window_manager.plots[-1].show()

    if file is None:
        return

    elif file.endswith('.strn'):
        pass

    elif file.endswith('.gtrn'):
        pass
