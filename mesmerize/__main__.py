#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 5 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
print('Loading, please wait... ')
from PyQt5.QtWidgets import QApplication
from mesmerize.common.window_manager import WindowManager
from mesmerize.project_manager import ProjectManager
from mesmerize.common.welcome_window import MainWindow
from mesmerize.scripts import *
from mesmerize import Transmission
from mesmerize.plotting import open_plot_file
import os


class App(QApplication):
    window_manager = WindowManager()
    project_manager = ProjectManager()


def start_welcome_window():
    app = App([])
    app.window_manager.welcome_window = MainWindow()
    app.window_manager.welcome_window.show()

    return app


def start_batch_manager(batch_path: str, item_uuid: str):
    app = App([])
    app.window_manager.welcome_window = MainWindow()
    app.window_manager.welcome_window.show()
    bm = app.window_manager.get_batch_manager(run_batch=[batch_path, item_uuid])
    return (app, bm)


def main():
    if not len(sys.argv) > 1:
        app = start_welcome_window()
        app.exec_()

    elif sys.argv[1] == 'run':
        if sys.argv[2] == 'batch':
            app, bm = start_batch_manager(sys.argv[3], sys.argv[4])
            app.exec_()

    elif sys.argv[1] == 'lighten':
        create_lite_project.main(*sys.argv[2:])

    elif sys.argv[1] == 'show-graph':
        path = sys.argv[2]
        if not os.path.isfile(path):
            raise FileNotFoundError("File does not exist")

        t = Transmission.from_hdf5(path)
        dbs = t.history_trace.data_blocks
        for db in dbs:
            t.history_trace.draw_graph(data_block_id=db, view=True)

    elif sys.argv[1] == 'open-plot':
        path = sys.argv[2]
        proj_path = os.path.dirname(
            os.path.dirname(path)
        )
        app = start_welcome_window()

        app.window_manager.welcome_window.hide()
        app.project_manager.set(project_root_dir=proj_path)
        plot = open_plot_file(path)
        plot.show()

        app.exec_()

    else:
        raise ValueError('Invalid argument')


if __name__ == '__main__':
    main()
