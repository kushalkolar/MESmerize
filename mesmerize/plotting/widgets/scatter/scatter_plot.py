#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from ..base import BasePlotWidget
from ...variants import PgScatterPlot
from .control_widget import Ui_DockWidgetControls
from ....analysis import Transmission
from ....common.qdialogs import *
import numpy as np
from ....pyqtgraphCore import GraphicsLayoutWidget, mkBrush
from ....pyqtgraphCore.console import ConsoleWidget
from ...utils import get_colormap
from .. import DatapointTracerWidget
import os
from ....common.configuration import console_history_path
from ....common import get_project_manager
from uuid import UUID
import pandas as pd


class ControlDock(QtWidgets.QDockWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_DockWidgetControls()
        self.ui.setupUi(self)

        self.ui.listWidgetColormap.set_cmap('tab10')

        # signals for live updates
        self.ui.comboBoxDataColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxXColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxYColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.radioButtonDataColumn.toggled.connect(self.sig_changed.emit)
        self.ui.radioButtonXY.toggled.connect(self.sig_changed.emit)
        self.ui.checkBoxLogX.toggled.connect(self.sig_changed.emit)
        self.ui.checkBoxLogY.toggled.connect(self.sig_changed.emit)
        self.ui.comboBoxColorsColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.listWidgetColormap.currentRowChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxShapesColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxUUIDColumn.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.comboBoxDPTCurve.currentTextChanged.connect(self.sig_changed.emit)
        self.ui.spinBoxSpotSize.valueChanged.connect(self.sig_changed.emit)
        self.ui.doubleSpinBoxAlpha.valueChanged.connect(self.sig_changed.emit)

        self.data_controls = [self.ui.comboBoxDataColumn, self.ui.comboBoxXColumn, self.ui.comboBoxYColumn, self.ui.comboBoxDPTCurve]
        self.categorial_controls = [self.ui.comboBoxColorsColumn, self.ui.comboBoxShapesColumn]
        self.uuid_controls = [self.ui.comboBoxUUIDColumn]

    def set_combo_box(self, comboBox: QtWidgets.QComboBox, text: str):
        ix = comboBox.findText(text)
        comboBox.setCurrentIndex(ix)

    def fill_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        # Set the selected options after filling the widget if they are present in the new lists
        p_dcol = self.ui.comboBoxDataColumn.currentText()
        p_xcol = self.ui.comboBoxXColumn.currentText()
        p_ycol = self.ui.comboBoxYColumn.currentText()
        p_colors_col = self.ui.comboBoxColorsColumn.currentText()
        p_shape_col = self.ui.comboBoxShapesColumn.currentText()
        p_ucol = self.ui.comboBoxUUIDColumn.currentText()

        for cb in self.data_controls:
            cb.clear()
            cb.addItems(data_columns)

        if p_dcol in data_columns:
            self.set_combo_box(self.ui.comboBoxDataColumn, p_dcol)
            self.set_combo_box(self.ui.comboBoxXColumn, p_xcol)
            self.set_combo_box(self.ui.comboBoxYColumn, p_ycol)

        for cb in self.categorial_controls:
            cb.clear()
            cb.addItem('------------')
            cb.addItems(categorical_columns)

        if p_colors_col in categorical_columns:
            self.set_combo_box(self.ui.comboBoxColorsColumn, p_colors_col)

        if p_shape_col in self.categorial_controls:
            self.set_combo_box(self.ui.comboBoxShapesColumn, p_shape_col)

        for cb in self.uuid_controls:
            cb.clear()
            cb.addItems(uuid_columns)

        if p_ucol in uuid_columns:
            self.set_combo_box(self.ui.comboBoxUUIDColumn, p_ucol)


class CentralWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.graphics_view = GraphicsLayoutWidget()
        self.plot_variant = PgScatterPlot(self.graphics_view)  #: Instance of :ref:`PgScatterPlot <API_Variant_PgScatterPlot>` which is the actual plot area
        # self.setCentralWidget(self.graphics_view)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.graphics_view)

        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setMaximumHeight(32)

        self.vlayout.addWidget(self.status_label)

        self.setLayout(self.vlayout)


class ScatterPlotWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)
        self.setWindowTitle('Scatter Plot')

        self.central_widget = CentralWidget(self)
        self.plot_variant: PgScatterPlot = self.central_widget.plot_variant  #: the plot variant used for the actual plot area.
        self.graphics_view = self.central_widget.graphics_view
        self.status_label = self.central_widget.status_label
        self.status_label.mousePressEvent = self.show_exception_info

        self.setCentralWidget(self.central_widget)

        self.exception_holder = None  #: Used for holding exceptions that can be viewed by clicking on self.status_label

        self.control_widget = ControlDock(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_widget)
        self.control_widget.sig_changed.connect(self.update_plot)
        self.control_widget.ui.pushButtonUpdatePlot.clicked.connect(lambda: self.update_plot())

        self.block_signals_list = [self.control_widget]

        self.plot_opts = None

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot_dialog)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

        self.update_live = self.control_widget.ui.checkBoxLiveUpdateFromFlowchart.isChecked()
        self.control_widget.ui.checkBoxLiveUpdateFromFlowchart.toggled.connect(self.set_update_live)

        self.live_datapoint_tracer = DatapointTracerWidget()  #: Instance of :ref:`DatapointTracer <API_DatapointTracer>`
        self.plot_variant.signal_spot_clicked.connect(self.set_current_datapoint)

        self.dockDatapointTracer = QtWidgets.QDockWidget(self)
        self.dockDatapointTracer.setWindowTitle('Datapoint Tracer')
        self.dockDatapointTracer.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockDatapointTracer.setWidget(self.live_datapoint_tracer)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockDatapointTracer)

        cmd_history_file = os.path.join(console_history_path, 'scatter_plot.pik')

        ns = {'this': self,
              'plot_variant': self.plot_variant,
              'plot_item': self.plot_variant.plot
              }

        txt = ["Namespaces",
               "self as 'this'",
               "plot_variant as 'plot_variant'",
               "plot_variant.plot as 'plot_item'"
               ]

        txt = "\n".join(txt)

        self.console = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)

        self.dockConsole = QtWidgets.QDockWidget(self)
        self.dockConsole.setWindowTitle('Console')
        self.dockConsole.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockConsole)

    def set_update_live(self, b: bool):
        self.control_widget.ui.checkBoxLiveUpdateFromFlowchart.setChecked(b)
        self.update_live = b

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        """Set the input transmission"""
        if (self._transmission is None) or self.update_live:
            super(ScatterPlotWidget, self).set_input(transmission)
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, **kwargs):
        self.control_widget.fill_widget(**kwargs)

    def get_plot_opts(self, drop: bool = False) -> dict:
        """
         Get the plot options

         :param drop: no drop opts are specified for this plot
         """
        d = {'data_column': self.control_widget.ui.comboBoxDataColumn.currentText(),
             'data_column_radio': self.control_widget.ui.radioButtonDataColumn.isChecked(),
             'x_column': self.control_widget.ui.comboBoxXColumn.currentText(),
             'y_column': self.control_widget.ui.comboBoxYColumn.currentText(),
             'log_x': self.control_widget.ui.checkBoxLogX.isChecked(),
             'log_y': self.control_widget.ui.checkBoxLogY.isChecked(),
             'xy_radio': self.control_widget.ui.radioButtonXY.isChecked(),
             'colors_column': self.control_widget.ui.comboBoxColorsColumn.currentText(),
             'cmap': self.control_widget.ui.listWidgetColormap.current_cmap,
             'shapes_column': self.control_widget.ui.comboBoxShapesColumn.currentText(),
             'uuid_column': self.control_widget.ui.comboBoxUUIDColumn.currentText(),
             'dpt_curve_column': self.control_widget.ui.comboBoxDPTCurve.currentText(),
             'spot_size': self.control_widget.ui.spinBoxSpotSize.value(),
             'spot_alpha': self.control_widget.ui.doubleSpinBoxAlpha.value()
             }

        if drop:
            for k in self.drop_opts:
                d.pop(k)

        return d

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        """Set all plot options from a dict"""
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxDataColumn, opts['data_column'])
        self.control_widget.ui.radioButtonDataColumn.setChecked(opts['data_column_radio'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxXColumn, opts['x_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxYColumn, opts['y_column'])
        self.control_widget.ui.radioButtonXY.setChecked(opts['xy_radio'])

        self.control_widget.ui.checkBoxLogX.setChecked(opts['log_x'])
        self.control_widget.ui.checkBoxLogY.setChecked(opts['log_y'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxColorsColumn, opts['colors_column'])
        self.control_widget.ui.listWidgetColormap.set_cmap(opts['cmap'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxShapesColumn, opts['shapes_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxUUIDColumn, opts['uuid_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxDPTCurve, opts['dpt_curve_column'])
        self.control_widget.ui.spinBoxSpotSize.setValue(opts['spot_size'])
        self.control_widget.ui.doubleSpinBoxAlpha.setValue(opts['spot_alpha'])

    @exceptions_label('status_label', 'exception_holder', 'Error while setting data', 'Make sure you have selected appropriate columns')
    def update_plot(self):
        """Update the plot data and draw"""

        self.exception_holder = None
        self.status_label.clear()

        self.plot_opts = self.get_plot_opts()

        if self.plot_opts['data_column_radio']:
            data_column = self.plot_opts['data_column']
            data = np.vstack(self.transmission.df[data_column].values)

            if data.shape[1] != 2:
                raise ValueError('Size of arrays in data column must equal 2')
            xs = data[:, 0]
            ys = data[:, 1]

        elif self.plot_opts['xy_radio']:
            xs = self.transmission.df[self.plot_opts['x_column']].values
            ys = self.transmission.df[self.plot_opts['y_column']].values

            if xs.ndim > 1:
                raise ValueError('X Column must contain single values, not arrays')
            if ys.ndim > 1:
                raise ValueError('Y Column must contain single values, not arrays')

        else:
            raise ValueError('Must choose either Data Column or X & Y option')

        self.plot_variant.clear()

        if self.plot_opts['log_x']:
            xs = np.log10(xs)
        if self.plot_opts['log_y']:
            ys = np.log10(ys)

        if self.plot_opts['colors_column'] != '------------':
            colors_map = get_colormap(self.transmission.df[self.plot_opts['colors_column']],
                                       self.plot_opts['cmap'], output='pyqt', alpha=self.plot_opts['spot_alpha'])

            colors = list(map(colors_map.get, self.transmission.df[self.plot_opts['colors_column']]))
            brushes_list = list(map(mkBrush, colors))
        else:
            colors_map = None
            brushes_list = 'r'

        if self.plot_opts['shapes_column'] != '------------':
            shapes = ['o', 's', 't', 'd', '+']
            shapes_labels = self.transmission.df[self.plot_opts['shapes_column']].unique()
            if len(shapes_labels) > len(shapes):
                raise ValueError('Too many labels to set different shapes')
            shapes_map = dict(zip(shapes_labels, shapes))

            shapes_list = list(map(shapes_map.get, self.transmission.df[self.plot_opts['shapes_column']]))
        else:
            shapes_map = None
            shapes_list = 'o'

        self.plot_variant.add_data(xs, ys, self.transmission.df[self.plot_opts['uuid_column']], color=brushes_list,
                                   size=self.plot_opts['spot_size'], symbol=shapes_list)

        if colors_map is not None:
            self.plot_variant.set_legend(colors_map, shapes_map)

    def set_current_datapoint(self, identifier: UUID):
        """Set the UUID of the current datapoint and update the Datapoint Tracer"""
        self.current_datapoint = identifier
        u = str(self.current_datapoint)

        uuid_column = self.plot_opts['uuid_column']

        r = self.transmission.df[self.transmission.df[uuid_column] == u]
        dpt_col = self.plot_opts['dpt_curve_column']

        db_id = r['_BLOCK_']
        if isinstance(db_id, pd.Series):
            db_id = db_id.item()
        ht = self.transmission.history_trace.get_data_block_history(db_id)

        self.live_datapoint_tracer.set_widget(u, dpt_col, row=r, proj_path=get_project_manager().root_dir,
                                              history_trace=ht)

    def show_exception_info(self, mouse_press_ev):
        if self.exception_holder is not None:
            QtWidgets.QMessageBox.warning(self, *self.exception_holder)
