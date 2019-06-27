#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets, QtCore
import abc
from ...analysis import Transmission
import traceback
import os
from typing import *

#TODO: Implement base for all plot widgets


class AbstractBasePlotWidget(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def transmission(self) -> Transmission:
        pass

    @transmission.setter
    @abc.abstractmethod
    def transmission(self, transmission: Transmission):
        pass

    @abc.abstractmethod
    def set_input(self, transmission: Transmission):
        pass

    @abc.abstractmethod
    def update_plot(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_plot_opts(self) -> dict:
        pass

    @abc.abstractmethod
    def set_plot_opts(self, opts: dict):
        pass

    @abc.abstractmethod
    def save_plot(self, *args):
        pass

    @abc.abstractmethod
    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        pass


class _MetaQtABC(QtWidgets.QWidget.__class__, AbstractBasePlotWidget.__class__):
    pass


class BasePlotWidget(AbstractBasePlotWidget, QtWidgets.QWidget, metaclass=_MetaQtABC):
    def __init__(self):
        super(BasePlotWidget, self).__init__()
        QtWidgets.QWidget.__init__(self)
        self.transmission = None
        self.block_siganls_list = []

    @property
    def transmission(self) -> Transmission:
        return self._transmission

    @transmission.setter
    def transmission(self, transmission: Transmission):
        self._transmission = transmission

    def set_input(self, transmission: Transmission):
        self.transmission = transmission

    def update_plot(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclass')

    def get_plot_opts(self) -> dict:
        raise NotImplementedError('Must be implemented in subclass')

    def set_plot_opts(self, opts: dict):
        raise NotImplementedError('Must be implemented in subclass')

    def save_plot(self, drop_opts: List[str] = None):
        """
        :param drop_opts: List of keys to drop from dict returned by get_plot_opts()
        """
        if self.transmission is None:
            QtWidgets.QMessageBox.warning(self, 'Nothing to save', 'No input transmission, nothing to save')
            return

        try:
            proj_path = self.transmission.get_proj_path()
            plots_path = os.path.join(proj_path, 'plots')
        except ValueError:
            plots_path = ''

        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save plot as', plots_path, '(*.ptrn)')
        if path == '':
            return
        path = path[0]

        if not path.endswith('.ptrn'):
            path = f'{path}.ptrn'

        plot_state = self.get_plot_opts()
        if drop_opts is not None:
            for k in drop_opts:
                plot_state.pop(k)
        # plot_state.pop('dataframes')
        # plot_state.pop('transmission')

        plot_state['type'] = self.__class__.__name__
        self.transmission.plot_state = plot_state
        self.transmission.to_hdf5(path)

    @classmethod
    def block_signals(cls, func):
        def fn(self, *args, **kwds):
            restore_dict = dict.fromkeys(self.block_signals_list)

            for w in self.block_signals_list:
                restore_dict[w] = w.signalsBlocked()
                w.blockSignals(True)

            try:
                ret = func(self, *args, **kwds)
            finally:
                for w in self.block_signals_list:
                    w.blockSignals(restore_dict[w])

            return ret

        return fn

    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        try:
            ptrn = Transmission.from_hdf5(ptrn_path)
        except:
            QtWidgets.QMessageBox.warning(self, 'File open error',
                                          f'Could not open the chosen file\n{traceback.format_exc()}')
            return

        plot_state = ptrn.plot_state
        plot_type = plot_state['type']

        if not plot_type == self.__class__.__name__:
            QtWidgets.QMessageBox.warning(self, 'Wrong plot type', f'The chosen file is not for this type of '
            f'plot\nThis file is for the following plot type: {plot_type}')
            return

        try:
            ptrn.set_proj_path(proj_path)
            ptrn.set_proj_config()

        except (FileNotFoundError, NotADirectoryError) as e:
            QtWidgets.QMessageBox.warning(self, 'Invalid Project Folder', 'This is not a valid Mesmerize project\n' + e)
            return

        self.set_input(ptrn)
        self.set_plot_opts(plot_state)

        return ptrn_path, proj_path

    def open_plot_dialog(self):
        ptrn_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose plot file', '', '(*.ptrn)')
        if ptrn_path == '':
            return

        proj_path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Project Folder')

        if proj_path == '':
            return

        self.open_plot(ptrn_path[0], proj_path)
