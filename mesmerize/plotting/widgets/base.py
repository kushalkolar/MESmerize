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
from ...analysis import Transmission, organize_dataframe_columns
from ...common.qdialogs import *
from ...common import InheritDocs
from typing import *

#TODO: Implement base for all plot widgets


class _AbstractBasePlotWidget(metaclass=InheritDocs):
    @property
    @abc.abstractmethod
    def transmission(self) -> Transmission:
        """
        The input transmission

        :rtype: Transmission
        """
        pass

    @transmission.setter
    @abc.abstractmethod
    def transmission(self, transmission: Transmission):
        """
        Set the input Transmission

        :param transmission: Input transmission
        """

        pass

    @abc.abstractmethod
    def set_input(self, transmission: Transmission):
        """
        Set the input Transmission with data to plot

        :param transmission: Input transmission
        """

        pass

    @abc.abstractmethod
    def update_plot(self, *args, **kwargs):
        """Method that must must be used for updating the plot"""
        pass

    @abc.abstractmethod
    def set_update_live(self, b: bool):
        "Method to set if the plot updates with live input"
        pass

    @abc.abstractmethod
    def get_plot_opts(self) -> dict:
        """Package all necessary plot parameters that in combination with the transmission property are sufficient to restore the plot"""
        pass

    @abc.abstractmethod
    def set_plot_opts(self, opts: dict):
        """Set plot parameters from a dict in the format returned by get_plot_opts()"""
        pass

    @abc.abstractmethod
    def save_plot(self, *args):
        """Package plot data and plot parameters and save to a file.
        Must contain all the information that is necessary to restore the plot"""
        pass

    @abc.abstractmethod
    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        """Open a plot file and restore the plot"""
        pass


class _MetaQtABC(QtWidgets.QWidget.__class__, _AbstractBasePlotWidget.__class__):
    pass


class BasePlotWidget(_AbstractBasePlotWidget, metaclass=_MetaQtABC):
    """
    Base for plot widgets.

    Subclasses must define the class attribute "drop_opts" which is used to store a list of JSON incompatible keys returned by the get_plot_opts() method
    """
    def __init__(self):
        super().__init__()
        self._transmission = None
        self.block_signals_list = []  #: List of QObjects included in dynamic signal blocking. Used for storing plot parameter widgets so that changing all of them quickly (like when restoring a plot) doesn't cause the plot to constantly update.
        self.previous_df_cols = []
        self.update_live = True

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

        cols = set(self.transmission.df.columns)

        if set(self.previous_df_cols) != cols:
            dcols, ccols, ucols = organize_dataframe_columns(self.transmission.df.columns)

            cols = {'data_columns': dcols, 'categorical_columns': ccols, 'uuid_columns': ucols}

            self.fill_control_widget(**cols)

        self.previous_df_cols = cols

    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        """Method for filling the control widget(s) when inputs are set. Must be implemented in subclass"""
        raise NotImplementedError("""Must be implemented in subclass""")

    def update_plot(self, *args, **kwargs):
        """Must be implemented in subclass"""
        raise NotImplementedError('Must be implemented in subclass')

    def set_update_live(self, b: bool):
        """Must be implemented in subclass"""
        raise NotImplementedError('Must be implemented in subclass')

    def get_plot_opts(self, drop: bool) -> dict:
        """
        Must be implemented in subclass
        """
        raise NotImplementedError('Must be implemented in subclass')

    def set_plot_opts(self, opts: dict):
        """Must be implemented in subclass"""
        raise NotImplementedError('Must be implemented in subclass')

    @classmethod
    def signal_blocker(cls, func):
        """Use as a decorator. Block Qt signals from all QObjects instances in the block_signals_list"""
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
        """Plot save dialog"""
        self.save_plot(path)

    @present_exceptions('Plot Save Error', 'The following error occurred while trying to save the plot.')
    def save_plot(self, path):
        """
        Save the plot as a Transmission in an HDF5 file. Plot parameters are stored as a JSON string within the HDF5 file.
        See Transmission.to_hdf5

        :param path: Path to save the file to. For easy identification use ".ptrn" extension.
        """
        # Drop the JSON incompatible data
        plot_state = self.get_plot_opts(drop=True)
        # if self.drop_opts is not None:
        #     for k in self.drop_opts:
        #         plot_state.pop(k)

        plot_state['type'] = self.__class__.__name__
        self.transmission.plot_state = plot_state
        self.transmission.to_hdf5(path)
        print(f"{self.__class__.__name__} plot saved to: {path}")

    @use_open_dir_dialog('Select Project Folder', None)
    @use_open_file_dialog('Choose plot file', None, ['*.ptrn'])
    def open_plot_dialog(self, filepath, dirpath, *args, **kwargs):
        """Open plot dialog"""
        self.open_plot(filepath, dirpath)

    @present_exceptions('Plot open error', 'The following error occurred while trying to open the plot')
    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        """
        Open a plot saved by the save_plot() method

        :param ptrn_path: Path to the HDF5 Transmission file. By convention file extension is ".ptrn"
        :param proj_path: Project path of the associated plot data.
        """
        ptrn = Transmission.from_hdf5(ptrn_path)

        plot_state = ptrn.plot_state
        plot_type = plot_state['type']

        if not plot_type == self.__class__.__name__:
            raise TypeError(f'Wrong plot type\n\n'
                            f'The chosen file is not for this type of plot\n'
                            f'This file is for the following plot type: {plot_type}')

        ptrn.set_proj_path(proj_path)
        ptrn.set_proj_config()

        update_state = self.update_live

        self.set_update_live(False)
        self.set_input(ptrn)
        self.set_plot_opts(plot_state)
        self.set_update_live(update_state)

        self.update_plot()

        return ptrn_path, proj_path
