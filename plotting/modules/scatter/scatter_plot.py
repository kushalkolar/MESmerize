#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ...variants.pgscatter import ScatterPlot
from ...old.window import PlotWindow
from ...old.beeswarms_window import ControlWidget
from ...datapoint_tracer import DatapointTracerWidget
from uuid import UUID
import numpy as np
import pandas as pd
import traceback


class ScatterPlotWidget(PlotWindow):
    def __init__(self, parent=None):
        super(ScatterPlotWidget, self).__init__(parent)
        self.setWindowTitle('Scatter Plot')
        #
        # self.ui.groupBoxSpecific.setLayout(QtWidgets.QVBoxLayout())
        # self.control_widget = ControlWidget(self.ui.groupBoxSpecific)
        # self.ui.groupBoxSpecific.layout().addWidget(self.control_widget)

        self.ui.label_group.setText('Color based on:')
        self.ui.listWidgetDataColumns.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_plot_tab('Scatter_Plot')

        self.current_datapoint = None

        self.scatter_plot = ScatterPlot(graphics_view=self.graphicsViews['Scatter_Plot'])

        self.scatter_plot.signal_spot_clicked.connect(self.set_current_datapoint)

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.ui.actionLive_datapoint_tracer.triggered.connect(self.live_datapoint_tracer.show)

        self.ui.comboBoxShape.show()
        self.ui.labelShapesBasedOn.show()

    @QtCore.pyqtSlot(UUID)
    def set_current_datapoint(self, identifier: UUID):
        self.current_datapoint = identifier
        r = self.dataframe[self.dataframe[self.uuid_column] == identifier]

        block_id = r._BLOCK_.item()
        h = self.merged_transmission.history_trace.get_data_block_history(block_id)

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=h)

    def update_plot(self):
        self.scatter_plot.clear()

        accepted_datatypes = [np.ndarray]

        if not self.data_types_check(accepted_datatypes):
            QtWidgets.QMessageBox.warning(self, 'Invalid data type in data column',
                                          'The data column can only contain the following data types: np.ndarray')
            return

        s = self.dataframes[self.data_column]
        try:
            data = np.vstack(s)
        except:
            QtWidgets.QMessageBox.warning(self, 'Exception while stacking data column',
                                          'The following exception was raised.' + traceback.format_exc())
            return
        # try:

        colors = self.auto_colormap(len(self.groups))

        shapes = {0: 'o', 1: 's', 2: 't', 3: 'd', 4: '+'}

        # labels_list = []

        # for numerical_label, group_name in self.groups:
        #     labels_list += [numerical_label] * self.dataframe[self.grouping_column].value_counts()[group_name]

        df = pd.DataFrame(data, columns=['x', 'y'])
        df[self.grouping_column] = self.dataframe[self.grouping_column]
        df['uuid'] = self.dataframe[self.uuid_column]

        for ix, label in enumerate(set(self.groups)):
            xs = df[df[self.grouping_column] == label]['x']
            ys = df[df[self.grouping_column] == label]['y']

            us = df[df[self.grouping_column] == label]['uuid']

            self.scatter_plot.add_data(xs, ys, uuid_series=us, color=colors[ix], symbol=shapes[ix])
        # except:
        #     QtWidgets.QMessageBox.warning(self, 'Improper input data for scatter plot. '
        #                                         'The data in the selected data column should form a 2D array. '
        #                                         'The following exception was raised: ' + traceback.format_exc())
        #     return


