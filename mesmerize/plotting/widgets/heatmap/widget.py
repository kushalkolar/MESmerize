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
from ..base import BasePlotWidget
from .. import DatapointTracerWidget
from ....analysis.data_types import HistoryTrace, Transmission
from ....analysis import organize_dataframe_columns
from .control_widget import Ui_ControlWidget
import numpy as np
import pandas as pd
from typing import Optional, Union
from ....common.qdialogs import present_exceptions
from warnings import warn


def help_func(e, tb):
    def show_info(info):
        QtWidgets.QMessageBox.information(None, 'Help info', info)
        return

    if str(e).startswith('all the input array dimensions for the concatenation axis must match exactly'):
        show_info('Make sure that the data under the "Data column" has been spliced.')

    elif str(e).startswith('Too many colors requested for the chosen cmap'):
        show_info('The chosen categorical labels column can only have a maximum of 20 unique labels.')

    elif 'unhashable type' in str(e):
        show_info('One of your selected columns has data type that is incompatible with what you have selected it for')


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
                 sort: bool = True,
                 reset_sorting: bool = True,
                 **kwargs):
        """
        :param dataframes:      list of dataframes or a single DataFrame
        :param data_column:     data column of the dataframe that is plotted in the heatmap
        :param labels_column:   dataframe column (usually categorical labels) used to generate the y-labels and legend.
        :param cmap:            colormap choice
        :param transmission:    transmission object that dataframe originates, used to calculate data units if passed
        :param sort:            if False, the sort comboBox is ignored
        :param reset_sorting:   reset the order of the rows in the heatmap
        """
        dataframe = self.merge_dataframes(dataframes)
        self.data_column = data_column
        self.cmap = cmap
        self.labels_column = labels_column

        self.dataframe = dataframe.reset_index(drop=True)

        self.kwargs = kwargs
        # print(kwargs)

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
            self.comboBoxSortColumn.addItems(organize_dataframe_columns(self.dataframe.columns)[1])

        if sort:
            ix = self.comboBoxSortColumn.findText(self.previous_sort_column)
            if (ix != -1) and (self.previous_sort_column != ''):
                self.comboBoxSortColumn.setCurrentIndex(ix)
                self.dataframe.sort_values(by=[self.previous_sort_column], inplace=True)

        data = np.vstack(self.dataframe[self.data_column].values)

        self._set_plot(data)

        self._connect_comboBoxSort()

    def _set_plot(self, data_array: np.ndarray):
        ylabels = self.dataframe[self.labels_column]
        self.plot_widget.set(data_array, cmap=self.cmap, ylabels=ylabels, **self.kwargs)

    @present_exceptions('Cannot sort', 'Make sure you choose an appropriate categorical column for sorting')
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

        self.ui.listWidgetColorMapsLabels.set_cmap('tab10')

        self.ui.listWidgetColorMapsData.signal_colormap_changed.connect(lambda: self.sig_changed.emit())
        self.ui.listWidgetColorMapsLabels.signal_colormap_changed.connect(lambda: self.sig_changed.emit())

        self.ui.comboBoxDataColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())
        self.ui.comboBoxLabelsColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())
        self.ui.comboBoxDPTCurveColumn.currentTextChanged.connect(lambda: self.sig_changed.emit())


class HeatmapTracerWidget(BasePlotWidget, HeatmapSplitterWidget):
    drop_opts = ['dataframes', 'transmission']

    def __init__(self):
        super(HeatmapTracerWidget, self).__init__()
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

        self.control_widget.ui.checkBoxLiveUpdate.toggled.connect(self.set_update_live)

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot_dialog)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

        self._update_live = False
        self.block_signals_list = [self.control_widget]

    def set_update_live(self, b: bool):
        self._update_live = b
        if b:
            self.update_plot()

    @QtCore.pyqtSlot(tuple)
    def set_current_datapoint(self, ix: tuple):
        try:
            identifier = self.dataframe.iloc[ix[1]]['uuid_curve']
        except IndexError:
            warn('Datapoint index out of bounds. Probably clicked a plot point outside of the data')
            return
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

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        super(HeatmapTracerWidget, self).set_input(transmission)
        cols = self.transmission.df.columns
        if set(self._previous_df_columns) != set(cols):
            dcols, ccols, ucols = organize_dataframe_columns(cols)

            self.control_widget.ui.comboBoxDataColumn.clear()
            self.control_widget.ui.comboBoxDataColumn.addItems(dcols)

            self.control_widget.ui.comboBoxLabelsColumn.clear()
            self.control_widget.ui.comboBoxLabelsColumn.addItems(ccols)

            self.control_widget.ui.comboBoxDPTCurveColumn.clear()
            self.control_widget.ui.comboBoxDPTCurveColumn.addItems(dcols)

        # self.transmission = transmission
        self._previous_df_columns = cols

        if self._update_live:
            self.update_plot()

    def get_plot_opts(self) -> dict:
        d = dict(dataframes=self.transmission.df,
                 data_column=self.control_widget.ui.comboBoxDataColumn.currentText(),
                 labels_column=self.control_widget.ui.comboBoxLabelsColumn.currentText(),
                 datapoint_tracer_curve_column=self.control_widget.ui.comboBoxDPTCurveColumn.currentText(),
                 cmap=self.control_widget.ui.listWidgetColorMaps.current_cmap,
                 transmission=self.transmission)
        return d

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['data_column'])
        self.control_widget.ui.comboBoxDataColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxLabelsColumn.findText(opts['labels_column'])
        self.control_widget.ui.comboBoxLabelsColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['datapoint_tracer_curve_column'])
        self.control_widget.ui.comboBoxDPTCurveColumn.setCurrentIndex(ix)

        self.control_widget.ui.listWidgetColorMapsData.set_cmap(opts['cmap'])

    def update_plot(self):
        self.set_data(**self.get_plot_opts())

    def get_cluster_kwargs(self) -> dict:
        # Just get the first datablock ID since Agglomerative clustering would have been done on all data blocks
        db_id = self.transmission.history_trace.data_blocks[0]
        children = np.array(self.transmission.history_trace.get_operation_params(data_block_id=db_id, operation='agglomerative_clustering')['children'])
        distance = np.arange(children.shape[0])
        obs = np.arange(2, children.shape[0] + 2)
        lkg = np.column_stack([children, distance, obs]).astype(np.float64)

        ck = dict(row_linkage=lkg, row_cluster=True, col_cluster=False)
        return ck

    @present_exceptions('Error while setting data', 'Make sure you have selected appropriate columns.', help_func)
    def set_data(self, *args, datapoint_tracer_curve_column: str = None, **kwargs):
        if self.transmission.last_output == 'AGG_CLUSTER_LABEL':
            self.comboBoxSortColumn.setDisabled(True)
            super(HeatmapTracerWidget, self).set_data(*args, cluster_kwargs=self.get_cluster_kwargs(), sort=False, **kwargs)
        else:
            super(HeatmapTracerWidget, self).set_data(*args, cluster_kwargs=None, **kwargs)

        self.datapoint_tracer_curve_column = datapoint_tracer_curve_column


