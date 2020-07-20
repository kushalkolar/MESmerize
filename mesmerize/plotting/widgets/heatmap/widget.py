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
from .control_widget_pytemplate import Ui_ControlWidget
import numpy as np
import pandas as pd
from typing import Optional, Union
from ....common.configuration import console_history_path
from ....common.qdialogs import present_exceptions, exceptions_label
from ....pyqtgraphCore.console import ConsoleWidget
from warnings import warn
import os


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
    """Widget for interactive heatmaps"""
    def __init__(self, highlight_mode='row'):
        """

        :param highlight_mode: Interactive mode, one of 'row' or 'item'
        """
        QtWidgets.QWidget.__init__(self)
        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.plot_variant: Heatmap = Heatmap(highlight_mode=highlight_mode)  #: That plot variant used by this plot widget

        self.labelSort = QtWidgets.QLabel(self)
        self.labelSort.setText('Sort heatmap according to column:')
        self.labelSort.setMinimumHeight(30)
        self.labelSort.setMaximumHeight(30)
        self.comboBoxSortColumn = QtWidgets.QComboBox(self)
        self.comboBoxSortColumn.currentTextChanged.connect(self._set_sort_order)

        self.plot_variant.layout().addWidget(self.labelSort)
        self.plot_variant.layout().addWidget(self.comboBoxSortColumn)

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.plot_variant)

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
        Set the data and then set the plot

        :param dataframes:      list of dataframes or a single DataFrame
        :param data_column:     data column of the dataframe that is plotted in the heatmap
        :param labels_column:   dataframe column (usually categorical labels) used to generate the y-labels and legend.
        :param cmap:            colormap choice
        :param transmission:    transmission object that dataframe originates, used to calculate data units if passed
        :param sort:            if False, the sort comboBox is ignored
        :param reset_sorting:   reset the order of the rows in the heatmap
        :param kwargs:          Passed to Heatmap.set
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
        self.plot_variant.set(data_array, cmap=self.cmap, ylabels=ylabels, **self.kwargs)

    @present_exceptions('Cannot sort', 'Make sure you choose an appropriate categorical column for sorting')
    def _set_sort_order(self, column: str):
        """
        Set the sort order of the heatmap rows according to a dataframe column. The column must contain categorical
        values. The rows are grouped together according to the categorical values.

        :param column: DataFrame column containing categorical values used for sorting the heatmap rows
        """
        self.dataframe.sort_values(by=[column], inplace=True)
        a = np.vstack(self.dataframe[self.data_column].values)
        self.previous_sort_column = column
        self._set_plot(a)

    def set_transmission(self, transmission: Transmission):
        """Set the input transmission"""
        self._transmission = transmission
        self.set_history_trace(transmission.history_trace)

    def get_transmission(self) -> Transmission:
        """Get the input transmission"""
        if self._transmission is None:
            raise ValueError('No tranmission has been set')
        else:
            return self._transmission

    def highlight_row(self, ix: int):
        """Highlight a row on the heatmap"""
        self.plot_variant.highlight_row(ix)

    def set_history_trace(self, history_trace: HistoryTrace):
        """Set the history trace object from the input transmission"""
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

        self.ui.pushButton_set_vmin_vmax.clicked.connect(self.sig_changed.emit)


