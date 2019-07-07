#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on July 2, 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from PyQt5 import QtCore, QtGui, QtWidgets
# from pyqtgraphCore.widgets.ColorButton import ColorButton
import pandas as pd
from ...common import configuration, get_project_manager
from .stimmap_modules.page import Page
from .stimmap_modules.row import Row, ColorButton
from .stimulus_mapping import ModuleGUI# as StimulusMappingModuleGUI


class MesStimmapGUI(ModuleGUI):
    def __init__(self, parent, viewer):
        super(MesStimmapGUI, self).__init__(parent, viewer)
        self.ui.comboBoxShowTimelineChoice.setVisible(False)
        self.ui.label.setVisible(False)
        self.clear_all_tabs()
        self.ui.btnSetAllMaps.clicked.connect(self.set_all_voltage_mappings)
        self.voltage_mappings = None

    def add_stim_type(self, stim_type: str):
        self.ui.tabWidget.addTab(PageMes(parent=self, stim_type=stim_type), stim_type)
        self.tabs[stim_type] = self.ui.tabWidget.widget(self.ui.tabWidget.count() - 1)

    def get_all_stims_dataframes(self) -> dict:
        d = {}

        for ix in range(self.ui.tabWidget.count()):
            w = self.ui.tabWidget.widget(ix)
            assert isinstance(w, PageMes)
            stim_def = w.combobox_stim_defs.currentText()
            if stim_def != '':
                d[stim_def] = {'channel': self.ui.tabWidget.tabText(ix),
                               'dataframe': w.get_dataframe()}

        return d

    def set_all_voltage_mappings(self):
        self.voltage_mappings = self.get_all_stims_dataframes()

    def export_to_work_env(self):
        pass


class PageMes(Page):
    def __init__(self, parent, stim_type: str):
        super(PageMes, self).__init__(parent, stim_type)
        self.ui.comboBoxTimeUnits.setVisible(False)
        self.ui.btnAddRow.setVisible(False)
        self.ui.label.setVisible(False)

        label_stim_def = QtWidgets.QLabel()
        label_stim_def.setText('Choose Stimulus Type (from project config):')
        self.ui.verticalLayout.insertWidget(0, label_stim_def)

        self.combobox_stim_defs = QtWidgets.QComboBox()
        self.update_stim_defs_combobox()
        get_project_manager().signal_dataframe_changed.connect(self.update_stim_defs_combobox)
        self.ui.verticalLayout.insertWidget(1, self.combobox_stim_defs)

    def update_stim_defs_combobox(self):
        self.combobox_stim_defs.clear()
        self.combobox_stim_defs.addItems([''])
        stim_defs = configuration.proj_cfg.options('STIM_DEFS')
        stim_defs.sort()
        self.combobox_stim_defs.addItems(stim_defs)

    def add_row(self, pd_series=None):
        """
        :type pd_series: pd.Series
        :type pd_series: pd.Series
        """
        row = RowMes(pd_series)
        self.ui.verticalLayout.insertLayout(self.ui.verticalLayout.count() - 1, row.hlayout)
        self.rows.append(row)


class RowMes(QtWidgets.QWidget):
    def __init__(self, pd_series: pd.Series):
        QtWidgets.QWidget.__init__(self)

        self.hlayout = QtWidgets.QHBoxLayout()

        self.voltage_label = QtWidgets.QLabel(self)
        self.hlayout.addWidget(self.voltage_label)

        self.name = QtWidgets.QLineEdit(self)
        self.name.setPlaceholderText('Stimulus Name')
        self.hlayout.addWidget(self.name)

        self.color_btn = ColorButton(self)
        self.hlayout.addWidget(self.color_btn)

        if pd_series is not None:
            self.name.setText(pd_series['name'])
            self.color_btn.setColor(pd_series['color'])
            self.voltage_label.setText(pd_series['voltage'])

    def set_series(self, pd_series: pd.Series):
        self.name.setText(pd_series['name'].item())
        self.color_btn.setColor(pd_series['color'].item())
        self.voltage_label.setText(pd_series['voltage'].item())

    def get_dict(self) -> dict:
        d = {'voltage': self.voltage_label.text(),
             'name':    self.name.text(),
             'color':   self.color_btn.color()
             }
        return d

    # def delete(self):
    #     self.qlabel.deleteLater()
    #     self.name.deleteLater()
    #     self.start.deleteLater()
    #     self.end.deleteLater()
    #     self.btn_remove.deleteLater()
    #     self.color_btn.deleteLater()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ModuleGUI(parent=None, viewer=None)
    w.add_stim_type('bah test')
    w.add_stim_type('bah test2')
    w.show()
    app.exec_()