#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 17 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .dataframe_columns_widget import DataFrameColumnsWidget
from .column_widget import ColumnWidget
import pandas as pd
# from common import configurationt
from numpy import int64, float64


class TabAreaWidget(QtWidgets.QWidget):
    signal_new_tab_requested = QtCore.pyqtSignal(pd.DataFrame, list)

    def __init__(self, parent, tab_name, dataframe, filter_history, is_root=False):
        QtWidgets.QWidget.__init__(self)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.columns_widget = DataFrameColumnsWidget(self)
        self.vertical_layout.addWidget(self.columns_widget)

        self.tab_name = tab_name
        self.is_root = is_root
        self.filter_history = filter_history
        self.dataframe = dataframe

        self.columns = []

    # def initialize_gui(self):
        for column in self.dataframe.columns:
            # if column in configuration.proj_cfg['EXCLUDE']:
            #     continue

            c = ColumnWidget(parent=self.columns_widget,
                             tab_name=self.tab_name,
                             column_name=column,
                             is_root=self.is_root)

            c.signal_apply_clicked.connect(self.slot_filter_requested)
            self.columns.append(c)
            self.columns_widget.add_column(c)

        self.populate_tab()
        # self.columns_widget.show()

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._dataframe

    @dataframe.setter
    def dataframe(self, dataframe: pd.DataFrame):
        self._dataframe = dataframe

    def set_columns_empty(self):
        for column in self.columns:
            column.set_empty()

    @QtCore.pyqtSlot(dict)
    def slot_filter_requested(self, d):
        print(d)
        column_widget = d['column_widget']

        dataframe = self.dataframe.copy()
        filter_history = []

        if (d['option'] is None) or (d['option'] == 'new'):
            dataframe, filter_history = self._filter(column_widget, dataframe)

        elif (d['option'] == 'all') or (d['option'] == 'all_in_new'):
            for column in self.columns:
                assert isinstance(column, ColumnWidget)
                if column.lineEdit.text() != '':
                    dataframe, history = self._filter(column, dataframe)
                    filter_history += history

        if self.is_root or (d['option'] == 'all_in_new') or (d['option'] == 'new'):
            self.signal_new_tab_requested.emit(dataframe, filter_history)
            return

        else:
            self.dataframe = dataframe
            self.filter_history = filter_history
            self.populate_tab()

    def _filter(self, column_widget: ColumnWidget, dataframe: pd.DataFrame) -> tuple:
        if column_widget.column_type in [str, list]:
            filt = column_widget.lineEdit.text()
            if filt.startswith('$NOT:'):
                filt = filt[5:]
                selection = dataframe[column_widget.column_name].str.contains(filt)
                filtered_df = dataframe[~selection]
                filter_history = {'filter_type': '!str.contains', 'filter': filt}
            else:
                selection = dataframe[column_widget.column_name].str.contains(filt)
                filtered_df = dataframe[selection]
                filter_history = {'filter_type': 'str.contains', 'filter': filt}

        elif column_widget.column_type in [int, float, int64, float64]:
            filt = column_widget.lineEdit.text()
            if filt.startswith('$NOT:'):
                filt = filter[5:]
                selection = dataframe[column_widget.column_name] != column_widget.column_type(filt)
                filter_history = {'filter_type': '!=', 'filter': column_widget.column_type(filt)}

            else:
                selection = dataframe[column_widget.column_name] == column_widget.column_type(filt)
                filter_history = {'filter_type': '==', 'filter': column_widget.column_type(filt)}

            filtered_df = dataframe[selection]

        else:
            raise TypeError('Unsupported type for filtering, '
                            'can only support str, list, int, float, '
                            'numpy.int64 and numpy.float64')

        return filtered_df, filter_history

    def populate_tab(self):
        if self.dataframe.size < 1:
            self.set_columns_empty()
            return

        for column in self.columns:
            self._populate_column(column, self.dataframe[column.column_name])

    def _populate_column(self, column: ColumnWidget, series: pd.Series):
        column.series = series
