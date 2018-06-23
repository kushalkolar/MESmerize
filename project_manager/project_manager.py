#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore
from common import configuration, project_config_window, start
import os
import pandas as pd
from viewer.modules.batch_manager import ModuleGUI as BatchModuleGUI
from datetime import datetime
from time import time
from shutil import copyfile


class ProjectManager(QtCore.QObject):
    signal_dataframe_changed = QtCore.pyqtSignal(pd.DataFrame)
    signal_project_config_changed = QtCore.pyqtSignal()

    def __init__(self, project_root_dir):
        QtCore.QObject.__init__(self)
        self.root_dir = project_root_dir
        configuration.proj_path = self.root_dir
        self.dataframe = pd.DataFrame(data=None)
        self.signal_dataframe_changed.connect(self.save_dataframe)
        self.child_dataframes = dict()

    def create_child_dataframes(self):
        for child_name in configuration.proj_cfg.options('CHILD_DFS'):
            filt = configuration.proj_cfg['CHILD_DFS'][child_name]
            df = self.dataframe.copy()
            filt = filt.split('\n')
            for f in filt:
                df = eval(f)
            self.child_dataframes.update({child_name: {'dataframe': df, 'filter_history': filt}})

    def add_child_dataframe(self, child_name: str, filter_history: str, dataframe: pd.DataFrame):
        self.child_dataframes.update({child_name: {'dataframe': dataframe, 'filter_history': filter_history}})
        if child_name in configuration.proj_cfg.options('CHILD_DFS'):
            configuration.proj_cfg['CHILD_DFS'][child_name] = configuration.proj_cfg['CHILD_DFS'][child_name] + '\n'.join(filter_history)
        else:
            configuration.proj_cfg.set('CHILD_DFS', child_name, '\n'.join(filter_history))

        configuration.save_proj_config()

    def remove_child_dataframe(self, name: str):
        self.child_dataframes.pop(name)
        configuration.proj_cfg.remove_option('CHILD_DFS', name)
        configuration.save_proj_config()

    def setup_new_project(self):
        os.makedirs(self.root_dir + '/dataframes')
        os.mkdir(self.root_dir + '/batches')
        os.mkdir(self.root_dir + '/images')
        os.mkdir(self.root_dir + '/curves')
        os.mkdir(self.root_dir + '/plots')
        os.mkdir(self.root_dir + '/clusters')

        configuration.new_proj_config()

        self._initialize_config_window()
        self.config_window.tabs.widget(0).ui.btnSave.clicked.connect(self._create_new_project_dataframe)
        self.config_window.show()

        self._initialize_batch_manager()

    def open_project(self):
        if not os.path.isdir(self.root_dir + '/dataframes'):
            raise NotADirectoryError('dataframes directory not found')

        if not os.path.isdir(self.root_dir + '/images'):
            raise NotADirectoryError('images directory not found')

        if not os.path.isdir(self.root_dir + '/curves'):
            raise NotADirectoryError('curves directory not found')

        self.dataframe = pd.read_pickle(self.root_dir + '/dataframes/root.dfr')

        self._initialize_config_window()

        configuration.open_proj_config()

        self._initialize_batch_manager()

    def attach_open_windows(self, windows):
        pass

    def update_open_windows(self, windows):
        pass

    def _initialize_config_window(self):
        self.config_window = project_config_window.Window()
        self.config_window.tabs.widget(0).ui.btnSave.clicked.connect(self.update_open_windows)
        # self.config_window.resize(560, 620)

    def _initialize_batch_manager(self):
        if not hasattr(configuration.window_manager, 'batch_manager'):
            batch_path = self.root_dir + '/batches' + '/' + \
                         datetime.fromtimestamp(time()).strftime('%Y%m%d_%H%M%S')
            configuration.window_manager.initialize_batch_manager(batch_path)

    def show_config_window(self):
        self.config_window.show()

    def _create_new_project_dataframe(self):
        self.config_window.tabs.widget(0).ui.btnSave.clicked.disconnect(self._create_new_project_dataframe)

        include = configuration.proj_cfg.options('INCLUDE')
        exclude = configuration.proj_cfg.options('EXCLUDE')

        c = include + exclude

        self.dataframe = pd.DataFrame(data=None, columns=c)
        self.save_dataframe()

        start.project_browser()
        configuration.window_manager.welcome_window.ui.btnProjectBrowser.clicked.connect(configuration.window_manager.project_browsers[-1].show)

    def save_dataframe(self):
        self.dataframe.to_pickle(self.root_dir + '/dataframes/root.dfr')

    def update_project_config_requested(self, custom_to_add):
        if self.dataframe.empty:
            return

        columns_changed = False

        for column in configuration.proj_cfg.options('ROI_DEFS'):
            if column not in self.dataframe.columns:
                self.dataframe[column] = 'untagged'
                columns_changed = True

        for column in configuration.proj_cfg.options('STIM_DEFS'):
            if column not in self.dataframe.columns:
                self.dataframe[column] = [['untagged']] * len(self.dataframe)
                columns_changed = True

        for column in configuration.proj_cfg.options('CUSTOM_COLUMNS'):
            if column not in self.dataframe.columns:

                rep_val = custom_to_add[column]['replacement_value']

                if custom_to_add[column]['type'] == 'bool':
                    if rep_val == 'True':
                        rep_val = True
                    elif rep_val == 'False':
                        rep_val = False

                self.dataframe[column] = rep_val
                columns_changed = True

        if columns_changed:
            self.backup_project_dataframe()
            self.emit_signal_dataframe_changed()

        del configuration.window_manager.project_browsers[0]
        self.signal_project_config_changed.emit()
        # configuration.proj_cfg_changed.notify_all()

    def backup_project_dataframe(self):
        copyfile(self.root_dir + '/dataframes/root.dfr', self.root_dir + '/dataframes/root_bak' + str(time()) + '.dfr')

    def append_to_dataframe(self, dicts_to_append: list):
        self.backup_project_dataframe()
        self.dataframe = self.dataframe.append(pd.DataFrame(dicts_to_append), ignore_index=True)
        self.emit_signal_dataframe_changed()

    def emit_signal_dataframe_changed(self):
        self.signal_dataframe_changed.emit(self.dataframe)

    def change_sample_rows(self, sample_id, dicts_to_append):
        self.backup_project_dataframe()
        self.dataframe = self.dataframe[self.dataframe['SampleID'] != sample_id]
        self.dataframe = self.dataframe.append(pd.DataFrame(dicts_to_append), ignore_index=True)
        self.emit_signal_dataframe_changed()