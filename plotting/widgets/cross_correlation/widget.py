#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from .compute_cc import compute_cc_data, CC_Data
from .control_widget import Ui_CrossCorrelationControls
from .. import HeatmapSplitterWidget
from ...variants import TimeseriesPlot
from analysis.data_types import Transmission
from analysis.math import cross_correlation as cc_funcs
import numpy as np
from pyqtgraphCore import PlotDataItem


class ControlWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_CrossCorrelationControls()
        self.ui.setupUi(self)


class CrossCorrelationWidget(HeatmapSplitterWidget):
    def __init__(self):
        HeatmapSplitterWidget.__init__(self, highlight_mode='item')
        self.control_widget = ControlWidget()
        # self.cross_corr_layout = QtWidgets.QVBoxLayout()
        self.add_to_splitter(self.control_widget)

        self.cross_corr_plot = TimeseriesPlot()
        self.control_widget.ui.verticalLayoutLeftMain.addWidget(self.cross_corr_plot)

        self.current_sample_id = None
        self.control_widget.ui.listWidgetSampleID.currentItemChanged.connect(self.set_current_sample)

        # self.main_dataframe = None
        self.transmission = None
        self.sample_list = None
        self.cc_data = None

        self.plot_widget.sig_selection_changed.connect(self.set_lineplots)

        self.curve_plot_1 = PlotDataItem()
        self.curve_plot_2 = PlotDataItem()

        self.control_widget.ui.graphicsViewCurve1.addItem(self.curve_plot_1)
        self.control_widget.ui.graphicsViewCurve2.addItem(self.curve_plot_2)

        self.control_widget.ui.pushButtonComputeAllData.clicked.connect(self.compute_dataframe)

        self.control_widget.ui.radioButtonMaxima.clicked.connect(self.set_heatmap)
        self.control_widget.ui.radioButtonLag.clicked.connect(self.set_heatmap)

    def set_heatmap(self):
        sample_id = self.current_sample_id
        # sample_df = self.main_dataframe[self.main_dataframe.SampleID == sample_id]

        # self.data = np.vstack(sample_df[self.data_column].values)

        if self.control_widget.ui.radioButtonLag.isChecked():
            plot_data = self.cc_data[sample_id].lag_matrix
            cmap = 'brg'

        elif self.control_widget.ui.radioButtonMaxima.isChecked():
            plot_data = self.cc_data[sample_id].epsilon_matrix
            cmap = 'jet'

        self.plot_widget.set(plot_data, cmap=cmap)

        # self.set_data(sample_df, data_column=self.data_column, labels_column=self.labels_column,
        #               cmap=self.cmap, transmission=self.transmission)

    def set_lineplots(self, indices):
        if self.plot_widget.selector.multi_select_mode:
            nccs = []
            for ix in self.plot_widget.selector.multi_selection_list:
                # x = self.data[ix[0]]
                # y = self.data[ix[1]]
                i = ix[0]
                j = ix[1]
                nccs.append(self.cc_data[self.current_sample_id].ccs[i, j, :])

            if len(nccs) < 1:
                return

            a = np.vstack(nccs)

            self.curve_plot_1.clear()
            self.curve_plot_2.clear()

            self.cross_corr_plot.set(a)
        else:
            x = self.curve_data[indices[0]]
            y = self.curve_data[indices[1]]

            self.curve_plot_1.clear()
            self.curve_plot_2.clear()

            self.curve_plot_1.setData(x)
            self.curve_plot_2.setData(y)

            ncc = cc_funcs.ncc_c(x, y)

            self.cross_corr_plot.set_single_line(ncc)

    def set_input(self, transmission: Transmission = None):
        self.transmission = transmission
        self.transmission.df.reset_index(drop=True, inplace=True)
        # self.main_dataframe = self.transmission.df

        self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.addItems(self.transmission.df.columns)

        self.reset_sample_id_list_widget()
        self.control_widget.ui.listWidgetSampleID.setCurrentRow(0)

    def reset_sample_id_list_widget(self):
        self.sample_list = self.transmission.df.SampleID.unique().tolist()
        self.control_widget.ui.listWidgetSampleID.clear()
        self.control_widget.ui.listWidgetSampleID.addItems(self.sample_list)

    def set_current_sample(self):
        if self.cc_data is None:
            return
        ix = self.control_widget.ui.listWidgetSampleID.currentRow()
        self.current_sample_id = self.sample_list[ix]
        self.curve_data = np.vstack(self.transmission.df[self.transmission.df.SampleID == self.current_sample_id][self.data_column].values)
        self.set_heatmap()

    def compute_dataframe(self):
        self.data_column = self.control_widget.ui.comboBoxDataColumn.currentText()

        self.cc_data = dict.fromkeys(self.sample_list)

        for sample_id in self.sample_list:
            data = np.vstack(self.transmission.df[self.transmission.df.SampleID == sample_id][self.data_column].values)
            self.cc_data[sample_id] = compute_cc_data(data)
