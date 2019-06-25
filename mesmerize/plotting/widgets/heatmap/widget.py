#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from ...variants import Heatmap
from .. import DatapointTracerWidget
from ....analysis.data_types import HistoryTrace, Transmission
from .control_widget import Ui_ControlWidget
import numpy as np
import pandas as pd
from typing import Optional, Union
import traceback
import os


class HeatmapWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = Heatmap()

        self.vlayout.addWidget(self.plot_widget)
        self.setLayout(self.vlayout)
        self.dataframe = pd.DataFrame()

    def set_data(self, array: np.ndarray = None, dataframe: pd.DataFrame = None, data_column: str = None,
                 cmap: str = 'jet'):

        if array is not None:
            assert isinstance(array, np.ndarray)
            data = array

        elif dataframe is not None:
            assert isinstance(dataframe, pd.DataFrame)
            assert isinstance(data_column, str)
            self.dataframe = dataframe
            data = np.vstack(self.dataframe[data_column].values)

        else:
            raise TypeError('You must pass either a numpy array or dataframe as and argument')

        self.plot_widget.set(data, cmap=cmap)


class HeatmapSplitterWidget(QtWidgets.QWidget):
    def __init__(self, highlight_mode='row'):
        QtWidgets.QWidget.__init__(self)
        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.plot_widget = Heatmap(highlight_mode=highlight_mode)

        self.labelSort = QtWidgets.QLabel(self)
        self.labelSort.setText('Sort heatmap according to column:')
        self.labelSort.setMinimumHeight(30)
        self.labelSort.setMaximumHeight(30)
        self.comboBoxSortColumn = QtWidgets.QComboBox(self)
        self.comboBoxSortColumn.currentTextChanged.connect(self._set_sort_order)

        self.plot_widget.layout().addWidget(self.labelSort)
        self.plot_widget.layout().addWidget(self.comboBoxSortColumn)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.plot_widget)

        self.vlayout.addWidget(self.splitter)
        # self.vlayout.addSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.setLayout(self.vlayout)

        # self.plot_widget.signal_row_selection_changed.connect(self.set_current_datapoint)

        self.dataframe = None
        self.labels_column = None
        self.cmap = None

        self.previous_sort_column = ''

        self._transmission = None
        self._history_trace = None
        self.has_history_trace = False
        self.data_column = None

    def add_to_splitter(self, ui):
        self.splitter.addWidget(ui)
        return ui

    def _disconnect_comboBoxSort(self):
        try:
            self.comboBoxSortColumn.currentTextChanged.disconnect(self._set_sort_order)
        except TypeError:
            pass

    def _connect_comboBoxSort(self):
        self.comboBoxSortColumn.currentTextChanged.connect(self._set_sort_order)

    @staticmethod
    def merge_dataframes(dataframes) -> pd.DataFrame:
        if type(dataframes) is list:
            dataframe = pd.concat(dataframes)
        else:
            dataframe = dataframes

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError('Must pass a dataframe or list of dataframes')
        return dataframe

    def set_data(self, dataframes: Union[pd.DataFrame, list],
                 data_column: str,
                 labels_column: str,
                 cmap: str = 'jet',
                 transmission: Optional[Transmission] = None,
                 reset_sorting: bool = True,
                 **kwargs):
        """
        :param dataframes:      list of dataframes or a single DataFrame
        :param data_column:     data column of the dataframe that is plotted in the heatmap
        :param labels_column:   dataframe column (usually categorical labels) used to generate the y-labels and legend.
        :param cmap:            colormap choice
        :param transmission:    transmission object that dataframe originates, used to calculate data units if passed
        :param reset_sorting:   reset the order of the rows in the heatmap
        """
        dataframe = self.merge_dataframes(dataframes)
        self.data_column = data_column
        self.cmap = cmap
        self.labels_column = labels_column

        self.dataframe = dataframe.reset_index(drop=True)

        self._transmission = None
        self._history_trace = None
        self.has_history_trace = False

        if transmission is not None:
            if not isinstance(transmission, Transmission):
                raise TypeError("Argument 'transmission' must be of type mesmerize.analysis.data_types.Transmission")
            self.set_transmission(transmission)

        self._disconnect_comboBoxSort()

        if reset_sorting:
            self.comboBoxSortColumn.clear()
            self.comboBoxSortColumn.addItems(self.dataframe.columns.to_list())

        ix = self.comboBoxSortColumn.findText(self.previous_sort_column)
        if (ix != -1) and (self.previous_sort_column != ''):
            self.comboBoxSortColumn.setCurrentIndex(ix)
            self._set_sort_order(self.previous_sort_column)
        else:
            data = np.vstack(self.dataframe[self.data_column].values)
            self._set_plot(data)

        self._connect_comboBoxSort()

    def _set_plot(self, data_array: np.ndarray):
        ylabels = self.dataframe[self.labels_column]
        self.plot_widget.set(data_array, cmap=self.cmap, ylabels=ylabels)

    def _set_sort_order(self, column: str):
        self.dataframe.sort_values(by=[column], inplace=True)
        a = np.vstack(self.dataframe[self.data_column].values)
        self.previous_sort_column = column
        self._set_plot(a)

    def set_transmission(self, transmission: Transmission):
        self._transmission = transmission
        self.set_history_trace(transmission.history_trace)

    def get_transmission(self) -> Transmission:
        if self._transmission is None:
            raise ValueError('No tranmission has been set')
        else:
            return self._transmission

    def highlight_row(self, ix: int):
        self.plot_widget.highlight_row(ix)

    def set_history_trace(self, history_trace: HistoryTrace):
        assert isinstance(history_trace, HistoryTrace)
        self._history_trace = history_trace
        self.has_history_trace = True


