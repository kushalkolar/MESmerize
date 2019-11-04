#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#@author: kushal

#Chatzigeorgiou Group
#Sars International Centre for Marine Molecular Biology

#GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

from ..base import BasePlotWidget
from ...utils import *
from ....pyqtgraphCore.widgets.ComboBox import ComboBox
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.console import ConsoleWidget
from ....common.configuration import console_history_path
from matplotlib.axes import Axes
from typing import *

class ControlDock(QtWidgets.QDockWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.vlayout = QtWidgets.QVBoxLayout()

        label_categorical_column = QtWidgets.QLabel(self)
        label_categorical_column.setText('Categorical Label')
        label_categorical_column.setMaximumHeight(30)
        self.vlayout.addWidget(label_categorical_column)

        self.combo_categorical_column = ComboBox(self)
        self.combo_categorical_column.setMaximumHeight(30)
        self.combo_categorical_column.currentTextChanged.connect(self.sig_changed)
        self.vlayout.addWidget(self.combo_categorical_column)

        self.cmap_label = QtWidgets.QLabel(self)
        self.cmap_label.setText('Colormap ')
        self.cmap_label.setMaximumHeight(30)
        self.cmap_label.hide()
        self.vlayout.addWidget(self.cmap_label)

        self.cmap_listwidget = ColormapListWidget(self)
        self.cmap_listwidget.set_cmap('tab10')
        self.cmap_listwidget.currentRowChanged.connect(self.sig_changed)
        self.cmap_listwidget.setMaximumHeight(150)
        self.vlayout.addWidget(self.cmap_listwidget)

        self.btn_update_plot = QtWidgets.QPushButton(self)
        self.btn_update_plot.setText('Update Plot')
        self.btn_update_plot.setMaximumHeight(30)
        self.btn_update_plot.clicked.connect(self.sig_changed)
        self.vlayout.addWidget(self.btn_update_plot)


class SpaceMapWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)

        self.setWindowTitle('Space Map Plot')

        self.plot_area = MatplotlibWidget()
        self.setCentralWidget(self.plot_area)

        self.control_widget = ControlDock(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_widget)
        self.control_widget.sig_changed.connect(self.update_plot)
        self.control_widget.ui.pushButtonUpdatePlot.clicked.connect(lambda: self.update_plot())

        cmd_history_file = os.path.join(console_history_path, 'space_map.pik')

        ns = {'this': self,
              'plot_area': self.plot_area,
              }

        txt = ["Namespaces",
               "self as 'this'",
               ]

        txt = "\n".join(txt)

        self.console = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)

        self.block_signals_list = [self.control_widget]


    @property
    def ax(self) -> Axes:
        """
        The Axes objects for this plot

        :return: The Axes object for this plot
        :rtype: AXes
        """

        if self._ax is None:
            TypeError("Axes not set")

        return self._ax

    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        pass

    def update_plot(self, *args, **kwargs):
        pass

    def set_update_live(self, b: bool):
        pass

    def get_plot_opts(self, drop: bool) -> dict:
        pass

    def set_plot_opts(self, opts: dict):
        pass
