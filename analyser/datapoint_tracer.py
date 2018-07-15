#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .pytemplates.datapoint_tracer_pytemplate import *
from .HistoryWidget import HistoryTreeWidget
from uuid import UUID
import pandas as pd


class DatapointTracerWidget(QtWidgets.QWidget):
    def __init__(self, datapoint_uuid: UUID, row: pd.Series, history_trace: list, parent=None, peak_ix: int = None, tstart: int = None, tend: int = None):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_DatapointTracer()
        self.ui.setupUi(self)

        self.ui.labelUUID.setText(str(datapoint_uuid))

        self.history_widget = HistoryTreeWidget()
        self.history_widget.fill_widget(history_trace)
        self.ui.verticalLayout.addWidget(self.history_widget)

        row.reset_index(inplace=True)
        self.pandas_series_widget = PandasWidget(parent=self)
        self.pandas_series_widget.set_data(row)
        self.ui.verticalLayout.addWidget(self.pandas_series_widget)

        if (tstart is not None) and (tend is not None):
            pass

        if peak_ix is not None:
            pass


class PandasWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        vLayout = QtWidgets.QVBoxLayout(self)
        hLayout = QtWidgets.QHBoxLayout()
        self.pathLE = QtWidgets.QLineEdit(self)
        hLayout.addWidget(self.pathLE)
        vLayout.addLayout(hLayout)
        self.pandasTv = QtWidgets.QTableView(self)
        vLayout.addWidget(self.pandasTv)
        self.pandasTv.setSortingEnabled(True)

    def set_data(self, series: pd.Series):
        model = PandasModel(series)
        self.pandasTv.setModel(model)


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df = pd.Series(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()
