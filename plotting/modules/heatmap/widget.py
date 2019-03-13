#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from PyQt5 import QtCore, QtWidgets
from .heatmap import Heatmap
import numpy as np
import pandas as pd
from ...datapoint_tracer import DatapointTracerWidget
from analyser.DataTypes import HistoryTrace, Transmission


class HeatmapWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = Heatmap()

        self.vlayout.addWidget(self.plot_widget)
        self.setLayout(self.vlayout)

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


class HeatmapTracerWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.plot_widget = Heatmap()

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

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.splitter.addWidget(self.live_datapoint_tracer)

        self.vlayout.addWidget(self.splitter)
        # self.vlayout.addSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        self.setLayout(self.vlayout)

        self.plot_widget.signal_row_selection_changed.connect(self.set_current_datapoint)

        self.dataframe = None
        self.labels_column = None
        self.cmap = None

        self.previous_sort_column = ''

        self._transmission = None
        self._history_trace = None
        self.has_history_trace = False
        self.data_column = None
        self.datapoint_tracer_curve_column = None

    @QtCore.pyqtSlot(int)
    def set_current_datapoint(self, ix: int):
        identifier = self.dataframe.iloc[ix]['uuid_curve']
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

    def _disconnect_comboBoxSort(self):
        try:
            self.comboBoxSortColumn.currentTextChanged.disconnect(self._set_sort_order)
        except TypeError:
            pass

    def _connect_comboBoxSort(self):
        self.comboBoxSortColumn.currentTextChanged.connect(self._set_sort_order)

    def set_data(self, dataframes,
                 data_column: str,
                 labels_column: str,
                 datapoint_tracer_curve_column: str,
                 cmap: str = 'jet',
                 transmission: Transmission = None,
                 reset_data: bool = True):

        if type(dataframes) is list:
            dataframe = pd.concat(dataframes)
        else:
            dataframe = dataframes

        assert isinstance(dataframe, pd.DataFrame)

        self.data_column = data_column
        self.cmap = cmap
        self.labels_column = labels_column

        self.dataframe = dataframe.reset_index(drop=True)

        self._transmission = None
        self._history_trace = None
        self.has_history_trace = False

        if transmission is not None:
            assert isinstance(transmission, Transmission)
            self.set_transmission(transmission)

        self.datapoint_tracer_curve_column = datapoint_tracer_curve_column

        self._disconnect_comboBoxSort()

        if reset_data:
            self.comboBoxSortColumn.clear()
            self.comboBoxSortColumn.addItems(dataframe.columns.to_list())

        ix = self.comboBoxSortColumn.findText(self.previous_sort_column)
        if (ix != -1) and (self.previous_sort_column != ''):
            self.comboBoxSortColumn.setCurrentIndex(ix)
            self._set_sort_order(self.previous_sort_column)
        else:
            data = np.vstack(self.dataframe[self.data_column].values)
            self._set_plot(data)

        self._connect_comboBoxSort()

    def _set_plot(self, data_array: np.ndarray):
        cmap = self.cmap
        ylabels = self.dataframe[self.labels_column]
        self.plot_widget.set(data_array, cmap=self.cmap, ylabels_bar=ylabels)

    def _set_sort_order(self, column: str):
        self.dataframe.sort_values(by=[column], inplace=True)
        a = np.vstack(self.dataframe[self.data_column].values)
        self.previous_sort_column = column
        self._set_plot(a)

    def set_transmission(self, transmission):
        self._transmission = transmission
        self.set_history_trace(transmission.history_trace)

    def get_transmission(self) -> Transmission:
        if self._transmission is None:
            raise ValueError('No tranmission is set')
        else:
            return self._transmission

    def highlight_row(self, ix):
        self.plot_widget.highlight_row(ix)

    def set_history_trace(self, history_trace: HistoryTrace):
        assert isinstance(history_trace, HistoryTrace)
        self._history_trace = history_trace
        self.has_history_trace = True
