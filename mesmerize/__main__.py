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


class App(QApplication):
    window_manager = WindowManager()
    project_manager = ProjectManager()


def start_welcome_window():
    app = App([])
    app.window_manager.welcome_window = MainWindow()
    app.window_manager.welcome_window.show()
    app.exec_()


def start_batch_manager(batch_path: str, item_uuid: str):
    app = App([])
    app.window_manager.welcome_window = MainWindow()
    app.window_manager.welcome_window.show()
    bm = app.window_manager.get_batch_manager(run_batch=[batch_path, item_uuid])
    app.exec_()


def main():
    if not len(sys.argv) > 1:
        start_welcome_window()

    elif sys.argv[1] == 'run':
        if sys.argv[2] == 'batch':
            start_batch_manager(sys.argv[3], sys.argv[4])

    elif sys.argv[1] == 'lighten':
        create_lite_project.main(*sys.argv[2:])

    else:
        raise ValueError('Invalid argument')


if __name__ == '__main__':
    main()
