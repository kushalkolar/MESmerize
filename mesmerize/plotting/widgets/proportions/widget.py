#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from PyQt5 import QtWidgets
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.console import ConsoleWidget
from ....pyqtgraphCore.widgets.ComboBox import ComboBox
from ....analysis import Transmission, organize_dataframe_columns, get_proportions
from math import sqrt
from ..base import BasePlotWidget
from ....common.qdialogs import *
from ....common.configuration import console_history_path
from ...utils import auto_colormap, ColormapListWidget
from seaborn import heatmap
import os
from matplotlib.axes import Axes


class ProportionsWidget(BasePlotWidget, MatplotlibWidget):
    drop_opts = ['xs', 'ys']  #: Drop the 'xs' and 'ys' since they are pd.Series objects and not required for restoring the plot

    def __init__(self):
        super().__init__()
        self.message_label = QtWidgets.QLabel()
        self.message_label.setText('')
        self.message_label.setMaximumHeight(30)
        self.vbox.addWidget(self.message_label)

        self.checkbox_update_live = QtWidgets.QCheckBox(self)
        self.checkbox_update_live.setText('Live update from flowchart')
        self.checkbox_update_live.setChecked(True)
        self.checkbox_update_live.toggled.connect(self.set_update_live)
        self.vbox.addWidget(self.checkbox_update_live)

        xs_label = QtWidgets.QLabel(self)
        xs_label.setText('X column')
        xs_label.setMaximumHeight(30)
        self.vbox.addWidget(xs_label)

        self.xs_combo = ComboBox(self)
        self.xs_combo.currentIndexChanged.connect(lambda: self.update_plot())
        self.xs_combo.setMaximumHeight(30)
        self.vbox.addWidget(self.xs_combo)

        ys_label = QtWidgets.QLabel(self)
        ys_label.setText('Y column')
        ys_label.setMaximumHeight(30)
        self.vbox.addWidget(ys_label)

        self.ys_combo = ComboBox(self)
        self.ys_combo.setMaximumHeight(30)
        self.ys_combo.currentTextChanged.connect(lambda: self.update_plot())
        self.vbox.addWidget(self.ys_combo)

        self.checkbox_percent = QtWidgets.QCheckBox(self)
        self.checkbox_percent.setText('Show percentages')
        self.checkbox_percent.setChecked(True)
        self.checkbox_percent.toggled.connect(lambda: self.update_plot())
        self.checkbox_percent.setMaximumHeight(30)
        self.vbox.addWidget(self.checkbox_percent)

        self.radio_barplot = QtWidgets.QRadioButton(self)
        self.radio_barplot.setText('bar plot')
        self.radio_barplot.setChecked(True)
        self.radio_barplot.toggled.connect(lambda: self.update_plot())
        self.radio_barplot.setMaximumHeight(30)

        self.radio_heatmap = QtWidgets.QRadioButton(self)
        self.radio_heatmap.setText('heatmap')
        self.radio_heatmap.toggled.connect(lambda: self.update_plot())
        self.radio_heatmap.toggled.connect(self.show_cmap_listwidget)

        hlayout_radios_btns = QtWidgets.QHBoxLayout()
        hlayout_radios_btns.addWidget(self.radio_barplot)
        hlayout_radios_btns.addWidget(self.radio_heatmap)
        self.vbox.addLayout(hlayout_radios_btns)

        self.cmap_label = QtWidgets.QLabel(self)
        self.cmap_label.setText('Colormap for heatmap')
        self.cmap_label.setMaximumHeight(30)
        self.cmap_label.hide()
        self.vbox.addWidget(self.cmap_label)

        self.cmap_listwidget = ColormapListWidget(self)
        self.cmap_listwidget.set_cmap('viridis')
        self.cmap_listwidget.currentRowChanged.connect(lambda: self.update_plot())
        self.cmap_listwidget.hide()
        self.cmap_listwidget.setMaximumHeight(100)
        self.vbox.addWidget(self.cmap_listwidget)

        hlayout2 = QtWidgets.QHBoxLayout()

        self.btn_update_plot = QtWidgets.QPushButton(self)
        self.btn_update_plot.setText('Update Plot')
        self.btn_update_plot.setMaximumHeight(30)
        self.btn_update_plot.clicked.connect(lambda: self.update_plot())
        hlayout2.addWidget(self.btn_update_plot)

        self.btn_swap_xy = QtWidgets.QPushButton(self)
        self.btn_swap_xy.setText('Swap X-Y')
        self.btn_swap_xy.clicked.connect(self.swap_x_y)
        self.btn_swap_xy.setMaximumHeight(30)
        hlayout2.addWidget(self.btn_swap_xy)

        self.vbox.addLayout(hlayout2)

        hlayout = QtWidgets.QHBoxLayout()

        btn_save = QtWidgets.QPushButton(self)
        btn_save.setText('Save')
        btn_save.clicked.connect(self.save_plot_dialog)
        btn_save.setMaximumHeight(30)
        hlayout.addWidget(btn_save)

        btn_load = QtWidgets.QPushButton(self)
        btn_load.setText('Load')
        btn_load.clicked.connect(self.open_plot_dialog)
        btn_load.setMaximumHeight(30)
        hlayout.addWidget(btn_load)

        self.vbox.addLayout(hlayout)

        hlayout3 = QtWidgets.QHBoxLayout()

        btn_export = QtWidgets.QPushButton(self)
        btn_export.setText('Export CSV')
        btn_export.clicked.connect(self.export)
        btn_export.setMaximumHeight(30)
        hlayout3.addWidget(btn_export)

        btn_show_console = QtWidgets.QPushButton(self)
        btn_show_console.setText('Show Console')
        btn_show_console.setCheckable(True)
        btn_show_console.setChecked(False)
        btn_show_console.setMaximumHeight(30)
        hlayout3.addWidget(btn_show_console)

        self.vbox.addLayout(hlayout3)

        ns = {'this': self,
              'get_fig': lambda: self.fig,
              'get_ax': lambda: self.ax,
              'get_dataframe': lambda: self.props_df,
              }

        txt = ["Namespaces",
               "self as 'this'",
               "get_fig() - get the current Figure instance",
               "get_ax() - get the current Axes instance",
               "get_dataframe() - get the current dataframe of proportions"
               ]

        txt = "\n".join(txt)

        cmd_history_file = os.path.join(console_history_path, 'proportions_plot.pik')

        self.console = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)
        self.console.setMaximumHeight(300)
        self.console.setVisible(False)

        self.vbox.addWidget(self.console)
        btn_show_console.toggled.connect(self.console.setVisible)

        spacer = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding)
        self.vbox.insertSpacerItem(0, spacer)

        self.props_df = None

        self.block_signals_list = [self.xs_combo, self.ys_combo, self.checkbox_percent, self.checkbox_update_live]

        self._ax = None

    @property
    def ax(self) -> Axes:
        """
        The Axes object for this plot

        :return: The Axes object for this plot
        :rtype: AXes
        """

        if self._ax is None:
            TypeError("Axes not set")

        return self._ax

    def show_cmap_listwidget(self, b: bool):
        self.cmap_label.setVisible(b)
        self.cmap_listwidget.setVisible(b)

    @BasePlotWidget.signal_blocker
    def set_update_live(self, b: bool):
        self.checkbox_update_live.setChecked(b)
        self.update_live = b

        if b:
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def swap_x_y(self, *args, **kwargs):
        """Swap the X and Y axes"""
        xs_opt = self.xs_combo.currentText()
        ys_opt = self.ys_combo.currentText()

        ix_x = self.xs_combo.findText(ys_opt)
        self.xs_combo.setCurrentIndex(ix_x)

        ix_y = self.ys_combo.findText(xs_opt)
        self.ys_combo.setCurrentIndex(ix_y)
        # self._block = False

        self.update_plot()

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        super(ProportionsWidget, self).set_input(transmission)
        if self.update_live:
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        # self.xs_combo.clear()
        self.xs_combo.setItems(categorical_columns)

        # self.ys_combo.clear()
        self.ys_combo.setItems(categorical_columns)

    def get_plot_opts(self, drop: bool = False):
        """
        Get the plot options

        :param drop: Drop the 'xs' and 'ys' objects when saving the returned dict for saving to an hdf5 file
        """
        xs_name = self.xs_combo.currentText()
        ys_name = self.ys_combo.currentText()

        opts = dict(xs_name=xs_name, ys_name=ys_name,
                    xs=self.transmission.df[xs_name],
                    ys=self.transmission.df[ys_name],
                    percentages=self.checkbox_percent.isChecked(),
                    use_barplot=self.radio_barplot.isChecked(),
                    use_heatmap=self.radio_heatmap.isChecked(),
                    heatmap_cmap=self.cmap_listwidget.current_cmap
                    )
        if drop:
            for k in self.drop_opts:
                opts.pop(k)
        return opts

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        """Set the plot options"""
        ix_x = self.xs_combo.findText(opts['xs_name'])
        self.xs_combo.setCurrentIndex(ix_x)

        ix_y = self.ys_combo.findText(opts['ys_name'])
        self.ys_combo.setCurrentIndex(ix_y)

        self.checkbox_percent.setChecked(opts['percentages'])

        try:
            self.radio_barplot.setChecked(opts['use_barplot'])
            self.radio_heatmap.setChecked(opts['use_heatmap'])
            self.cmap_listwidget.set_cmap(opts['heatmap_cmap'])
        except:
            pass

    @present_exceptions('Plot error', 'Cannot plot, make sure you have selected appropriate data columns')
    def update_plot(self):
        """
        Update the plot data and draw
        """
        # self.ax.cla()
        self.fig.clear()
        self._ax = self.fig.add_subplot(111)  #: The axis that is used for this plot

        opts = self.get_plot_opts()
        use_barplot = opts.pop('use_barplot')
        use_heatmap = opts.pop('use_heatmap')
        heatmap_cmap = opts.pop('heatmap_cmap')

        if opts['xs_name'] == opts['ys_name']:
            self.message_label.setText('Must choose different X and Y columns')
            return
        self.message_label.clear()

        ys = self.transmission.df[opts['ys_name']]

        show_percents = opts['percentages']

        self.props_df = get_proportions(**opts)  #: DataFrame instance containing proportions data according to the plot parameters

        n_labels = len(ys.unique())

        if n_labels < 11:
            cmap = 'tab10'
        elif 10 < n_labels < 21:
            cmap = 'tab20'
        elif 20 < n_labels < 211:
            cmap = 'nipy_spectral'
        else:
            raise ValueError('Cannot generate colormap for greater than 210 labels.\n'
                             'Why would you have > 210 labels?')

        colors = auto_colormap(n_labels, cmap)

        if show_percents:
            label = 'percentages'
        else:
            label = 'raw counts'

        if use_barplot:
            self.props_df.plot(kind='bar', stacked=True, ax=self.ax, color=colors)
            self.ax.set_xlabel(opts['xs_name'])
            self.ax.set_ylabel(label)
            # self.fig.tight_layout()
            self.ax.legend(bbox_to_anchor=(0.0, 1.02, 1.0, 0.102), loc='upper center', ncol=int(sqrt(len(set(ys)))),
                           mode='expand')

        elif use_heatmap:
            props_df = self.props_df.fillna(value=0.)
            heatmap(props_df.T, ax=self.ax, cmap=heatmap_cmap, annot=True, fmt='.1f', cbar_kws={'label': label})
            self.fig.tight_layout()

        self.draw()
        self.toolbar.update()

    @present_exceptions('Export error', 'The following error occurred.')
    def export(self, *args, **kwargs):
        """Export as a csv file"""
        if self.props_df is None:
            return
        if self.transmission is None:
            return

        try:
            proj_path = self.transmission.get_proj_path()
        except ValueError:
            proj_path = ''

        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file as', proj_path, '(*.csv)')
        if path == '':
            return

        path = path[0]
        if not path.endswith('.csv'):
            path = f'{path}.csv'

        self.props_df.to_csv(path)
