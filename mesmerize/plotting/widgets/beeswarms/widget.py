#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ..plot_window import PlotWindow
from .beeswarm_plot_controls_pytemplate import Ui_BeeswarmControls
from ...variants import BeeswarmPlot
from .. import DatapointTracerWidget
from ...variants import ViolinsPlot
import numpy as np
from uuid import UUID
import pandas as pd
from ....common.qdialogs import use_save_file_dialog, present_exceptions
import os


class SummaryStatsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout(self)

        self.text_widget = QtWidgets.QPlainTextEdit(self)
        self.text_widget.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.text_widget.setFont(font)
        self.vlayout.addWidget(self.text_widget)

        self.button_save = QtWidgets.QPushButton(self)
        self.button_save.setText("Save to file")
        self.button_save.clicked.connect(lambda: self.save_to_file())
        self.vlayout.addWidget(self.button_save)

        self.setLayout(self.vlayout)

        self.data: str = ''

    def clear(self):
        self.data = ''
        self.text_widget.clear()

    def set_data(self, s: str):
        self.clear()
        self.data = s
        self.text_widget.setPlainText(self.data)

    @use_save_file_dialog("Save summary stats file", ext='.stats')
    @present_exceptions()
    def save_to_file(self, path, *args):
        if not self.data:
            raise ValueError(
                "Summary stats are empty, nothing to save."
            )
        if os.path.isfile(path):
            raise FileExistsError(
                "A file with that name already exists, specify a different path"
            )

        with open(path, 'w') as f:
            f.write(self.data)


class ControlWidget(QtWidgets.QWidget, Ui_BeeswarmControls):
    signal_changed = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(ControlWidget, self).__init__(parent)  # parent)
        self.setupUi(parent)

    def apply_all_settings(self):
        data_columns = self.listWidgetDataColumns.selectedItems()
        if self.radioButtonGroupBySingleColumn.isChecked():
            if self.comboBoxGrouping.currentText() == '':
                QtWidgets.QMessageBox.warning(None, 'Invalid parameters', 'Invalid grouping option')
                return
            grouping = {'type': 'column', 'column_name': self.comboBoxGrouping.currentText()}

        elif self.radioButtonGroupByTransmissions.isChecked():
            grouping = {'type': 'transmissions'}

        else:
            QtWidgets.QMessageBox.warning(None, 'Invalid parameters', 'No grouping selected')
            return

        self.signal_changed.emit(data_columns, grouping)


