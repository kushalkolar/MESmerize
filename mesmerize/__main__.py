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
print('Loading, please wait... ')
from PyQt5.QtWidgets import QApplication
from mesmerize.common.window_manager import WindowManager
from mesmerize.project_manager import ProjectManager
from mesmerize.common.welcome_window import MainWindow


class App(QApplication):
    window_manager = WindowManager()
    project_manager = ProjectManager()


def main():
    app = App([])

    if not len(sys.argv) > 1:
        app.window_manager.welcome_window = MainWindow()
        app.window_manager.welcome_window.show()

    elif sys.argv[1] == 'run':
        if sys.argv[2] == 'batch':
            app.window_manager.welcome_window = MainWindow()
            app.window_manager.welcome_window.show()
            bm = app.window_manager.get_batch_manager(run_batch=[sys.argv[3], sys.argv[4]])
            # bm.run()

    # elif sys.argv[1].endswith('.tiff') or sys.argv[1].endswith('.tif'):
    #     start.viewer(sys.argv[1])
    #
    # elif sys.argv[1].endswith('.fc') or sys.argv[1].endswith('.fcd'):
    #     start.flowchart(sys.argv[1])

    else:
        raise ValueError('Invalid argument')

    app.exec_()


if __name__ == '__main__':
    main()
