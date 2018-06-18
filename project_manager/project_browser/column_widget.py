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
from .pytemplates.column_pytemplate import Ui_column_template
from functools import partial
import pandas as pd
from numpy import int64, float64
# from common import configuration


class ColumnWidget(QtWidgets.QWidget, Ui_column_template):
    signal_apply_clicked = QtCore.pyqtSignal(dict)
    signal_sample_id = QtCore.pyqtSignal(str)

    def __init__(self, parent, tab_name, column_name, is_root=False):
        # super(ColumnWidget, self).__init__(parent)
        QtWidgets.QWidget.__init__(self, parent)
        # Ui_column_template.__init__(self)
        self.setupUi(self)

        self.tab_name = tab_name
        self.column_name = column_name

        self.btnApply.clicked.connect(partial(self.btn_apply_clicked_emit_dict, option=None))
        self.btnReset.clicked.connect(self.lineEdit.clear)

        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.itemSelectionChanged.connect(self.set_lineEdit)

        if self.column_name == 'SampleID':
            self.listWidget.itemDoubleClicked.connect(self.emit_sample_id)

        if not is_root:
            self.btnApply.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.btnApply.customContextMenuRequested.connect(self.btnApply_context_menu_requested)

            apply_all = QtWidgets.QWidgetAction(self)
            apply_all.setText('Apply all')
            apply_all.triggered.connect(partial(self.btn_apply_clicked_emit_dict, option='all'))

            apply_all_in_new_tab = QtWidgets.QWidgetAction(self)
            apply_all_in_new_tab.setText('Apply all in new tab')
            apply_all_in_new_tab.triggered.connect(partial(self.btn_apply_clicked_emit_dict, option='all_in_new'))


            apply_in_new_tab = QtWidgets.QWidgetAction(self)
            apply_in_new_tab.setText('Apply in new tab')
            apply_in_new_tab.triggered.connect(partial(self.btn_apply_clicked_emit_dict, option='new'))

            self.btnApplyMenu = QtWidgets.QMenu(self)
            self.btnApplyMenu.addAction(apply_all)
            self.btnApplyMenu.addAction(apply_all_in_new_tab)
            self.btnApplyMenu.addSeparator()
            self.btnApplyMenu.addAction(apply_in_new_tab)

        self.lineEdit.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.lineEdit.customContextMenuRequested.connect(self.lineEdit_context_menu_requested)

        lineEdit_view_all = QtWidgets.QWidgetAction(self)
        lineEdit_view_all.setText('...')
        lineEdit_view_all.triggered.connect(self.line_edit_view_all_in_text_browser)

        lineEditNegation = QtWidgets.QWidgetAction(self)
        lineEditNegation.setText('"Not" modifer')
        lineEditNegation.triggered.connect(self.set_not_modifier)

        self.lineEditMenu = QtWidgets.QMenu(self)
        self.lineEditMenu.addAction(lineEdit_view_all)
        self.lineEditMenu.addAction(lineEditNegation)

    @property
    def series(self) -> pd.Series:
        return self._series

    @series.setter
    def series(self, series: pd.Series):
        self._series = series
        if len(series) < 1:
            self.set_empty()
            return

        self.listWidget.clear()
        self.setEnabled(True)

        self.column_type = type(self.series[self.series.index.values.min()])
        self.labelColumnName.setText(self.column_name + '\n' + str(self.column_type))

        if self.column_type is str:
            self.set_as_str()
        elif self.column_type in [int, float, int64, float64]:
            self.set_as_num()
        elif self.column_type is list:
            self.set_as_list()
        elif self.column_type is bool:
            self.set_as_bool()
        else:
            self.set_as_unknown()

    def set_empty(self):
        self.listWidget.clear()
        self.listWidget.addItems(['Empty'])
        self.setDisabled(True)

    def btn_apply_clicked_emit_dict(self, option=None):
        d = {'column_widget': self, 'option': option}

        self.signal_apply_clicked.emit(d)
        print(d)

    def btnApply_context_menu_requested(self, p):
        self.btnApplyMenu.exec_(self.btnApply.mapToGlobal(p))

    def lineEdit_context_menu_requested(self, p):
        self.lineEditMenu.exec_(self.lineEdit.mapToGlobal(p))

    def line_edit_view_all_in_text_browser(self):
        pass

    def set_not_modifier(self):
        text = self.lineEdit.text()
        self.lineEdit.setText('$NOT:' + text)

    def set_as_str(self):
        self.listWidget.addItems(list(set(self.series)))

        lineEdit_exact_match = QtWidgets.QWidgetAction(self)
        lineEdit_exact_match.setText('Exact match')

    def set_as_num(self):
        self.listWidget.addItems([str(x) for x in set(self.series)])

        lineEdit_greater_than = QtWidgets.QWidgetAction(self)
        lineEdit_greater_than.setText('Greater than')
        lineEdit_greater_than.triggered.connect(partial(self.set_num_modifier, '$>:'))
        self.lineEditMenu.addAction(lineEdit_greater_than)

        lineEdit_less_than = QtWidgets.QWidgetAction(self)
        lineEdit_less_than.setText('Less than')
        lineEdit_less_than.triggered.connect(partial(self.set_num_modifier, '$<:'))

        self.lineEditMenu.addAction(lineEdit_less_than)

    def set_num_modifier(self, modifier):
        text = self.lineEdit.text()
        self.lineEdit.setText(modifier + text)

    def set_as_bool(self):
        pass

    def set_as_list(self):
        self.listWidget.addItems(list(set([a for b in self.series.tolist() for a in b])))

        lineEdit_exact_match = QtWidgets.QWidgetAction(self)
        lineEdit_exact_match.setText('Exact match')

    def set_as_unknown(self):
        self.listWidget.addItems(['Unsupported type'])
        self.setDisabled(True)

    def set_lineEdit(self):
        txt = ''
        for item in self.listWidget.selectedItems():
            txt = txt + '|' + item.text()
        txt = txt[1:]
        self.lineEdit.setText(txt)

    def emit_sample_id(self, item: QtWidgets.QListWidgetItem):
        self.signal_sample_id.emit(item.text())

    # def clear(self):
    #     self.listWidget.clear()
    #     self.listWidget.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    df = pd.read_pickle('/home/kushal/Sars_stuff/github-repos/testprojects/March 9/dataframes/root.mzp')

    c = ColumnWidget(parent=None, tab_name='bah_tab', column_name='Genotype', series=df['odor'])

    c.show()
    app.exec_()