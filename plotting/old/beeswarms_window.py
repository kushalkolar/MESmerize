#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .window import *
from .pytemplates.beeswarm_plot_controls_pytemplate import Ui_BeeswarmControls
from .beeswarms import *
import numpy as np
from ..datapoint_tracer import DatapointTracerWidget


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
        self.add_plot_tab('Violins')

        self.current_datapoint = None

        self.beeswarm_plot.signal_spot_clicked.connect(self.set_current_datapoint)

        self.control_widget.btnTraceDatapoint.clicked.connect(self.open_datapoint_tracer)
        self.datapoint_tracers = []

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.ui.actionLive_datapoint_tracer.triggered.connect(self.live_datapoint_tracer.show)

    def get_current_datapoint(self) -> UUID:
        return self.current_datapoint

    @QtCore.pyqtSlot(UUID)
    def set_current_datapoint(self, identifier: UUID):
        self.current_datapoint = identifier

        tstart = None
        tend = None

        if '_pfeature_ix_base_left_abs' in self.dataframe.columns:
            tstart = self.dataframe[self.dataframe[self.uuid_column] == identifier]['_pfeature_ix_base_left_abs'].item()
        if '_pfeature_ix_base_right_abs' in self.dataframe.columns:
            tend = self.dataframe[self.dataframe[self.uuid_column] == identifier]['_pfeature_ix_base_right_abs'].item()

        r = self.dataframe[self.dataframe[self.uuid_column] == identifier]

        self.live_datapoint_tracer.set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=self.get_history_trace(identifier),
                                              tstart=tstart, tend=tend
                                              )

    def update_params(self):
        super(BeeswarmPlotWindow, self).update_params()
        spot_size = self.control_widget.horizontalSliderSpotSize.value()
        self.update_beeswarm()
        self.update_violins()

    def update_beeswarm(self):
        self.beeswarm_plot.clear_plots()
        colors = self.auto_colormap(len(self.groups))
        errors = []

        accepted_datatypes = [int, float, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32,
                              np.uint64, np.float16, np.float32, np.float64, np.uint64, np.float16, np.float32,
                              np.float64]

        if not self.data_types_check(accepted_datatypes):
            return

        for i, data_column in enumerate(self.data_columns):
            msg = 'Progress: ' + str(
                ((i + 1) / len(self.data_columns)) * 100) + ' % ,Plotting data column: ' + data_column
            self.status_bar.showMessage(msg)
            self.beeswarm_plot.add_plot(data_column)

            for ii, (dataframe, group) in enumerate(zip(self.group_dataframes, self.groups)):
                self.status_bar.showMessage(msg + ', plotting group: ' + group)
                self.beeswarm_plot.add_data_to_plot(i, data_series=dataframe[data_column],
                                                    uuid_series=dataframe[self.uuid_column],
                                                    name=group, color=colors[ii])

    def update_violins(self):
        pass

    def open_datapoint_tracer(self):
        identifier = self.get_current_datapoint()
        self.datapoint_tracers.append(DatapointTracerWidget())

        r = self.dataframe[self.dataframe[self.uuid_column] == identifier]

        self.datapoint_tracers[-1].set_widget(datapoint_uuid=identifier,
                                              data_column_curve=self.datapoint_tracer_curve_column,
                                              parent=self,
                                              row=r,
                                              proj_path=self.merged_transmission.get_proj_path(),
                                              history_trace=self.get_history_trace(identifier),
                                              )
        self.datapoint_tracers[-1].show()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bpw = BeeswarmPlotWindow()
    bpw.show()
    app.exec_()
