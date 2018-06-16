#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from common import configuration, project_config_window
import os
import pandas as pd
from viewer.modules.batch_manager import ModuleGUI as BatchModuleGUI


class ProjectManager:
    def __init__(self, project_root_dir):
        self.root_dir = project_root_dir
        configuration.proj_path = self.root_dir

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
        self.config_window.resize(560, 620)

    def _initialize_batch_manager(self):
        self.batch_manager = BatchModuleGUI()
        self.batch_manager.hide()

    def show_config_window(self):
        self.config_window.show()

    def _create_new_project_dataframe(self):
        self.config_window.tabs.widget(0).ui.btnSave.clicked.disconnect(self._create_new_project_dataframe)

        include = configuration.proj_cfg.options('INCLUDE')
        exclude = configuration.proj_cfg.options('EXCLUDE')

        c = include + exclude

        self.dataframe = pd.DataFrame(data=None, columns=c)
