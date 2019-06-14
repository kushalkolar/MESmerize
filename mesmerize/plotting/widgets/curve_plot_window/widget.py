#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
from ..plot_window import PlotWindow
from ...variants import PgCurvePlot
from numpy import ndarray


class CurvePlotWindow(PlotWindow):
    def __init__(self, parent=None):
        super(CurvePlotWindow, self).__init__(parent)
        self.setWindowTitle('Curves Plot Window')

        self.ui.comboBoxUUIDColumn.setDisabled(True)

        self.add_plot_tab('Curves')
        self.curve_plot = PgCurvePlot(self.graphicsViews['Curves'])
        self.legends = []

        self.plotting_tabs = {'Curves': self.curve_plot}

    def update_params(self):
        super(CurvePlotWindow, self).update_params()
        self.update_curve_plot()

    def update_curve_plot(self):
        for tab_ix in range(1, self.ui.tabWidget.count()):
            self.ui.tabWidget.removeTab(1)

        self.curve_plot.clear_plot()
        colors = self.auto_colormap(len(self.groups))
        errors = []

        accepted_datatypes = [ndarray]

        if not self.data_types_check(accepted_datatypes):
            return

        for plot_ix, data_column in enumerate(self.data_columns):

            msg = 'Progress: ' + \
                  str(((plot_ix + 1) / len(self.data_columns)) * 100) + ' % , Plotting data column: ' + data_column
            self.status_bar.showMessage(msg)

            self.curve_plot.add_plot(data_column)
            self.curve_plot.create_legend(plot_ix)

            for ii, (dataframe, group) in enumerate(zip(self.group_dataframes, self.groups)):
                self.status_bar.showMessage(msg + ', plotting group: ' + group)

                self.add_plot_tab(title=group)
                group_plot = PgCurvePlot(self.graphicsViews[group])
                self.plotting_tabs.update({group: group_plot})

                self.curve_plot.add_data_to_plot(plot_ix, data_series=dataframe[data_column],
                                                 name=group, color=colors[ii])

                rng = self.curve_plot.get_range(plot_ix)
                self.curve_plot.set_range(plot_ix, x_range=rng[0], y_range=rng[1])

                group_plot.add_plot(data_column)
                group_plot.add_data_to_plot(plot_ix, data_series=dataframe[data_column],
                                            name=group, color=colors[ii])
                group_plot.set_range(plot_ix, x_range=rng[0], y_range=rng[1])

        if len(errors) > 0:
            QtWidgets.QMessageBox.warning(self, 'Errors while plotting',
                                          'The following errors occured while plotting:\n' + '\n'.join(errors))
