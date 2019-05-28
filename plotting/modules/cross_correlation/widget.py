#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from plotting.modules.cross_correlation.control_widget import Ui_CrossCorrelationControls
from plotting.modules.heatmap.widget import HeatmapSplitterWidget
from plotting.variants.timeseries import TimeseriesPlot
from analyser.DataTypes import Transmission
from analyser.math import cross_correlation as cc_funcs
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

        self.main_dataframe = None
        self.data = None
        self.transmission = None
        self._samples_list = None

        self.plot_widget.sig_selection_changed.connect(self.set_lineplots)

        self.curve_plot_1 = PlotDataItem()
        self.curve_plot_2 = PlotDataItem()

        self.control_widget.ui.graphicsViewCurve1.addItem(self.curve_plot_1)
        self.control_widget.ui.graphicsViewCurve2.addItem(self.curve_plot_2)

    def set_heatmap(self, sample_id: str):
        sample_df = self.main_dataframe[self.main_dataframe.SampleID == sample_id]

        self.data = np.vstack(sample_df[self.data_column].values)

        if self.control_widget.ui.radioButtonLag.isChecked():
            self.cc_data = cc_funcs.get_lag_matrix(self.data)
        elif self.control_widget.ui.radioButtonMaxima.isChecked():
            self.cc_data = cc_funcs.get_epsilon_matrix(self.data)

        self.plot_widget.set(self.cc_data, cmap=self.cmap)

        # self.set_data(sample_df, data_column=self.data_column, labels_column=self.labels_column,
        #               cmap=self.cmap, transmission=self.transmission)

    def set_lineplots(self, indices):
        if self.plot_widget.selector.multi_select_mode:
            nccs = []
            for ix in self.plot_widget.selector.multi_selection_list:
                x = self.data[ix[0]]
                y = self.data[ix[1]]
                nccs.append(cc_funcs.ncc_c(x, y))
            if len(nccs) < 1:
                return

            a = np.vstack(nccs)

            self.curve_plot_1.clear()
            self.curve_plot_2.clear()

            self.cross_corr_plot.set(a)
        else:
            x = self.data[indices[0]]
            y = self.data[indices[1]]

            self.curve_plot_1.clear()
            self.curve_plot_2.clear()

            self.curve_plot_1.setData(x)
            self.curve_plot_2.setData(y)

            ncc = cc_funcs.ncc_c(x, y)

            self.cross_corr_plot.set_single_line(ncc)

    def set(self, dataframes,
            data_column: str,
            cmap: str = 'brg',
            transmission: Transmission = None):

        df = self.merge_dataframes(dataframes)
        self.main_dataframe = df.reset_index(drop=True)

        self.data_column = data_column
        self.cmap = cmap
        self.transmission = transmission

        self.reset_sample_id_list_widget()
        self.control_widget.ui.listWidgetSampleID.setCurrentRow(0)

    def reset_sample_id_list_widget(self):
        self.control_widget.ui.listWidgetSampleID.clear()
        self._samples_list = self.main_dataframe.SampleID.unique().tolist()
        self.control_widget.ui.listWidgetSampleID.addItems(self._samples_list)

    def set_current_sample(self):
        ix = self.control_widget.ui.listWidgetSampleID.currentRow()

        self.current_sample_id = self._samples_list[ix]
        self.set_heatmap(self.current_sample_id)


if __name__ == '__main__':
    import pickle
    t = pickle.load(open('/home/kushal/Sars_stuff/mesmerize_toy_datasets/cesa_hnk1_raw_data.trn', 'rb'))
    df = t['df']

    df['_SPLICE_ARRAYS'] = df._RAW_CURVE.apply(lambda x: x[:2998])

    app = QtWidgets.QApplication([])
    w = CrossCorrelationWidget()
    w.set(dataframes=df, data_column='_SPLICE_ARRAYS', transmission=t)

    w.show()
    app.exec_()
