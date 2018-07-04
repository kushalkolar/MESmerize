#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

if __name__ == '__main__':
    from tab_page_pytemplate import Ui_TabPage
    from row import Row
else:
    from .tab_page_pytemplate import *
    from .row import Row
import pandas as pd
from functools import partial


class Page(QtWidgets.QWidget):
    def __init__(self, parent, stim_type: str):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_TabPage()
        self.ui.setupUi(self)

        self.stim_type = stim_type
        self.rows = []
        self.ui.btnAddRow.clicked.connect(lambda: self.add_row())

    def set_data(self, dataframe: pd.DataFrame):
        self.clear()
        for ix, series in dataframe.iterrows():
            self.add_row(series)

    def add_row(self, pd_series=None):
        row = Row(pd_series)
        self.rows.append(row)
        row.btn_remove.clicked.connect(partial(self.delete_row, row))
        self.ui.verticalLayout.insertLayout(self.ui.verticalLayout.count() - 1, row.hlayout)

    def delete_row(self, row):
        self.ui.verticalLayout.removeItem(row.hlayout)
        row.delete()
        row.hlayout.deleteLater()
        row.deleteLater()
        self.rows.remove(row)

    def clear(self):
        for row in self.rows:
            self.delete_row(row)

    def get_dataframe(self) -> pd.DataFrame:
        l = []
        for row in self.rows:
            l.append(row.get_dict())
        return pd.DataFrame(l)

    def set_stim_autocompleter(self, stimulus_list: list):
        autocompleter = QtWidgets.QCompleter(stimulus_list)
        for row in self.rows:
            row.name.setCompleter(autocompleter)

