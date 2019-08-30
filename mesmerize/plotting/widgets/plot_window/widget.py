#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
from typing import List, Any, Union

from PyQt5.QtGui import QColor

from .window_pytemplate import *
import pandas as pd
import pickle
import scipy
from ....pyqtgraphCore import GraphicsLayoutWidget, mkColor
from ....pyqtgraphCore.console import ConsoleWidget
from matplotlib import cm as matplotlib_color_map
import numpy as np
from ....analysis import Transmission, organize_dataframe_columns
from ....common import configuration
import os


class PlotWindow(QtWidgets.QMainWindow):
    # __metaclass__ = abc.ABCMeta
    signal_params_updated = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.transmissions = None
        self.merged_transmission = None
        self.dataframe = pd.DataFrame()
        self.data_columns = []
        self.data_columns_dtypes = []

        self.groups = []
        self.group_dataframes = []
        self.uuid_column = ''

        self.graphicsViews = {}

        self.ui.listWidgetDataColumns.setSortingEnabled(True)

        self.ui.btnApplyAll.clicked.connect(self.update_params)

        ns = {'np': np,
              'pickle': pickle,
              'scipy': scipy,
              'pd': pd,
              'graphicsViews': self.graphicsViews,
              'this': self,
              }

        txt = "Namespaces:\n" \
              "pickle as pickle\n" \
              "numpy as 'np'\n" \
              "scipy as 'scipy'\n" \
              "pd as pandas\n" \
              "graphicsViews (plot tabs) as graphicsViews\n" \
              "self as 'this'\n\n" \

        cmd_history_file = os.path.join(configuration.console_history_path, 'plot_window.pik')

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt, historyFile=cmd_history_file))

        self.ui.dockConsole.hide()

        self.ui.comboBoxShape.hide()
        self.ui.checkBoxUseDifferentShapes.hide()

        self.old_column_selection = {'group': None,
                                     'shape': None,
                                     'uuid': None
                                     }

    @property
    def status_bar(self) -> QtWidgets.QStatusBar:
        return self.statusBar()

    def set_old_selections(self):
        if self.old_column_selection['group'] is not None:
            ix = self.ui.comboBoxGrouping.findText(self.old_column_selection['group'])
            if ix != -1:
                self.ui.comboBoxGrouping.setCurrentIndex(ix)

        if self.old_column_selection['shape'] is not None:
            ix = self.ui.comboBoxShape.findText(self.old_column_selection['shape'])
            if ix != -1:
                self.ui.comboBoxShape.setCurrentIndex(ix)

        if self.old_column_selection['uuid'] is not None:
            ix = self.ui.comboBoxUUIDColumn.findText(self.old_column_selection['uuid'])
            if ix != -1:
                self.ui.comboBoxUUIDColumn.setCurrentIndex(ix)
        # if self.old_column_selection['data'] is not None:
        #     item = self.ui.listWidgetDataColumns.get(self.old_column_selection['data'], QtCore.Qt.MatchExactly).text()
        #     self.ui.listWidgetDataColumns.setSelection()

    def update_input_transmissions(self, transmissions: list):
        self.transmissions = transmissions

        dfs = [t.df for t in self.transmissions]

        self.dataframe = pd.concat(dfs)#, axis=1)
        self.dataframe.reset_index(drop=True, inplace=True)
        try:
            self.dataframe.drop(columns=['index'], inplace=True)
        except:
            pass
        #self.dataframe = self.dataframe.sample(n=100, axis=0)

        columns = self.dataframe.columns.tolist()

        columns.sort()

        self.merged_transmission = Transmission.merge(self.transmissions)

        dcols, ccols, ucols = organize_dataframe_columns(self.merged_transmission.df.columns)

        self.ui.listWidgetDataColumns.clear()
        self.ui.listWidgetDataColumns.addItems(dcols)

        self.ui.comboBoxGrouping.clear()
        self.ui.comboBoxGrouping.addItems(ccols)

        self.ui.comboBoxShape.clear()
        self.ui.comboBoxShape.addItems(ccols)

        self.ui.comboBoxDataPointTracerCurveColumn.clear()
        self.ui.comboBoxDataPointTracerCurveColumn.addItems(dcols)

        self.ui.comboBoxUUIDColumn.clear()
        self.ui.comboBoxUUIDColumn.addItems(ucols)
        # self.ui.comboBoxUUIDColumn.setCurrentIndex(columns.index(next(column for column in columns if 'uuid' in column)))

        self.set_old_selections()

    def add_plot_tab(self, title: str):
        self.graphicsViews.update({title: GraphicsLayoutWidget(parent=self.ui.tabWidget)})
        self.ui.tabWidget.addTab(self.graphicsViews[title], title)
        i = self.ui.tabWidget.count() - 1
        self.ui.tabWidget.widget(i).setLayout(QtWidgets.QVBoxLayout())

    def update_params(self):
        self.data_columns.clear()
        self.data_columns = [item.text() for item in self.ui.listWidgetDataColumns.selectedItems()]

        for col in self.data_columns:
            dtype = type(self.dataframe[col].iloc[0])
            if dtype is np.NaN:
                i = 0
                while dtype is np.NaN:
                    dtype = type(self.dataframe[col].iloc[i])
                    i += 1

            self.data_columns_dtypes.append(dtype)

        if self.ui.radioButtonGroupBySingleColumn.isChecked():
            self.grouping_column = self.ui.comboBoxGrouping.currentText()
            self.groups = list(set(self.dataframe[self.grouping_column].tolist()))
        else:
            return
        self.group_dataframes = [self.dataframe[self.dataframe[self.grouping_column] == group] for group in self.groups]
        self.shape_column = self.ui.comboBoxShape.currentText()
        self.uuid_column = self.ui.comboBoxUUIDColumn.currentText()

        self.datapoint_tracer_curve_column = self.ui.comboBoxDataPointTracerCurveColumn.currentText()

        self.old_column_selection['group'] = self.grouping_column
        self.old_column_selection['shape'] = self.shape_column
        self.old_column_selection['uuid'] = self.uuid_column

    def auto_colormap(self, number_of_colors: int, color_map: str = 'hsv') -> List[Union[QColor, Any]]:
        cm = matplotlib_color_map.get_cmap(color_map)
        cm._init()
        lut = (cm._lut * 255).view(np.ndarray)
        cm_ixs = np.linspace(0, 210, number_of_colors, dtype=int)

        colors = []
        for ix in range(number_of_colors):
            c = lut[cm_ixs[ix]]
            colors.append(mkColor(c))
        return colors

    def data_types_check(self, accepted_dtypes: list) -> bool:
        errors = []
        for data_column, data_dtype in zip(self.data_columns, self.data_columns_dtypes):
            if data_dtype not in accepted_dtypes:
                errors.append('Unsupported data type <' + str(data_dtype) + '> in data column: ' + data_column)

        if len(errors) > 0:
            QtWidgets.QMessageBox.warning(self, 'Datatype error',
                                          'You cannot use the following data columns:\n' + '\n'.join(errors))
            return False
        else:
            return True
