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
from copy import deepcopy
# from functools import partial
import traceback
from ...common import configuration, get_project_manager


MOD_NOT = '$NOT:'
MOD_STR = '$STR:'
MOD_STR_EQ = '$STR=:'
MOD_STR_NOT_EQ = '$STR!=:'
MOD_GT = '$>:'
MOD_LT = '$<:'
MOD_GE = '$>=:'
MOD_LE = '$<=:'


class TabAreaWidget(QtWidgets.QWidget):
    signal_new_tab_requested = QtCore.pyqtSignal(pd.DataFrame, list)
    signal_open_sample_in_viewer_requested = QtCore.pyqtSignal(str)

    def __init__(self, parent, tab_name: str, dataframe: pd.DataFrame, filter_history: list, is_root=False):
        QtWidgets.QWidget.__init__(self, parent)

        self.vertical_layout = QtWidgets.QVBoxLayout(self)
        self.columns_widget = DataFrameColumnsWidget(parent=self)
        self.vertical_layout.addWidget(self.columns_widget)

        self.tab_name = tab_name
        self.is_root = is_root
        self.filter_history = filter_history
        self.dataframe = dataframe

        self.columns = []

        # def initialize_gui(self):
        for column in self.dataframe.columns:
            if column in configuration.proj_cfg['EXCLUDE'].keys():
                continue

            c = ColumnWidget(parent=self.columns_widget,
                             tab_name=self.tab_name,
                             column_name=column,
                             is_root=self.is_root)

            c.signal_apply_clicked.connect(self.slot_filter_requested)
            if column == 'SampleID':
                c.signal_sample_id.connect(self.emit_open_sample_in_viewer_requested)
            self.columns.append(c)
            self.columns_widget.add_column(c)

        self.populate_tab()
        # self.columns_widget.show()

    @QtCore.pyqtSlot(str)
    def emit_open_sample_in_viewer_requested(self, sample_id: str):
        self.signal_open_sample_in_viewer_requested.emit(sample_id)

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
    def slot_filter_requested(self, d: dict):
        column_widget = d['column_widget']

        dataframe = self.dataframe.copy()

        if (d['option'] is None) or (d['option'] == 'new'):
            try:
                dataframe, history = self._filter(column_widget, dataframe)
            except (ValueError, TypeError) as e:
                QtWidgets.QMessageBox.warning(self, 'Invalid entry', str(e))
                return

        elif (d['option'] == 'all') or (d['option'] == 'all_in_new'):
            history = []
            for column in self.columns:
                assert isinstance(column, ColumnWidget)
                if column.lineEdit.text() != '':
                    try:
                        dataframe, h = self._filter(column, dataframe)
                        history += h
                    except (ValueError, TypeError) as e:
                        QtWidgets.QMessageBox.warning(self, 'Invalid entry', str(e))
                        return
        filter_history = deepcopy(self.filter_history)
        filter_history += history
        if self.is_root or (d['option'] == 'all_in_new') or (d['option'] == 'new'):
            self.signal_new_tab_requested.emit(dataframe, filter_history)
            return

        else:
            self.dataframe = dataframe
            self.filter_history += filter_history
            self.populate_tab()

        get_project_manager().child_dataframes[self.tab_name]['dataframe'] = self.dataframe
        get_project_manager().child_dataframes[self.tab_name]['filter_history'] = self.filter_history

    def _filter(self, column_widget: ColumnWidget, dataframe: pd.DataFrame) -> tuple:
        filt = column_widget.lineEdit.text()

        if filt.startswith('$') \
                and not filt.startswith(('$NOT:',
                                         '$STR:',
                                         '$STR=:',
                                         '$STR!=:',
                                         '$>:',
                                         '$<:',
                                         '$>=:',
                                         '$<=:')):

            raise ValueError('Unrecognized modifer in column ' + str(column_widget.column_name))

        if column_widget.column_type is list:
            if filt.startswith(MOD_NOT):  # NOT
                filt = filt[len(MOD_NOT):].split('|')
                selection = ~dataframe[column_widget.column_name].apply(
                    lambda l: any([v in u for u in l for v in filt])  # True if any str in the `filt` list is a
                )                                                     # substring in the `l` list
                selection_str = \
                    f'~df["{column_widget.column_name}"].apply(' \
                            f'lambda l: any([v in u for u in l for v in {str(filt)}])'

            elif filt.startswith(MOD_STR):  # treat as str, same as not using this modifier for this case
                filt = filt[len(MOD_STR):].split('|')
                selection = dataframe[column_widget.column_name].apply(
                    lambda l: any([v in u for u in l for v in filt])
                )
                selection_str = \
                    f'df["{column_widget.column_name}"].apply(' \
                        f'lambda l: any([v in u for u in l for v in {str(filt)}])'

            elif filt.startswith(MOD_STR_EQ):  # exact match of str
                filt = filt[len(MOD_STR_EQ):].split('|')
                selection = dataframe[column_widget.column_name].apply(
                    lambda l: any([v == u for u in l for v in filt])  # True if any str in the `filt` list is
                )                                                     # an exact match of any strings in `l`
                selection_str = \
                    f'df["{column_widget.column_name}"].apply(' \
                        f'lambda l: any([v == u for u in l for v in {str(filt)}])'

            elif filt.startswith(MOD_STR_NOT_EQ):  # negation of exact match of str
                filt = filt[len(MOD_STR_NOT_EQ):].split('|')
                selection = ~dataframe[column_widget.column_name].apply(
                    lambda l: any([v == u for u in l for v in filt])
                )
                selection_str = \
                    f'~df["{column_widget.column_name}"].apply(' \
                        f'lambda l: any([v == u for u in l for v in {str(filt)}])'

            else:
                filt = filt.split('|')  # check if any of the input strings are a substring in the list
                selection = dataframe[column_widget.column_name].apply(
                    lambda l: any([v in u for u in l for v in filt])
                )
                selection_str = \
                    f'df["{column_widget.column_name}"].apply(' \
                        f'lambda l: any([v in u for u in l for v in {str(filt)}])'

        elif column_widget.column_type is str or \
                filt.startswith('$STR:') or \
                filt.startswith('$STR=:') or \
                filt.startswith('$STR!=:'):

            if filt.startswith('$NOT:'):
                filt = filt[5:]
                selection = ~dataframe[column_widget.column_name].str.contains(filt)
                selection_str = '~df["' + column_widget.column_name + '"].str.contains("' + filt + '")'

            elif filt.startswith('$STR:'):
                filt = filt[5:]
                selection = dataframe[column_widget.column_name].str.contains(filt)
                selection_str = 'df["' + column_widget.column_name + '"].str.contains("' + filt + '")'

            elif filt.startswith('$STR=:'):
                filt = filt[6:].split('|')
                selection = dataframe[column_widget.column_name].isin(filt)
                selection_str = 'df["' + column_widget.column_name + '"].isin(' + str(filt) + ')'

            elif filt.startswith('$STR!=:'):
                filt = filt[7:].split('|')
                selection = ~dataframe[column_widget.column_name].isin(filt)
                selection_str = '~df["' + column_widget.column_name + '"].isin(' + str(filt) + ')'

            else:
                selection = dataframe[column_widget.column_name].str.contains(filt)
                selection_str = 'df["' + column_widget.column_name + '"].str.contains("' + filt + '")'

        elif column_widget.column_type in [int, float, int64, float64]:
            filt = column_widget.lineEdit.text()

            if column_widget.column_type is int:
                t_func = 'int'
            elif column_widget.column_type is float:
                t_func = 'float'
            elif column_widget.column_type is int64:
                t_func = 'int64'
            elif column_widget.column_type is float64:
                t_func = 'float64'

            if filt.startswith('$NOT:'):
                filt = filt[5:].split('|')
                filt = list(map(column_widget.column_type, filt))
                selection = ~dataframe[column_widget.column_name].isin(filt)
                selection_str = '~df["' + column_widget.column_name + '"].isin(' + str(filt) + ')'

            elif filt.startswith('$') and '|' in filt:
                raise ValueError('Nonsensical filter\nYou cannot use ">" or "<" operators in combination with "|"')

            elif filt.startswith('$>:'):
                filt = column_widget.column_type(filt[3:])
                selection = dataframe[column_widget.column_name] > column_widget.column_type(filt)
                selection_str = 'df["' + column_widget.column_name + '"] > ' + t_func + '(' + str(filt) + ')'

            elif filt.startswith('$<:'):
                filt = column_widget.column_type(filt[3:])
                selection = dataframe[column_widget.column_name] < column_widget.column_type(filt)
                selection_str = 'df["' + column_widget.column_name + '"] < ' + t_func + '(' + str(filt) + ')'

            elif filt.startswith('$>=:'):
                filt = column_widget.column_type(filt[4:])
                selection = dataframe[column_widget.column_name] >= column_widget.column_type(filt)
                selection_str = 'df["' + column_widget.column_name + '"] >= ' + t_func + '(' + str(filt) + ')'

            elif filt.startswith('$<=:'):
                filt = column_widget.column_type(filt[4:])
                selection = dataframe[column_widget.column_name] <= column_widget.column_type(filt)
                selection_str = 'df["' + column_widget.column_name + '"] <= ' + t_func + '(' + str(filt) + ')'

            else:
                filt = filt.split('|')
                filt = list(map(column_widget.column_type, filt))
                selection = dataframe[column_widget.column_name].isin(filt)
                selection_str = 'df["' + column_widget.column_name + '"].isin(' + str(filt) + ')'

        else:
            raise TypeError('Unsupported type for filtering, '
                            'can only support str, list, int, float, '
                            'numpy.int64 and numpy.float64')

        filtered_df = dataframe[selection]
        filter_history = 'df[' + selection_str + ']'

        return filtered_df, [filter_history]

    def populate_tab(self):
        if self.dataframe.size < 1:
            self.set_columns_empty()
            return

        for column in self.columns:
            try:
                self._populate_column(column, self.dataframe[column.column_name])
            except Exception:
                raise ValueError(f"Cannot open project due to an issue with the following column: `{column.column_name}`\n")

    def _populate_column(self, column: ColumnWidget, series: pd.Series):
        column.series = series
