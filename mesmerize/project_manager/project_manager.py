#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

A back-end module for managing most project related functions, such as the root dataframe and all children,
adding rows to the root dataframe, updating child dataframes, and updating the project configuration.
"""

from PyQt5 import QtCore
from ..common import configuration, project_config_window, start, get_window_manager, is_mesmerize_project
# from ..common import get_window_manager
import os
import pandas as pd
from time import time
from shutil import move as move_file
from warnings import warn


class ProjectManager(QtCore.QObject):
    signal_dataframe_changed = QtCore.pyqtSignal(pd.DataFrame)
    signal_project_config_changed = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.root_dir = None
        self.dataframe = pd.DataFrame(data=None)
        self.child_dataframes = None

    def set(self, project_root_dir: str):
        self.root_dir = project_root_dir
        configuration.proj_path = self.root_dir
        self.dataframe = pd.DataFrame(data=None)
        self.signal_dataframe_changed.connect(self.save_dataframe)
        self.child_dataframes = dict()

    def create_sub_dataframe(self):
        for child_name in configuration.proj_cfg.options('CHILD_DFS'):
            filt = configuration.proj_cfg['CHILD_DFS'][child_name]
            df = self.dataframe.copy()
            filt = filt.split('\n')
            for f in filt:
                df = eval(f)
            self.child_dataframes.update({child_name: {'dataframe': df, 'filter_history': filt}})

    def add_sub_dataframe(self, child_name: str, filter_history: str, dataframe: pd.DataFrame):
        self.child_dataframes.update({child_name: {'dataframe': dataframe, 'filter_history': filter_history}})
        if child_name in configuration.proj_cfg.options('CHILD_DFS'):
            configuration.proj_cfg['CHILD_DFS'][child_name] = configuration.proj_cfg['CHILD_DFS'][child_name] + '\n'.join(filter_history)
        else:
            configuration.proj_cfg.set('CHILD_DFS', child_name, '\n'.join(filter_history))

        configuration.save_proj_config()

    def remove_sub_dataframe(self, name: str):
        self.child_dataframes.pop(name)
        configuration.proj_cfg.remove_option('CHILD_DFS', name)
        configuration.save_proj_config()

    def setup_new_project(self):
        subdirs = ['dataframes',
                   'batches',
                   'images',
                   'flowcharts',
                   'trns',
                   'plots']

        for d in subdirs:
            os.makedirs(os.path.join(self.root_dir, d))

        configuration.create_new_proj_config()

        self._initialize_config_window()
        self.config_window.tabs.widget(0).ui.btnSave.clicked.connect(self._create_new_project_dataframe)
        self.config_window.show()

    def open_project(self):
        is_mesmerize_project(self.root_dir)

        df_path = os.path.join(self.root_dir, 'dataframes', 'root.dfr')
        self.dataframe = pd.read_hdf(df_path, key='project_dataframe', mode='r')

        self._initialize_config_window()

        configuration.open_proj_config()

    def attach_open_windows(self, windows):
        pass

    def update_open_windows(self, windows):
        pass

    def _initialize_config_window(self):
        self.config_window = project_config_window.Window()
        self.config_window.tabs.widget(0).ui.btnSave.clicked.connect(self.update_open_windows)
        # self.config_window.resize(560, 620)

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

    def get_dataframe(self) -> pd.DataFrame:
        return self.dataframe

    def set_dataframe(self, dataframe: pd.DataFrame):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError('Must pass an instance of pandas.DataFrame')
        self.dataframe = dataframe.copy(deep=True)
        self.emit_signal_dataframe_changed()

    def save_dataframe(self):
        df_path = os.path.join(self.root_dir, 'dataframes', 'root.dfr')
        if os.path.isfile(df_path):
            warn('root.dfr already exists, renaming file...')
            self.backup_project_dataframe()

        self.dataframe.to_hdf(df_path, key='project_dataframe', mode='w')

    def update_project_config_requested(self, custom_to_add: dict):
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

        all_columns = configuration.proj_cfg.options('INCLUDE') + configuration.proj_cfg.options('EXCLUDE')
        columns_to_drop = list(set(self.dataframe.columns).difference(all_columns))
        if len(columns_to_drop) > 0:
            columns_changed = True

        if columns_changed:
            self.backup_project_dataframe()
            self.dataframe.drop(columns=columns_to_drop, inplace=True)
            self.save_dataframe()

            self.signal_dataframe_changed.disconnect(get_window_manager().project_browser.project_browser.update_dataframe_data)
            get_window_manager().project_browser.deleteLater()

            self.signal_project_config_changed.emit()
            self.emit_signal_dataframe_changed()

            pb = start.project_browser()
            pb.reload_all_tabs()
            get_window_manager().project_browser = pb

        # configuration.proj_cfg_changed.notify_all()

    def delete_gui_children(self, widget: QtCore.QObject):
        widget.children()

    def backup_project_dataframe(self):
        move_file(os.path.join(self.root_dir, 'dataframes', 'root.dfr'), os.path.join(self.root_dir, 'dataframes', f'root_bak_{time()}.dfr'))

    def append_to_dataframe(self, dicts_to_append: list):
        self.backup_project_dataframe()
        self.dataframe = self.dataframe.append(pd.DataFrame(dicts_to_append), ignore_index=True)
        self.emit_signal_dataframe_changed()

    def emit_signal_dataframe_changed(self):
        self.signal_dataframe_changed.emit(self.dataframe)

    def change_sample_rows(self, sample_id: str, dicts_to_append: list):
        """
        Remove the rows corresponding to the passed sample_id and replace them with the list of dicts provided
        """
        # self.backup_project_dataframe()
        # self.dataframe = self.dataframe[self.dataframe['SampleID'] != sample_id]
        self.delete_sample_id_rows(sample_id)
        self.dataframe = self.dataframe.append(pd.DataFrame(dicts_to_append), ignore_index=True)
        self.emit_signal_dataframe_changed()

    def delete_sample_id_rows(self, sample_id: str):
        self.backup_project_dataframe()
        self.dataframe = self.dataframe[self.dataframe['SampleID'] != sample_id]
        self.emit_signal_dataframe_changed()

    def get_sample_id_rows(self, sample_id: str) -> pd.DataFrame:
        return self.dataframe[self.dataframe['SampleID'] == sample_id]
