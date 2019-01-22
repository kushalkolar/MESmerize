#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from plotting.old.window import PlotWindow
from plotting.old.beeswarms_window import ControlWidget
import numpy as np
from plotting.datapoint_tracer import DatapointTracerWidget
from plotting.variants.pgscatter import ScatterPlot
from uuid import UUID
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from pyqtgraphCore.functions import mkBrush
import pandas as pd


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

        self.scatter_plot = ScatterPlot(graphics_view=self.graphicsViews['LDA_Projection'])

        self.scatter_plot.signal_spot_clicked.connect(self.set_current_datapoint)

        self.control_widget.btnTraceDatapoint.clicked.connect(self.open_datapoint_tracer)
        self.datapoint_tracesr = []

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.ui.actionLive_datapoint_tracer.triggered.connect(self.live_datapoint_tracer.show)

        self._lda = None

    @property
    def lda(self) -> LinearDiscriminantAnalysis:
        return self._lda

    def get_current_datapoint(self) -> UUID:
        return self.current_datapoint

    @QtCore.pyqtSlot(UUID)
    def set_current_datapoint(self, identifier: UUID):
        self.current_datapoint = identifier

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              row=self.dataframe[self.dataframe[self.uuid_column] == identifier],
                                              history_trace=self.get_history_trace(identifier))

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

        self.targets = []

        for cl in self.lda.classes_:
            self.targets += [cl] * self.dataframe[self.grouping_column].value_counts()[cl]

        df = pd.DataFrame(self.transformed_data, columns=['x', 'y'])
        df['targets'] = self.dataframe[self.grouping_column]
        df['uuid'] =    self.dataframe[self.uuid_column]

        for ix, t in enumerate(set(self.targets)):
            xs = df[df.targets == t]['x']
            ys = df[df.targets == t]['y']

            us = df[df.targets == t]['uuid']

            self.scatter_plot.add_data(xs, ys, uuid_series=us, color=colors[ix])

    def transform_data(self):
        self._lda = LinearDiscriminantAnalysis(n_components=2)
        s = self.dataframe[self.data_column]
        data = np.vstack(s)
        x_lda = self._lda.fit_transform(data, self.dataframe[self.grouping_column])
        return x_lda

    def open_datapoint_tracer(self):
        identifier = self.get_current_datapoint()
        self.datapoint_tracers.append(DatapointTracerWidget())

        self.datapoint_tracers[-1].set_widget(datapoint_uuid=identifier,
                                              parent=self,
                                              row=self.dataframe[self.dataframe[self.uuid_column] == identifier],
                                              history_trace=self.get_history_trace(identifier),
                                              )
        self.datapoint_tracers[-1].show()

    def get_history_trace(self, identifier: UUID):
        return []
