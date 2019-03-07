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

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.plot_widget)
        self.live_datapoint_tracer = DatapointTracerWidget()
        self.splitter.addWidget(self.live_datapoint_tracer)

        self.vlayout.addWidget(self.splitter)
        self.setLayout(self.vlayout)

        self.plot_widget.signal_row_selection_changed.connect(self.set_current_datapoint)

        self.dataframe = None
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

    def set_data(self, dataframes, data_column: str, labels_column: str, datapoint_tracer_curve_column: str, cmap: str ='jet',
                 transmission: Transmission = None):
        if type(dataframes) is list:
            dataframe = pd.concat(dataframes)
        elif type(dataframes) is not pd.DataFrame:
            QtWidgets.QMessageBox.warning(self, 'Invalid input data', 'You can only '
                                                                      'pass in a dataframe or a list of dataframes')
            return
        else:
            dataframe = dataframes

        self.data_column = data_column

        labels = dataframe[labels_column]

        self.dataframe = dataframe.reset_index(drop=True)
        data = np.vstack(self.dataframe[data_column].values)
        self.plot_widget.set(data, cmap=cmap, yticklabels=labels)

        self._transmission = None
        self._history_trace = None
        self.has_history_trace = False

        if transmission is not None:
            assert isinstance(transmission, Transmission)
            self.set_transmission(transmission)

        self.datapoint_tracer_curve_column = datapoint_tracer_curve_column

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
