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
from ... import DatapointTracerWidget
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
        for cb in self.data_controls:
            cb.clear()
            cb.addItems(data_columns)

        for cb in self.categorial_controls:
            cb.clear()
            cb.addItem('------------')
            cb.addItems(categorical_columns)

        for cb in self.uuid_controls:
            cb.clear()
            cb.addItems(uuid_columns)


class ScatterPlotWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)
        self.setWindowTitle('Scatter Plot')

        self.graphics_view = GraphicsLayoutWidget()
        self.plot_variant = PgScatterPlot(self.graphics_view)
        # self.view_box.addItem(self.plot_variant)
        self.setCentralWidget(self.graphics_view)

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

        self.live_datapoint_tracer = DatapointTracerWidget()
        self.plot_variant.signal_spot_clicked.connect(self.set_current_datapoint)

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
        super(ScatterPlotWidget, self).set_input(transmission)
        if self.update__live:
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, **kwargs):
        self.control_widget.fill_widget(**kwargs)

    def get_plot_opts(self, drop: bool = False) -> dict:
        d = {'data_column': self.control_widget.ui.comboBoxDataColumn.currentText(),
             'data_column_radio': self.control_widget.ui.radioButtonDataColumn.isChecked(),
             'x_column': self.control_widget.ui.comboBoxXColumn.currentText(),
             'y_column': self.control_widget.ui.comboBoxYColumn.currentText(),
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
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxDataColumn, opts['data_column'])
        self.control_widget.ui.radioButtonDataColumn.setChecked(opts['data_column_radio'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxXColumn, opts['x_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxYColumn, opts['y_column'])
        self.control_widget.ui.radioButtonXY.setChecked(opts['xy_radio'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxColorsColumn, opts['colors_column'])
        self.control_widget.ui.listWidgetColormap.set_cmap(opts['cmap'])

        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxShapesColumn, opts['shapes_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxUUIDColumn, opts['uuid_column'])
        self.control_widget.set_combo_box(self.control_widget.ui.comboBoxDPTCurve, opts['dpt_curve_column'])
        self.control_widget.ui.spinBoxSpotSize.setValue(opts['spot_size'])
        self.control_widget.ui.doubleSpinBoxAlpha.setValue(opts['spot_alpha'])

    @present_exceptions('Error while plotting the data', 'Make sure you have selected appropriate columns')
    def update_plot(self):
        self.plot_opts = self.get_plot_opts()

        if self.plot_opts['data_column_radio']:
            data_column = self.plot_opts['data_column']
            data = np.vstack(self.transmission.df[data_column].values)

            if data.shape[1] != 2:
                raise ValueError('Size of arrays in data column must equal 2')
            xs = data[:, 0]
            ys = data[:, 1]

        elif self.plot_opts['xy_radio']:
            xs = np.vstack(self.transmission.df[self.plot_opts['x_column']])
            ys = np.vstack(self.transmission.df[self.plot_opts['y_column']])

            if xs.ndim != 1:
                raise ValueError('X Column must contain single values, not arrays')
            if ys.ndim != 1:
                raise ValueError('Y Column must contain single values, not arrays')

        else:
            raise ValueError('Must choose either Data Column or X & Y option')

        self.plot_variant.clear()

        if self.plot_opts['colors_column'] != '------------':
            colors_map = get_colormap(self.transmission.df[self.plot_opts['colors_column']],
                                       self.plot_opts['cmap'], output='pyqt')
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

    def set_current_datapoint(self, u: UUID):
        u = str(UUID)

        r = self.transmission.df[self.transmission.df[self.control_widget.ui.comboBoxUUIDColumn.currentText()] == u]
        dpt_col = self.control_widget.ui.comboBoxDPTCurve.currentText()

        ht = r._BLOCK_
        if isinstance(ht, pd.Series):
            ht = ht.item()

        self.live_datapoint_tracer.set_widget(u, dpt_col, row=r, proj_path=get_project_manager().root_dir,
                                              history_trace=ht)