class ControlWidget(QtWidgets.QWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_ControlWidget()
        self.ui.setupUi(self)
        self.setMaximumWidth(350)

        self.ui.listWidgetColorMaps.signal_colormap_changed.connect(lambda: self.sig_changed.emit())
        self.ui.comboBoxDataColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())
        self.ui.comboBoxLabelsColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())
        self.ui.comboBoxDPTCurveColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())


class HeatmapTracerWidget(HeatmapSplitterWidget):
    def __init__(self):
        HeatmapSplitterWidget.__init__(self)
        self.setWindowTitle('Heatmap Tracer Widget')
        self.control_widget = ControlWidget()
        self.add_to_splitter(self.control_widget)

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.add_to_splitter(self.live_datapoint_tracer)

        self.plot_widget.sig_selection_changed.connect(self.set_current_datapoint)

        self.datapoint_tracer_curve_column = None
        self._previous_df_columns = []

        self.control_widget.ui.pushButtonPlot.clicked.connect(self.update_plot)
        self.control_widget.sig_changed.connect(self.update_plot)

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

    @QtCore.pyqtSlot(tuple)
    def set_current_datapoint(self, ix: tuple):
        identifier = self.dataframe.iloc[ix[1]]['uuid_curve']
        r = self.dataframe[self.dataframe['uuid_curve'] == identifier]

        if self.has_history_trace:
            block_id = r._BLOCK_
            if isinstance(block_id, pd.Series):
                block_id = block_id.item()
            h = self._history_trace.get_data_block_history(block_id)
        else:
            h = None

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.get_transmission().get_proj_path(),
                                              history_trace=h)

    def set_input(self, transmission: Transmission):
        cols = transmission.df.columns
        if set(self._previous_df_columns) != set(cols):
            self.control_widget.ui.comboBoxDataColumn.clear()
            self.control_widget.ui.comboBoxDataColumn.addItems(cols)

            self.control_widget.ui.comboBoxLabelsColumn.clear()
            self.control_widget.ui.comboBoxLabelsColumn.addItems(cols)

            self.control_widget.ui.comboBoxDPTCurveColumn.clear()
            self.control_widget.ui.comboBoxDPTCurveColumn.addItems(cols)

        self._input_transmission = transmission
        self._previous_df_columns = cols

        if self.control_widget.ui.pushButtonPlot.isChecked():
            self.update_plot()

    def get_plot_opts(self) -> dict:
        d = dict(dataframes=self._input_transmission.df,
                 data_column=self.control_widget.ui.comboBoxDataColumn.currentText(),
                 labels_column=self.control_widget.ui.comboBoxLabelsColumn.currentText(),
                 datapoint_tracer_curve_column=self.control_widget.ui.comboBoxDPTCurveColumn.currentText(),
                 cmap=self.control_widget.ui.listWidgetColorMaps.current_cmap,
                 transmission=self._input_transmission)
        return d

    def set_plot_opts(self, opts: dict):
        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['data_column'])
        self.control_widget.ui.comboBoxDataColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxLabelsColumn.findText(opts['labels_column'])
        self.control_widget.ui.comboBoxLabelsColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['datapoint_tracer_curve_column'])
        self.control_widget.ui.comboBoxDPTCurveColumn.setCurrentIndex(ix)

    def update_plot(self):
        if not self.control_widget.ui.pushButtonPlot.isChecked():
            return

        self.set_data(**self.get_plot_opts())

    def set_data(self, *args, datapoint_tracer_curve_column: str = None, **kwargs):
        super(HeatmapTracerWidget, self).set_data(*args, **kwargs)
        self.datapoint_tracer_curve_column = datapoint_tracer_curve_column

    def save_plot(self):
        try:
            proj_path = self._input_transmission.get_proj_path()
        except ValueError:
            proj_path = ''
        plots_path = os.path.join(proj_path, 'plots')
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save plot as', plots_path, '(*.ptrn)')
        if path == '':
            return
        path = path[0]

        if not path.endswith('.ptrn'):
            path = f'{path}.ptrn'

        plot_state = self.get_plot_opts()
        plot_state.pop('dataframes')
        plot_state.pop('transmission')

        plot_state['type'] = self.__class__.__name__
        self._input_transmission.plot_state = plot_state
        self._input_transmission.to_hdf5(path)

    def open_plot_dialog(self):
        ptrn_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose plot file', '', '(*.ptrn)')
        if ptrn_path == '':
            return

        proj_path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Project Folder')

        if proj_path == '':
            return

        self.open_plot(ptrn_path[0], proj_path)

    def open_plot(self, ptrn_path: str, proj_path: str):
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
            QtWidgets.QMessageBox.warning(None, 'Invalid Project Folder', 'This is not a valid Mesmerize project\n' + e)
            return

        self.set_input(ptrn)
        self.set_plot_opts(plot_state)
        self.control_widget.ui.pushButtonSave.setChecked(True)
        self.update_plot()

