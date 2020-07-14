#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets, QtCore
from mesmerize import Transmission
from ..base import BasePlotWidget
from ....common.qdialogs import exceptions_label
from ....common.configuration import console_history_path
from ....pyqtgraphCore.console import ConsoleWidget
from typing import *
from uuid import UUID
from .control_widget import Ui_ControlWidget
from ..datapoint_tracer import DatapointTracerWidget
import os


class ControlDock(QtWidgets.QDockWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_ControlWidget()
        self.ui.setupUi(self)

        self.ui.listWidgetColormap.set_cmap('tab10')

        self.ui.listWidgetDataColumns.selectionChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxGroupBy.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.listWidgetColormap.currentRowChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxUUIDColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxDPTCurve.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.spinBoxSpotSize.valueChanged.connect(self.sig_changed.emit)

        self.data_controls = [self.ui.listWidgetDataColumns, self.ui.comboBoxDPTCurve]
        self.categorical_controls = [self.ui.comboBoxGroupBy]
        self.uuid_controls = [self.ui.comboBoxUUIDColumn]

    def fill_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        for w in self.data_controls:
            w.setItems(data_columns)

        for w in self.categorical_controls:
            w.setItems(categorical_columns)

        for w in self.uuid_controls:
            w.setItems(uuid_columns)

    def set_combo_box(self, comboBox: QtWidgets.QComboBox, text: str):
        ix = comboBox.findText(text)
        comboBox.setCurrentIndex(ix)


class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setMaximumHeight(32)
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.status_label)


class BeeswarmPlotWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)
        self.setWindowTitle('Beeswarm Plot')

        self.central_widget = CentralWidget(self)
        self.status_label = self.central_widget.status_label

        self.exception_holder = None

        self.control_widget = ControlDock(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_widget)
        # self.control_widget.sig_changed.connect(self.update_plot)

        # Update only when button is clicked since these plots can take a while to draw.
        self.control_widget.ui.pushButtonUpdatePlot.clicked.connect(self.update_plot)
        self.control_widget.ui.checkBoxLiveUpdateFromFlowchart.toggled.connect(self.set_update_live)

        self.block_signals_list = [self.control_widget]

        self.transmision_withhold = None

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.dockDatapointTracer = QtWidgets.QDockWidget(self)
        self.dockDatapointTracer.setWindowTitle('Datapoint Tracer')
        self.dockDatapointTracer.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockDatapointTracer.setWidget(self.live_datapoint_tracer)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockDatapointTracer)

        cmd_history_file = os.path.join(console_history_path, 'beeswarm_plot.pik')

    def set_update_live(self, b: bool):
        self.update_live = b
        self.control_widget.ui.checkBoxLiveUpdateFromFlowchart.setChecked(b)

        if b and (self.transmision_withhold is not None):
            self.set_input(self.transmision_withhold)  #: set the input that has been withheld

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        if (self.transmission is None) or self.update_live:
            super(BeeswarmPlotWidget, self).set_input(transmission)
            return

        else:  # hold the transmission in case the user clicks the update checkbox
            self.transmision_withhold = transmission

    def get_plot_opts(self, drop: bool = False) -> dict:
        d = {'data_columns': self.control_widget.ui.listWidgetDataColumns.getSelectedItems(),
             'group_by_column': self.control_widget.ui.comboBoxGroupBy.currentText(),
             'cmap': self.control_widget.ui.listWidgetColormap.current_cmap,
             'uuid_column': self.control_widget.ui.comboBoxUUIDColumn.currentText(),
             'dpt_curve_column': self.control_widget.ui.comboBoxDPTCurve.currentText(),
             'spot_size': self.control_widget.ui.spinBoxSpotSize.value()
             }

        return d

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        self.control_widget.ui.listWidgetDataColumns.setSelectedItems(opts['data_columns'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxGroupBy, opts['group_by_column'])
        self.control_widget.ui.listWidgetColormap.set_cmap(opts['cmap'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxUUIDColumn, opts['uuid_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxDPTCurve, opts['dpt_curve_column'])
        self.control_widget.ui.spinBoxSpotSize.setValue(opts['spot_size'])

    @exceptions_label('status_label', 'exception_holder', 'Error while setting data', 'Make sure you have selected approriate columns')
    def update_plot(self, *args, **kwargs):
        opts = self.get_plot_opts()
        self.plot_opts = opts

        data_columns = opts['data_columnns']

        # for col in data_columns:
        #     data =

    def set_current_datapoint(self, identifier: Union[UUID, str]):
        self.current_datapoint = identifier
        u = str(self.current_datapoint)

    def show_exception_info(self, mouse_ev):
        if self.exception_holder is not None:
            QtWidgets.QMessageBox.warning(self, *self.exception_holder)