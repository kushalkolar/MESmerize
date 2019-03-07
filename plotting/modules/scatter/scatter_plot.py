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
        self.current_datapoint = str(identifier)
        r = self.dataframe[self.dataframe[self.uuid_column] == self.current_datapoint]
        print(r)
        if isinstance(r._BLOCK_, pd.Series):
            block_id = r._BLOCK_.item()
        elif isinstance(r._BLOCK_, str):
            block_id = r._BLOCK_

        h = self.merged_transmission.history_trace.get_data_block_history(block_id)

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=h)

    def update_params(self):
        super(ScatterPlotWidget, self).update_params()
        self.update_plot()

    def update_plot(self):
        self.scatter_plot.clear()

        accepted_datatypes = [np.ndarray]

        # if not self.data_types_check(accepted_datatypes):
        #     QtWidgets.QMessageBox.warning(self, 'Invalid data type in data column',
        #                                   'The data column can only contain the following data types: np.ndarray')
        #     return
        self.data_column = self.data_columns[0]
        s = self.dataframe[self.data_column]
        try:
            data = np.vstack(s)
        except:
            QtWidgets.QMessageBox.warning(self, 'Exception while stacking data column',
                                          'The following exception was raised.' + traceback.format_exc())
            return
        if data.shape[1] != 2:
            QtWidgets.QMessageBox.warning(self, 'Improper data column',

                                          'Data within the chosen Data column must form a 2D Array')
            return
        # if data.shape[1]
        # try:

        colors = self.auto_colormap(len(self.groups))

        colors_map = {}
        for i, c in enumerate(colors):
            colors_map.update({self.groups[i]: c})

        colors_series = self.dataframe[self.grouping_column].map(colors_map)

        shapes_map_ref = {0: 'o', 1: 's', 2: 't', 3: 'd', 4: '+'}

        shapes_column = list(set(self.ui.comboBoxShape.currentText()))

        shapes_series = self.dataframe[shapes_column]

        shapes_map = {}

        for i, s in enumerate(set(shapes_series.to_list)):
            shapes_map.update({s: shapes_map_ref[i]})

        shapes = shapes_series.map(shapes_map)

        us = self.dataframe[self.uuid_column]

        self.scatter_plot.add_data(data[:, 0], data[:, 1], uuid_series=us, color=colors_series, symbol=shapes)
        # except:
        #     QtWidgets.QMessageBox.warning(self, 'Improper input data for scatter plot. '
        #                                         'The data in the selected data column should form a 2D array. '
        #                                         'The following exception was raised: ' + traceback.format_exc())
        #     return