class HeatmapTracerWidget(BasePlotWidget, HeatmapSplitterWidget):
    """Heatmap with an embedded datapoint tracer"""
    drop_opts = ['dataframes', 'transmission']  #: keys of the plot_opts dict that are not JSON compatible and not required for restoring this plot

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Heatmap Tracer Widget')
        self.control_widget = ControlWidget()
        self.add_to_splitter(self.control_widget)

        self.live_datapoint_tracer = DatapointTracerWidget()  #: The embedded `Datapoint Tracer <API_DatapointTracer>`
        self.add_to_splitter(self.live_datapoint_tracer)

        ns = {'this': self,
              'get_plot_area': lambda: self.plot_variant
              }

        txt = ["Namespaces",
               "self as 'this'",
               "Usefull callables, see docs for details:",
               "get_plot_area()"
               ]

        txt = "\n".join(txt)

        cmd_history_file = os.path.join(console_history_path, 'heatmap_tracer_widget')

        self.console_widget = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)
        self.console_widget.setVisible(False)
        self.control_widget.ui.pushButtonShowHideConsole.toggled.connect(self.console_widget.setVisible)
        self.vlayout.addWidget(self.console_widget)

        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setMaximumHeight(32)
        self.status_label.mousePressEvent = self.show_exception_info
        self.vlayout.addWidget(self.status_label)

        self.exception_holder = None  #: Used for holding exceptions that can be viewed by clicking on self.status_label

        self.plot_variant.sig_selection_changed.connect(self.set_current_datapoint)

        self.datapoint_tracer_curve_column = None

        self.control_widget.ui.listWidgetColorMapsData.set_cmap('jet')

        self.control_widget.ui.pushButtonPlot.clicked.connect(self.update_plot)

        self.control_widget.ui.checkBoxLiveUpdate.toggled.connect(self.set_update_live)

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot_dialog)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

        self.update_live = False
        self.block_signals_list = [self.control_widget]

        self.is_clustering = False

        self.control_widget.sig_changed.connect(self.update_plot)

    @BasePlotWidget.signal_blocker
    def set_update_live(self, b: bool):
        """Set whether the plot should update live with changes in the flowchart"""
        self.update_live = b
        self.control_widget.ui.checkBoxLiveUpdate.setChecked(b)
        if b:
            self.update_plot()

    @QtCore.pyqtSlot(tuple)
    def set_current_datapoint(self, ix: tuple):
        """
        Set the currently selected datapoint in the :ref:`Datapoint Tracer <DatapointTracer>`.

        :param ix: index, (x, y). x is always 0 for this widget since it only uses 'row' selection mode and not 'item'
        """
        try:
            if self.is_clustering:
                ix = self.plot_variant.plot.dendrogram_row.reordered_ind[ix[1]]
            else:
                ix = ix[1]
            identifier = self.dataframe.iloc[ix]['uuid_curve']
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
        """Set the input Transmission and update the plot if update_live is True"""
        if (self._transmission is None) or self.update_live:
            super(HeatmapTracerWidget, self).set_input(transmission)
            if self.update_live:
                self._set_vmin_vmax_limits()
                self.update_plot()

    def _set_vmin_vmax_limits(self):
        data_column = self.control_widget.ui.comboBoxDataColumn.currentText()
        data = np.vstack(self.transmission.df[data_column].values)

        _min = np.nanmin(data)
        _max = np.nanmax(data)

        range = abs(_min - _max)

        ws = [
                self.control_widget.ui.doubleSpinBox_vmin,
                self.control_widget.ui.doubleSpinBox_vmax,
             ]

        for w in ws:
            w.setMinimum(_min)
            w.setMaximum(_max)

        for w in ws:
            w.setSingleStep(range / 10)

        self.control_widget.ui.doubleSpinBox_vmin.setValue(_min)
        self.control_widget.ui.doubleSpinBox_vmax.setValue(_max)

    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        # self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.setItems(data_columns)

        # self.control_widget.ui.comboBoxLabelsColumn.clear()
        self.control_widget.ui.comboBoxLabelsColumn.setItems(categorical_columns)

        # self.control_widget.ui.comboBoxDPTCurveColumn.clear()
        self.control_widget.ui.comboBoxDPTCurveColumn.setItems(data_columns)

    def get_plot_opts(self, drop: bool = False) -> dict:
        """
        Get the plot options

        :param drop: Drop the non-json compatible objects that are not necessary to restore this plot
        """
        new_datacolumn = self.control_widget.ui.comboBoxDataColumn.currentText()

        if self.data_column != new_datacolumn:
            self._set_vmin_vmax_limits()

        d = dict(dataframes=self.transmission.df,
                 data_column=new_datacolumn,
                 labels_column=self.control_widget.ui.comboBoxLabelsColumn.currentText(),
                 datapoint_tracer_curve_column=self.control_widget.ui.comboBoxDPTCurveColumn.currentText(),
                 cmap=self.control_widget.ui.listWidgetColorMapsData.current_cmap,
                 transmission=self.transmission,
                 ylabels_cmap=self.control_widget.ui.listWidgetColorMapsLabels.current_cmap,
                 vmin=self.control_widget.ui.doubleSpinBox_vmin.value(),
                 vmax=self.control_widget.ui.doubleSpinBox_vmax.value()
                 )

        if drop:
            for k in self.drop_opts:
                d.pop(k)
        return d

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        """Set all plot options from a dict"""
        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['data_column'])
        self.control_widget.ui.comboBoxDataColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxLabelsColumn.findText(opts['labels_column'])
        self.control_widget.ui.comboBoxLabelsColumn.setCurrentIndex(ix)

        ix = self.control_widget.ui.comboBoxDataColumn.findText(opts['datapoint_tracer_curve_column'])
        self.control_widget.ui.comboBoxDPTCurveColumn.setCurrentIndex(ix)

        self.control_widget.ui.listWidgetColorMapsData.set_cmap(opts['cmap'])
        self.control_widget.ui.listWidgetColorMapsLabels.set_cmap(opts['ylabels_cmap'])

    def update_plot(self):
        """Calls set_data and passes dict from get_plot_opts() as keyword arguments"""
        self.set_data(**self.get_plot_opts())

    def get_cluster_kwargs(self) -> dict:
        """Organize kwargs for visualization of hierarchical clustering"""
        # Just get the first datablock ID since Agglomerative clustering would have been done on all data blocks
        db_id = self.transmission.history_trace.data_blocks[0]
        linkage = np.array(self.transmission.history_trace.get_operation_params(data_block_id=db_id, operation='fcluster')['linkage_matrix'])
        cluster_labels = self.transmission.df['FCLUSTER_LABELS']
        ck = dict(row_linkage=linkage, row_cluster=True, col_cluster=False, cluster_labels=cluster_labels)
        return ck

    @exceptions_label('status_label', 'exception_holder', 'Error while setting data', 'Make sure you have selected appropriate columns')
    def set_data(self, *args, datapoint_tracer_curve_column: str = None, **kwargs):
        """
        Set the plot data, parameters and draw the plot.
        If the input Transmission comes directly from the FCluster it will pass a dict from get_cluster_kwargs() to the
        cluster_kwargs argument. Else it will pass None to cluster_kwargs.

        :param args: arguments to pass to superclass set_data() method
        :param datapoint_tracer_curve_column: Data column containing curves to use in the datapoint tracer
        :param kwargs:  keyword arguments, passed to superclass set_data() method
        """
        self.exception_holder = None
        self.status_label.clear()

        if self.transmission.last_output == 'fcluster':
            self.comboBoxSortColumn.setDisabled(True)
            self.is_clustering = True
            super(HeatmapTracerWidget, self).set_data(*args, cluster_kwargs=self.get_cluster_kwargs(), sort=False, **kwargs)
        else:
            self.is_clustering = False
            super(HeatmapTracerWidget, self).set_data(*args, cluster_kwargs=None, **kwargs)

        self.datapoint_tracer_curve_column = datapoint_tracer_curve_column

    def show_exception_info(self, mouse_press_ev):
        if self.exception_holder is not None:
            QtWidgets.QMessageBox.warning(self, *self.exception_holder)
