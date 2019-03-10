#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import seaborn as sns
from math import ceil


class ViolinsPlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        # sns.set()
        self.fig.subplots_adjust(hspace=0.3, wspace=0.3)
        self.num_columns = 4
        self.axes = []

    def set(self, sub_dataframe, data_columns: list, x_column: str, sub_group_column: str = None, x_order: list = None):
        self.axes = []
        self.fig.clear()

        num_rows = ceil(len(data_columns) / self.num_columns)

        for i, data_column in enumerate(data_columns):
            self.axes.append(self.fig.add_subplot(num_rows, self.num_columns, i + 1))
            sns.violinplot(x=x_column, y=data_column, hue=sub_group_column, order=x_order, palette='muted',
                                data=sub_dataframe[sub_dataframe[data_column].notna()], ax=self.axes[i])
        self.draw()
