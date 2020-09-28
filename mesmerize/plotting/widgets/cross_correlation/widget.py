#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from ....analysis.math.cross_correlation import compute_cc_data, CC_Data
from .control_widget_pytemplate import Ui_CrossCorrelationControls
from .. import HeatmapSplitterWidget
from ...variants import TimeseriesPlot
from ....analysis import Transmission, get_sampling_rate, get_array_size, organize_dataframe_columns
import numpy as np
from ....pyqtgraphCore import PlotDataItem, mkPen
from ..datapoint_tracer import DatapointTracerWidget, CNMFROI, ManualROI, mkColor
import pandas as pd
from ....common.qdialogs import *
from ....common.utils import HdfTools
from .stims import get_binary_stims


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

        self.plot_variant.sig_selection_changed.connect(self.set_lineplots)

        # self.plot_widget.ax_ylabel_bar.set_axis_on()
        # self.plot_widget.ax_heatmap.get_yaxis().set_visible(True)

        self.curve_plot_1 = PlotDataItem()
        self.curve_plot_2 = PlotDataItem()

        self.control_widget.ui.graphicsViewCurve1.addItem(self.curve_plot_1)
        self.control_widget.ui.graphicsViewCurve2.addItem(self.curve_plot_2)

        self.control_widget.ui.pushButtonComputeAllData.clicked.connect(self.compute_dataframe)
        self.control_widget.ui.pushButtonExportAllData.clicked.connect(self.export_data)

        self.control_widget.ui.radioButtonMaxima.clicked.connect(self.set_heatmap)
        self.control_widget.ui.radioButtonLag.clicked.connect(self.set_heatmap)
        self.control_widget.ui.doubleSpinBoxMaximaThreshold.valueChanged.connect(self.set_heatmap)
        self.control_widget.ui.doubleSpinBoxLagThreshold.valueChanged.connect(self.set_heatmap)
        self.datapoint_tracer = DatapointTracerWidget()

        self.stimulus_labels: List[str] = []

        self.roi_2 = None

    def set_heatmap(self):
        if self.cc_data is None:
            return
        
        sample_id = self.current_sample_id

        abs_val = self.control_widget.ui.checkBoxAbsoluteValue.isChecked()

        lt = self.control_widget.ui.doubleSpinBoxLagThreshold.value()
        mt = self.control_widget.ui.doubleSpinBoxMaximaThreshold.value()

        if self.control_widget.ui.radioButtonLag.isChecked():
            opt = 'lag'
            cmap = 'brg'

        elif self.control_widget.ui.radioButtonMaxima.isChecked():
            opt = 'maxima'
            cmap = 'jet'
        else:
            raise ValueError

        plot_data = self.cc_data[sample_id].get_threshold_matrix(matrix_type=opt, lag_thr=lt, max_thr=mt, lag_thr_abs=abs_val)

        sub_df = self.transmission.df[self.transmission.df['SampleID'] == sample_id]

        labels_col = self.control_widget.ui.comboBoxLabelsColumn.currentText()
        ylabels = sub_df[labels_col].tolist() + self.stimulus_labels

        # Since it's just same curve vs. same curves in the cc_matrix
        xlabels = ylabels
                                                                                     #  lines make large matrices hard to see
        self.plot_variant.set(plot_data, cmap=cmap, ylabels=ylabels, xlabels=xlabels)#, linewidths=.5, linecolor='k')
        # self.plot_widget.ax_ylabel_bar.set_axis_off()

        self.plot_variant.plot.ax_heatmap.set_xlabel('Curve 1, magenta')
        self.plot_variant.plot.ax_heatmap.set_ylabel('Curve 2, cyan')

        self.plot_variant.draw()

    def set_lineplots(self, indices):
        if self.plot_variant.selector.multi_select_mode:
            nccs = []
            for ix in self.plot_variant.selector.multi_selection_list:
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

            xticks = self._get_xticks_linspace(nccs[0])

            self.cross_corr_plot.set(a, xticks=xticks)
        else:
            i = indices[0]
            j = indices[1]
            x = self.cc_data[self.current_sample_id].input_data[i]
            y = self.cc_data[self.current_sample_id].input_data[j]
            # x = self.curve_data[i]
            # y = self.curve_data[j]

            self.curve_plot_1.clear()
            self.curve_plot_2.clear()

            sub_df = self.transmission.df[self.transmission.df.SampleID == self.current_sample_id].reset_index(drop=True)

            if i < sub_df.uuid_curve.size:
                ux = sub_df.uuid_curve.iloc[i]
            else:
                ux = False

            if j < sub_df.uuid_curve.size:
                uy = sub_df.uuid_curve.iloc[j]
            else:
                uy = False

            if ux:
                r = sub_df[sub_df.uuid_curve == ux]
                db_id = r._BLOCK_.item()

                self.datapoint_tracer.set_widget(
                    datapoint_uuid=ux, data_column_curve=self.data_column,
                    row=r, proj_path=self.transmission.get_proj_path(),
                    history_trace=self.transmission.history_trace.get_data_block_history(db_id),
                    roi_color='m'
                )
            self.datapoint_tracer.ui.graphicsViewPlot.clear()

            if uy:
                r2 = sub_df[sub_df.uuid_curve == uy]
                self.add_second_roi_to_datapoint_tracer(r2)

            if (ux or uy):
                self.datapoint_tracer.show()

            self.control_widget.ui.lineEditCurve1UUID.setText(ux if ux else '')
            self.control_widget.ui.lineEditCurve2UUID.setText(uy if uy else '')

            self.curve_plot_1.setData(x=np.linspace(0, (len(x) / self.sampling_rate), len(x)), y=x, pen=mkPen(color='m', width=2))
            self.curve_plot_2.setData(x=np.linspace(0, (len(y) / self.sampling_rate), len(y)), y=y, pen=mkPen(color='c', width=2))

            ncc = self.cc_data[self.current_sample_id].ccs[i, j, :]

            xticks = self._get_xticks_linspace(ncc)

            self.cross_corr_plot.set_single_line(x=xticks, y=ncc)
        self.cross_corr_plot.ax.set_xlabel("lag (seconds)")

    # TODO: Just simplify the datapoint_tracer to take in multiple ROIs
    def add_second_roi_to_datapoint_tracer(self, r: pd.Series):
        if isinstance(self.roi_2, (CNMFROI, ManualROI)):
            self.roi_2.remove_from_viewer()

        roi_state = r['ROI_State'].item()
        if isinstance(roi_state, pd.Series):
            roi_state = roi_state.item()

        if roi_state['roi_type'] == 'CNMFROI':
            self.roi_2 = CNMFROI.from_state(curve_plot_item=None, view_box=self.datapoint_tracer.view, state=roi_state)
            self.roi_2.get_roi_graphics_object().setBrush(mkColor('c'))

        elif roi_state['roi_type'] == 'ManualROI':
            self.roi_2 = ManualROI.from_state(curve_plot_item=None, view_box=self.datapoint_tracer.view, state=roi_state)

        if self.roi_2 is not None:
            self.roi_2.get_roi_graphics_object().setPen(mkColor('c'))
            self.roi_2.add_to_viewer()

    def _get_xticks_linspace(self, ncc) -> np.ndarray:
            m = ncc.size
            stop = ((m / 2) / self.sampling_rate)
            start = -stop
            return np.linspace(start, stop, m)

    def set_input(self, transmission: Transmission = None):
        self.transmission = transmission
        self.transmission.df.reset_index(drop=True, inplace=True)

        cols = self.transmission.df.columns
        dcols, ccols, ucols = organize_dataframe_columns(cols)

        self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.addItems(dcols)

        self.control_widget.ui.comboBoxLabelsColumn.clear()
        self.control_widget.ui.comboBoxLabelsColumn.addItems(ccols)

        self.control_widget.ui.comboBoxStimulusType.clear()
        self.control_widget.ui.comboBoxStimulusType.addItems(
            self.transmission.STIM_DEFS
        )

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
        labels_col = self.control_widget.ui.comboBoxLabelsColumn.currentText()

        self.cc_data = dict.fromkeys(self.sample_list)

        for sample_id in self.sample_list:
            sub_df = self.transmission.df[self.transmission.df.SampleID == sample_id]

            if self.transmission.STIM_DEFS:
                stim_type = self.control_widget.ui.comboBoxStimulusType.currentText()

                stim_df = sub_df.iloc[0].stim_maps[0][0][stim_type]
                index_size = sub_df[self.data_column].values[0].size

                binary_stims_array, stim_names = get_binary_stims(
                    stim_df=stim_df,
                    index_size=index_size,
                    start_offset=0,
                    end_offset=0
                )

            data = np.vstack(sub_df[self.data_column].values)

            # append the stimulus array too
            if self.transmission.STIM_DEFS:
                data = np.vstack([data, binary_stims_array])

            r = get_sampling_rate(self.transmission)
            self.sampling_rate = r

            self.cc_data[sample_id] = compute_cc_data(data)
            self.cc_data[sample_id].lag_matrix = np.true_divide(self.cc_data[sample_id].lag_matrix, r)
            self.cc_data[sample_id].curve_uuids = np.array(list(map(str, sub_df['uuid_curve'].values))) # convert all UUIDs to str representation

            labels = sub_df[labels_col].values.astype(np.unicode)

            if self.transmission.STIM_DEFS:
                self.cc_data[sample_id].labels = np.concatenate([labels, stim_names]).astype(np.unicode)
                self.stimulus_labels = stim_names
            else:
                self.cc_data[sample_id].labels = labels
                self.stimulus_labels = []

        self.set_current_sample()

    @use_save_file_dialog('Save file as', None, '.hdf5')
    @present_exceptions()
    def export_data(self, path, *args, **kwargs):
        HdfTools.save_dict(self.cc_data, path, group='cross_corr_data')
