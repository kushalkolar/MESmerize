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
from mesmerize import configuration
from PyQt5.QtWidgets import QApplication
from mesmerize.common.window_manager import WindowManager
from mesmerize.project_manager import ProjectManager
from mesmerize.common.welcome_window import MainWindow
from mesmerize.scripts import *
from mesmerize import Transmission
from mesmerize.plotting import open_plot_file
import os
import logging
from datetime import datetime
from glob import glob
import click
import traceback
from zipfile import ZipFile, ZIP_LZMA


session_id = datetime.now().strftime("%Y-%m-%d_%H.%M.%S-%f")


class App(QApplication):
    window_manager = WindowManager()
    project_manager = ProjectManager()
    session_id = session_id


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


def move_old_logfiles(logger, log_file_dir):
    zlogfile = ZipFile(
        os.path.join(log_file_dir, 'logs.zip'),
        mode='a',
        compression=ZIP_LZMA,
        allowZip64=True,

    )

    logfiles = glob(os.path.join(log_file_dir, '*.log'))
    logfiles.sort()
    while len(logfiles) > 5:
        logger.info("Moving old logfiles...")
        old_logfile = logfiles.pop(0)
        zlogfile.write(old_logfile, os.path.basename(old_logfile))
        os.remove(old_logfile)
    zlogfile.close()


@click.command()
@click.option('--log-level', type=str, default='INFO')
@click.option('--log-file', type=click.Path(exists=False, writable=True))
@click.option('--log-file-dir', type=click.Path(writable=True))
@click.option('--log-format', type=str)
@click.option('--run-batch', nargs=2, type=str)
@click.option('--open-plot', type=click.Path(exists=True, readable=True))
def main(
        log_level,
        log_file,
        log_file_dir,
        log_format,
        run_batch,
        open_plot
):
    if log_file_dir is None:
        log_file_dir = configuration.sys_cfg_dir

    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir, exist_ok=True)

    if log_file is None:
        log_file = os.path.join(log_file_dir, f"{session_id}.log")

    if log_format is None:
        log_format = "%(asctime)s %(levelname)s %(pathname)s %(lineno)s \n %(message)s "

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        filename=log_file,
        filemode='w'
    )

    def exception_hook(exc_type, exc_value, traceback):
        logging.error('EXCEPTION ENCOUNTERED', exc_info=(exc_type, exc_value, traceback))

    sys.excepthook = exception_hook

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(log_format)

    root_logger = logging.getLogger()

    root_logger.addHandler(console)
    root_logger.addHandler(
        logging.StreamHandler(sys.stdout)
    )
    root_logger.addHandler(
        logging.StreamHandler(sys.stderr)
    )

    move_old_logfiles(root_logger, log_file_dir)

    if not len(sys.argv) > 1:
        app = start_welcome_window()
        app.exec_()

    if run_batch:
        batch_path = run_batch[0]
        item = run_batch[1]
        app, bm = start_batch_manager(batch_path, item)
        app.exec_()

    elif open_plot:
        proj_path = os.path.dirname(
            os.path.dirname(open_plot)
        )
        app = start_welcome_window()

        app.window_manager.welcome_window.hide()
        app.project_manager.set(project_root_dir=proj_path)
        plot = open_plot_file(open_plot)
        plot.show()
        app.exec_()

    else:
        app = start_welcome_window()
        app.exec_()
    #
    # elif sys.argv[1] == 'lighten':
    #     create_lite_project.main(*sys.argv[2:])
    #
    # elif sys.argv[1] == 'show-graph':
    #     path = sys.argv[2]
    #     if not os.path.isfile(path):
    #         raise FileNotFoundError("File does not exist")
    #
    #     t = Transmission.from_hdf5(path)
    #     dbs = t.history_trace.data_blocks
    #     for db in dbs:
    #         t.history_trace.draw_graph(data_block_id=db, view=True)
    #


if __name__ == '__main__':
    main()
