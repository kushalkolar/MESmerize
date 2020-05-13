#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from .tab_page_pytemplate import *
from .row import Row
import pandas as pd
from functools import partial
from typing import Union


class Page(QtWidgets.QWidget):
    def __init__(self, parent, stim_type: str):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_TabPage()
        self.ui.setupUi(self)

        self.stim_type = stim_type
        self.rows = []  #: List of row objects, each row holds one stimulus period.
        self.ui.btnAddRow.clicked.connect(lambda: self.add_row())

    def set_data(self, dataframe: pd.DataFrame):
        """
        Set the stimulus map

        :param dataframe: DataFrame with the appropriate rows (see add_row())
        """
        self.clear()
        for ix, series in dataframe.iterrows():
            self.add_row(series)

    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the stimulus map as a DataFrame
        """
        if len(self.rows) < 1:
            raise IndexError('No stimuli input for this stimulus type: ' + self.stim_type)

        l = []
        for row in self.rows:
            l.append(row.get_dict())
        return pd.DataFrame(l)

    def set_units(self, units: str):
        """
        Set the time units

        :param units: One of 'frames' or 'seconds'
        """

        if units not in ['frames', 'seconds']:
            raise ValueError('Units must be either "frames" or "seconds"')

        ix = self.ui.comboBoxTimeUnits.findText(units)
        self.ui.comboBoxTimeUnits.setCurrentIndex(ix)

    def get_units(self) -> str:
        """
        Get the time units
        """
        return self.ui.comboBoxTimeUnits.currentText()

    def add_row(self, pd_series: pd.Series = None):
        """
        Add a row to the stimulus map

        :param pd_series: pandas series containing the following: stimulus name, start, end, and color
        :return:
        """
        row = Row(pd_series)
        self.rows.append(row)
        row.btn_remove.clicked.connect(partial(self.delete_row, row))
        self.ui.verticalLayout.insertLayout(self.ui.verticalLayout.count() - 1, row.hlayout)

    def delete_row(self, row: Union[Row, int]):
        """
        Delete a row from the stimulus map

        :param row: The Row object to remove or the numerical index of the row
        """

        if isinstance(row, int):
            row = self.rows[row]
        if not isinstance(row, Row):
            raise TypeError("row must be either a Row object or int")

        self.ui.verticalLayout.removeItem(row.hlayout)
        self.rows.remove(row)
        row.delete()
        row.hlayout.deleteLater()
        row.deleteLater()

    def clear(self):
        """Clear the stimulus map"""
        while len(self.rows) > 0:
            self.delete_row(self.rows[0])

    def set_stim_autocompleter(self, stimulus_list: list):
        autocompleter = QtWidgets.QCompleter(stimulus_list)
        for row in self.rows:
            row.name.setCompleter(autocompleter)
