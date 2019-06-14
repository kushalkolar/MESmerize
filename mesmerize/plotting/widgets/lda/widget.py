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
from ..beeswarms.widget import ControlWidget
# from plotting.old.beeswarms_window import ControlWidget
import numpy as np
from .. import DatapointTracerWidget
from ...variants import PgScatterPlot
from uuid import UUID
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
# from pyqtgraphCore.functions import mkBrush
# import pandas as pd
from .. import HeatmapTracerWidget
from ...variants import Heatmap


class LDAPlot(PlotWindow):
    def __init__(self, parent=None):
        super(LDAPlot, self).__init__(parent)
        self.setWindowTitle('LDA')

        # Setup the control widget. Pass the main control widget to the LDA specific control widget class as its parent so that LDA specific stuff is just added to it.
        self.ui.groupBoxSpecific.setLayout(QtWidgets.QVBoxLayout())
        self.control_widget = ControlWidget(self.ui.groupBoxSpecific)
        self.ui.groupBoxSpecific.layout().addWidget(self.control_widget)

        self.ui.label_group.setText('Target values based on:')
        self.ui.listWidgetDataColumns.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_plot_tab('LDA_Projection')

        self.current_datapoint = None

        self.scatter_plot = PgScatterPlot(graphics_view=self.graphicsViews['LDA_Projection'])

        self.scatter_plot.signal_spot_clicked.connect(self.set_current_datapoint)

        self.control_widget.btnTraceDatapoint.clicked.connect(self.open_datapoint_tracer)
        self.datapoint_tracers = []

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.ui.actionLive_datapoint_tracer.triggered.connect(self.live_datapoint_tracer.show)

        self._lda = None

        main_menu = self.menuBar()
        lda_menu = main_menu.addMenu('LDA')

        action_lda_decision_function = QtWidgets.QWidgetAction(self)
        action_lda_decision_function.setText('Get Decision Function')
        action_lda_decision_function.triggered.connect(self._get_decision_function)

        action_lda_coefficients = QtWidgets.QWidgetAction(self)
        action_lda_coefficients.setText('Get LDA Coefficients')
        action_lda_coefficients.triggered.connect(self._get_coefficients)

        action_lda_means = QtWidgets.QWidgetAction(self)
        action_lda_means.setText('Get LDA Means')
        action_lda_means.triggered.connect(self._get_lda_means)

        lda_menu.addAction(action_lda_decision_function)
        lda_menu.addAction(action_lda_coefficients)
        lda_menu.addAction(action_lda_means)

        self.decision_function_widget = None
        self.coefficients_widget = None
        self.lda_means_widget = None

    @property
    def lda(self) -> LinearDiscriminantAnalysis:
        return self._lda

    def get_current_datapoint(self) -> UUID:
        return self.current_datapoint

    @QtCore.pyqtSlot(UUID)
    def set_current_datapoint(self, identifier: UUID):
        self.current_datapoint = identifier
        r = self.dataframe[self.dataframe[self.uuid_column] == identifier]

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=self.merged_transmission.get_history_trace(identifier))

    def update_params(self):
        super(LDAPlot, self).update_params()
        spot_size = self.control_widget.horizontalSliderSpotSize.value()
        self.data_column = self.data_columns[0]
        self.update_plot()

    def update_plot(self):
        self.scatter_plot.clear()

        accepted_datatypes = [np.ndarray]

        if not self.data_types_check(accepted_datatypes):
            QtWidgets.QMessageBox.warning(self, 'Invalid data type in data column',
                                          'The data column can only contain the following data types: np.ndarray')
            return

        self.transformed_data = self.transform_data()

        colors = self.auto_colormap(len(self.groups))
        colors_list = []
        colors_map = {}
        for ix, lda_class in enumerate(self.lda.classes_):
            colors_map.update({lda_class: colors[ix]})
            colors_list += [colors[ix]] * self.dataframe[self.grouping_column].value_counts()[lda_class]

        us = self.dataframe[self.uuid_column]

        self.scatter_plot.add_data(self.transformed_data[:, 0], self.transformed_data[:, 1],
                                   uuid_series=us, color=colors_list)

        self.scatter_plot.set_legend(colors_map)

        # df = pd.DataFrame(self.transformed_data, columns=['x', 'y'])
        # df['targets'] = self.dataframe[self.grouping_column]
        # df['uuid'] =    self.dataframe[self.uuid_column]
        #
        # for ix, t in enumerate(set(self.targets)):
        #     xs = df[df.targets == t]['x']
        #     ys = df[df.targets == t]['y']
        #
        #     us = df[df.targets == t]['uuid']

        # self.scatter_plot.add_data(self.transformed_data[:,0], self.transformed_data[:,1],
        #                            uuid_series=us, color=colors[ix])

    def transform_data(self):
        self._lda = LinearDiscriminantAnalysis(n_components=2)
        s = self.dataframe[self.data_column]
        data = np.vstack(s)
        x_lda = self._lda.fit_transform(data, self.dataframe[self.grouping_column])
        return x_lda

    def open_datapoint_tracer(self):
        identifier = self.get_current_datapoint()
        self.datapoint_tracers.append(DatapointTracerWidget())

        r = self.dataframe[self.dataframe[self.uuid_column] == identifier]

        self.datapoint_tracers[-1].set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=self.get_history_trace(identifier),
                                              )
        self.datapoint_tracers[-1].show()

    def _get_decision_function(self):
        self.decision_function_widget = HeatmapTracerWidget()
        self.decision_function = self.lda.decision_function(np.vstack(self.dataframe[self.data_column]))
        for i, c in enumerate(self.lda.classes_):
            col_name = c + '__dec_func'
            self.dataframe[col_name] = self.decision_function[:, i]
        self.decision_function_widget.dataframe = self.dataframe
        self.decision_function_widget.plot_widget.set(self.decision_function, cmap='jet', xticklabels=self.lda.classes_)
        self.decision_function_widget.set_transmission(self.merged_transmission)
        self.decision_function_widget.show()

    def _get_coefficients(self):
        self.coefficients_widget = Heatmap()
        self.coefficients_widget.set(self.lda.coef_, cmap='jet', yticklabels=self.lda.classes_)
        self.coefficients_widget.show()

    def _get_lda_means(self):
        self.lda_means_widget = Heatmap()
        self.lda_means_widget.set(self.lda.means_, cmap='jet', yticklabels=self.lda.classes_)
        self.lda_means_widget.show()