class BeeswarmPlotWindow(PlotWindow):
    def __init__(self, parent=None):
        super(BeeswarmPlotWindow, self).__init__(parent)
        self.setWindowTitle('Beeswarm Plot Window')
        # self.plot_obj = BeeswarmPlot(self.ui.graphicsView, self)
        # self.plot_obj.signal_spot_clicked.connect(print)

        # Setup the control widget. Pass the main control widget to the Beeswarm specific control widget class as its parent so that beeswarm specific stuff is just added to it.
        self.ui.groupBoxSpecific.setLayout(QtWidgets.QVBoxLayout())
        self.control_widget = ControlWidget(self.ui.groupBoxSpecific)
        self.ui.groupBoxSpecific.layout().addWidget(self.control_widget)

        self.add_plot_tab('Beeswarm')
        self.beeswarm_plot = BeeswarmPlot(self.graphicsViews['Beeswarm'])
        # self.add_plot_tab('Violins')
        self.violins_plot = ViolinsPlot()
        self.ui.tabWidget.addTab(self.violins_plot, 'Violins')
        # self.ui.tabWidget.widget(1).setLayout(QtWidgets.QVBoxLayout())

        self.current_datapoint = None

        self.beeswarm_plot.signal_spot_clicked.connect(self.set_current_datapoint)

        # self.control_widget.btnTraceDatapoint.clicked.connect(self.open_datapoint_tracer)
        self.datapoint_tracers = []

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.ui.actionLive_datapoint_tracer.triggered.connect(self.live_datapoint_tracer.show)

        self.summary_stats_widget = SummaryStatsWidget(parent=None)
        self.control_widget.pushButtonSummaryStats.clicked.connect(
            self.summary_stats_widget.show
        )

    def get_current_datapoint(self) -> UUID:
        return self.current_datapoint

    @QtCore.pyqtSlot(UUID)
    def set_current_datapoint(self, identifier: UUID):
        self.current_datapoint = identifier

        tstart = None
        tend = None

        if '_pf_b_ix_l' in self.dataframe.columns:
            tstart = self.dataframe[self.dataframe[self.uuid_column] == str(identifier)]['_pf_b_ix_l']
            if isinstance(tstart, pd.Series):
                tstart = tstart.item()
        if '_pf_b_ix_r' in self.dataframe.columns:
            tend = self.dataframe[self.dataframe[self.uuid_column] == str(identifier)]['_pf_b_ix_r']
            if isinstance(tend, pd.Series):
                tend = tend.item()

        r = self.dataframe[self.dataframe[self.uuid_column] == str(identifier)]

        if isinstance(r._BLOCK_, pd.Series):
            block_id = r._BLOCK_.item()
        elif isinstance(r._BLOCK_, str):
            block_id = r._BLOCK_

        h = self.merged_transmission.history_trace.get_data_block_history(block_id)

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=h,
                                              tstart=tstart, tend=tend
                                              )

    def update_params(self):
        super(BeeswarmPlotWindow, self).update_params()
        spot_size = self.control_widget.horizontalSliderSpotSize.value()
        self.update_beeswarm()
        self.update_violins()

        summary_stats = self.dataframe.groupby(self.grouping_column).describe().unstack(1).to_string()
        self.summary_stats_widget.set_data(summary_stats)

    def update_beeswarm(self):
        self.beeswarm_plot.clear_plots()
        colors = self.auto_colormap(len(self.groups))

        colors_map = {}
        for ix, g in enumerate(self.groups):
            colors_map.update({g: colors[ix]})

        accepted_datatypes = [int, float, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32,
                              np.uint64, np.float16, np.float32, np.float64, np.uint64, np.float16, np.float32,
                              np.float64]

        if not self.data_types_check(accepted_datatypes):
            return

        for i, data_column in enumerate(self.data_columns):
            pr = int(((i + 1) / len(self.data_columns)) * 100)
            msg = f'Progress: {pr} % ,Plotting data column: {data_column}'
            self.status_bar.showMessage(msg)
            self.beeswarm_plot.add_plot(data_column)

            for ix, (dataframe, group) in enumerate(zip(self.group_dataframes, self.groups)):
                self.status_bar.showMessage(f'{msg}, plotting group: {group}')
                self.beeswarm_plot.add_data_to_plot(i, data_series=dataframe[data_column],
                                                    uuid_series=dataframe[self.uuid_column],
                                                    name=group, color=colors[ix])
        self.beeswarm_plot.set_legend(colors_map)

    def update_violins(self):
        cols = self.data_columns + [self.grouping_column]
        sub_df = self.dataframe.loc[:, cols]
        self.violins_plot.set(sub_df, x_column=self.grouping_column, data_columns=self.data_columns, x_order=self.groups)


    # def open_datapoint_tracer(self):
    #     identifier = self.get_current_datapoint()
    #     self.datapoint_tracers.append(DatapointTracerWidget())
    #
    #     r = self.dataframe[self.dataframe[self.uuid_column] == identifier]
    #
    #     self.datapoint_tracers[-1].set_widget(datapoint_uuid=identifier,
    #                                           data_column_curve=self.datapoint_tracer_curve_column,
    #                                           parent=self,
    #                                           row=r,
    #                                           proj_path=self.merged_transmission.get_proj_path(),
    #                                           history_trace=self.get_history_trace(identifier),
    #                                           )
    #     self.datapoint_tracers[-1].show()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bpw = BeeswarmPlotWindow()
    bpw.show()
    app.exec_()
