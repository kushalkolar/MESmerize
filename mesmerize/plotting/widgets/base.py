#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
import abc
from ...analysis import Transmission
from ...common.qdialogs import *
from typing import *

#TODO: Implement base for all plot widgets


class _AbstractBasePlotWidget(metaclass=abc.ABCMeta):
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


class _MetaQtABC(QtWidgets.QWidget.__class__, _AbstractBasePlotWidget.__class__):
    pass


class BasePlotWidget(_AbstractBasePlotWidget, metaclass=_MetaQtABC):
    def __init__(self):
        super().__init__()
        self._transmission = None

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'drop_opts'):
            raise AttributeError('Must define class attribute "drop_opts"')

    @property
    def transmission(self) -> Transmission:
        if self._transmission is None:
            raise AttributeError("No input transmission has been set")
        return self._transmission

    @transmission.setter
    def transmission(self, transmission: Transmission):
        if not isinstance(transmission, Transmission):
            raise TypeError('Input must be an instance of Transmission')
        self._transmission = transmission

    def set_input(self, transmission: Transmission):
        self.transmission = transmission

    def update_plot(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclass')

    def get_plot_opts(self, drop: bool) -> dict:
        """
        Drop keys that are incompatible with JSON
        """
        raise NotImplementedError('Must be implemented in subclass')

    def set_plot_opts(self, opts: dict):
        raise NotImplementedError('Must be implemented in subclass')

    @classmethod
    def signal_blocker(cls, func):
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

    @use_save_file_dialog('Save plot as', None, '.ptrn')
    def save_plot_dialog(self, path, *args):
        self.save_plot(path)

    @present_exceptions('Plot Save Error', 'The following error occurred while trying to save the plot.')
    def save_plot(self, path):
        plot_state = self.get_plot_opts(drop=True)
        # if self.drop_opts is not None:
        #     for k in self.drop_opts:
        #         plot_state.pop(k)

        plot_state['type'] = self.__class__.__name__
        self.transmission.plot_state = plot_state
        self.transmission.to_hdf5(path)

    @use_open_dir_dialog('Select Project Folder', None)
    @use_open_file_dialog('Choose plot file', None, ['*.ptrn'])
    def open_plot_dialog(self, filepath, dirpath, *args, **kwargs):
        self.open_plot(filepath, dirpath)

    @present_exceptions('Plot open error', 'The following error occurred while trying to open the plot')
    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        ptrn = Transmission.from_hdf5(ptrn_path)

        plot_state = ptrn.plot_state
        plot_type = plot_state['type']

        if not plot_type == self.__class__.__name__:
            raise TypeError(f'Wrong plot type\n\n'
                            f'The chosen file is not for this type of plot\n'
                            f'This file is for the following plot type: {plot_type}')

        ptrn.set_proj_path(proj_path)
        ptrn.set_proj_config()

        self.set_input(ptrn)
        self.set_plot_opts(plot_state)
        self.update_plot()

        return ptrn_path, proj_path
