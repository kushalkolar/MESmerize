#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...common.qdialogs import *
from ..core.common import ViewerUtils
from .pytemplates.tiff_io_pytemplate import *
from ..core.viewer_work_environment import ViewerWorkEnv
import os
from functools import partial


class ModuleGUI(QtWidgets.QDockWidget):
    load_methods = ['asarray', 'asarray-multi', 'imread']

    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnSelectTiff.clicked.connect(self.select_tiff_file)
        self.ui.btnSelectMetaFile.clicked.connect(self.select_meta_file)
        self.ui.btnLoadIntoWorkEnv.clicked.connect(self.load_tiff_file_slot)

        self.ui.radioButtonAsArray.clicked.connect(partial(self.set_load_method, 'asarray'))
        self.ui.radioButtonAsArrayMulti.clicked.connect(partial(self.set_load_method, 'asarray-multi'))
        self.ui.radioButtonImread.clicked.connect(partial(self.set_load_method, 'imread'))

        self.tiff_file_path = ''
        self.meta_file_path = ''
        self._load_method = None

    @property
    def tiff_file_path(self) -> str:
        return self._tiff_file_path

    @tiff_file_path.setter
    def tiff_file_path(self, path: str):
        self._tiff_file_path = path

    @property
    def meta_file_path(self) -> str:
        return self._meta_file_path

    @meta_file_path.setter
    def meta_file_path(self, path: str):
        self._meta_file_path = path

    def get_load_method(self) -> str:
        if self._load_method is None:
            raise ValueError('Load method not set.')
        else:
            return self._load_method

    def set_load_method(self, method: str):
        if method not in self.load_methods:
            raise ValueError('Must set one of the following methods: imread, asarray, asarray-multi.')
        self._load_method = method

    @use_open_file_dialog('Choose tiff file', '', ['*.tiff', '*.tif'])
    def select_tiff_file(self, path, *args, **kwargs):
        self._tiff_file_path = path
        self.ui.labelFileTiff.setText(self.tiff_file_path)
        self.check_meta_path()

    def check_meta_path(self):
        bn = os.path.basename(self.tiff_file_path)
        dir_path = os.path.dirname(self.tiff_file_path)
        filename = os.path.join(dir_path, os.path.splitext(bn)[0])

        meta_path = f'{filename}.json'

        if os.path.isfile(meta_path):
            self.meta_file_path = meta_path
            self.ui.labelFileMeta.setText(meta_path)
            return True
        else:
            self.meta_file_path = ''
            return False

    @use_open_file_dialog('Choose meta data file', '', ['*.json'])
    def select_meta_file(self, path, *args, **kwargs):
        self.meta_file_path = path
        self.ui.labelFileMeta.setText(self.meta_file_path)

    @present_exceptions('Could not open file(s)', 'The following error occurred while trying to open the image file.')
    def load_tiff_file_slot(self, *args, **kwargs):
        tiff_path = self.tiff_file_path
        if not tiff_path:
            raise ValueError('Nothing to load, you must choose a file to load.')

        method = self.get_load_method()
        meta_path = self.meta_file_path

        self.load_tiff_file(tiff_path, meta_path, method)

    def load_tiff_file(self, tiff_path, meta_path, method):
        """
        Load a tiff file along with associated meta data

        :param tiff_path: path to the tiff file
        :param meta_path: path to the json meta data file
        :param method: one of "asarray", "asarray-multi", or "imread"
                        "asarray" and "asarray-multi" uses :meth:`tifffile.asarray`
                        "asarray-multi" is for multi-page tiffs
                        "imread" uses :meth:`tifffile.imread`
        """

        self.vi.viewer.status_bar_label.showMessage('Please wait, loading tiff file, this may take a few minutes...')

        if not self.vi.discard_workEnv():
            return

        self.vi.viewer.workEnv = ViewerWorkEnv.from_tiff(path=tiff_path,
                                                         method=method,
                                                         meta_path=meta_path)
        self.vi.update_workEnv()
        self.vi.enable_ui(True)
        self.vi.viewer.ui.label_curr_img_seq_name.setText(os.path.basename(tiff_path))
        self.vi.viewer.status_bar_label.showMessage('File loaded into work environment!')
