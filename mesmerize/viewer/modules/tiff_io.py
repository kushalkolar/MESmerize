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
from ..core import organize_metadata
from inspect import getmembers, isfunction
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

        self._tiff_file_path = None
        self._meta_file_path = None
        self._load_method = None

        # all available meta data loaders
        meta_funcs = [f for f in getmembers(organize_metadata) if isfunction(f[1])]

        self.meta_loaders = dict(
            zip(
                [f[0] for f in meta_funcs],         # function name
                [f[1].__doc__ for f in meta_funcs]  # function extension from docstring
            )
        )
        self.ui.listWidget_meta_data_loader.addItems(self.meta_loaders.keys())
        self.ui.listWidget_meta_data_loader.currentItemChanged.connect(self.check_meta_path)

        self.meta_loader = None

    @property
    def tiff_file_path(self) -> str:
        return self._tiff_file_path

    @tiff_file_path.setter
    def tiff_file_path(self, path: str):
        self._tiff_file_path = path
        self.ui.labelFileTiff.setText(self.tiff_file_path)

    @property
    def meta_file_path(self) -> str:
        return self._meta_file_path

    @meta_file_path.setter
    def meta_file_path(self, path: str):
        self._meta_file_path = path
        self.ui.labelFileMeta.setText(self.meta_file_path)

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
        self.tiff_file_path = path
        self.check_meta_path()

    def check_meta_path(self) -> bool:
        """
        check if a file exists with the same name
        and the meta data extension specified by the
        selected meta data format
        """
        bn = os.path.basename(self.tiff_file_path)
        dir_path = os.path.dirname(self.tiff_file_path)
        filename = os.path.join(dir_path, os.path.splitext(bn)[0])

        if self.ui.listWidget_meta_data_loader.currentItem() is None:
            return False

        meta_loader = self.ui.listWidget_meta_data_loader.currentItem().text()

        meta_ext = self.meta_loaders[meta_loader]

        self.meta_loader = meta_loader

        meta_path = f'{filename}{meta_ext}'

        if os.path.isfile(meta_path):
            self.meta_file_path = meta_path
            self.ui.labelFileMeta.setText(meta_path)
            return True
        else:
            self.meta_file_path = ''
            return False

    @use_open_file_dialog('Choose meta data file', '')
    def select_meta_file(self, path, *args, **kwargs):
        if self.meta_loader is not None:
            ext = self.meta_loaders[self.meta_loader]
            if not path.endswith(ext):
                QtWidgets.QMessageBox.information(
                    self.parent(),
                    f'File extension mismatch',
                    f'The file extension of the chosen meta data file does not match '
                    f'the expected file extension <{ext}> for the format <{self.meta_loader}>\n\n'
                    f'You can still try to load the meta data from this file.',
                    QtWidgets.QMessageBox.Ok
                )

        self.meta_file_path = path

    @present_exceptions('Could not open file(s)', 'The following error occurred while trying to open the image file.')
    def load_tiff_file_slot(self, *args, **kwargs):
        tiff_path = self.tiff_file_path
        if not tiff_path:
            raise ValueError('Nothing to load, you must choose a file to load.')

        method = self.get_load_method()

        if self.ui.radioButton_axes_custom.isChecked():
            axes_order = self.ui.lineEdit_axes_custom.text()
        else:
            axes_order = None

        if self.ui.groupBox_meta_loader.isChecked():
            if self.meta_file_path is None:
                raise AttributeError(
                    "You have not chosen a meta data file.\n"
                    "Uncheck 'Load meta data' if you do not wish to load "
                    "meta data through this module"
                )

            if self.meta_loader is None:
                raise AttributeError(
                    "You have not selected a meta data format"
                )

            meta_path = self.meta_file_path
            meta_format = self.meta_loader
        else:
            meta_path = None
            meta_format = None

        self.load(tiff_path, method, axes_order, meta_path, meta_format=meta_format)

    def load(
            self,
            tiff_path: str,
            method: str,
            axes_order: Optional[str] = None,
            meta_path: Optional[str] = None,
            meta_format: Optional[str] = None
    ) -> ViewerWorkEnv:
        """
        Load a tiff file along with associated meta data

        :param tiff_path:       path to the tiff file
        :param meta_path:       path to the json meta data file

        :param method:          one of "asarray", "asarray-multi", or "imread"
                                    "asarray" and "asarray-multi" uses :meth:`tifffile.asarray`
                                    "asarray-multi" is for multi-page tiffs
                                    "imread" uses :meth:`tifffile.imread`

        :param axes_order:      axes order, examples: txy, xyt, tzxy, xytz etc.
        :param meta_format:     name of function from viewer.core.organize_meta that should be used
                                to organize the meta data.
        """

        self.vi.viewer.status_bar_label.showMessage('Please wait, loading tiff file, this may take a few minutes...')

        if not self.vi.discard_workEnv():
            return

        self.vi.viewer.workEnv = ViewerWorkEnv.from_tiff(
            path=tiff_path,
            method=method,
            meta_path=meta_path,
            axes_order=axes_order,
            meta_format=meta_format
        )
        self.vi.update_workEnv()
        self.vi.enable_ui(True)
        self.vi.viewer.ui.label_curr_img_seq_name.setText(os.path.basename(tiff_path))
        self.vi.viewer.status_bar_label.showMessage('File loaded into work environment!')

        return self.vi.viewer.workEnv
