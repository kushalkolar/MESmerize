#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import seaborn as sns
import matplotlib.pyplot as plt
from math import ceil


class ViolinsPlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self, size = (8,6), dpi=100)
#        self.fig.subplots_adjust(hspace=0.3, wspace=0.3)
        self.num_columns = 4
        self.axes = []

    def set(self, sub_dataframe, data_columns: list, x_column: str, sub_group_column: str = None, x_order: list = None, label_rotation: int = 45):
        self.axes = []
        self.fig.clear()

        num_rows = ceil(len(data_columns) / self.num_columns)

        for i, data_column in enumerate(data_columns):
            ax = self.fig.add_subplot(num_rows, self.num_columns, i + 1)
            self.axes.append(ax)
            sns.violinplot(x=x_column, y=data_column, hue=sub_group_column, order=x_order, palette='muted',
                                data=sub_dataframe[sub_dataframe[data_column].notna()], ax=self.axes[i])
            ax.set_xticklabels(x_order, rotation=label_rotation)
        self.fig.tight_layout()
        self.draw()

##Testing code
if __name__ == "__main__":
    import pandas as pd

    import sys
    from PyQt5 import QtWidgets
    iris = sns.load_dataset('iris')
    app = QtWidgets.QApplication([])
    v = ViolinsPlot()
    v.set(iris, [x for x in iris.columns if "species" not in x], "species", label_rotation=90)
    v.show()
    sys.exit(app.exec())