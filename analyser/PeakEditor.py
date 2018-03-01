#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu March 1 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import pyqtgraphCore as pg
import numpy as np
import pandas as pd

if __name__ == '__main__':
    from peak_base_editor_pytemplate import *
    from DataTypes import Transmission
else:
    from .peak_base_editor_pytemplate import *
    from .DataTypes import Transmission


class PBWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, trans_curves, trans_peaks_bases):
        # super().__init__()
        super(PBWindow, self).__init__()
        # Ui_MainWindow.__init__(self)
        self.setupUi(self)
        assert isinstance(trans_curves, Transmission)
        self.tc = trans_curves
        assert isinstance(trans_peaks_bases, Transmission)
        self.tpb = trans_peaks_bases.copy()
        self.listwIndices.addItems(list(map(str, [*range(self.tc.df.index.size)])))
        # self.plots = pg.PlotItem()
        # self.graphicsView.addItem(self.plots)
        self.listwIndices.currentItemChanged.connect(self._set_row)
        self.listwIndices.itemClicked.connect(self._set_row)
        self.sliderDotSize.valueChanged.connect(self._set_pens)

        self.brush_size = 12

    def _set_row(self):
        self.graphicsView.clear()
        self.c_plots = []
        self.s_plots = []
        ixs = [item.text() for item in self.listwIndices.selectedItems()]
        ixs = list(map(int, ixs))

        if len(ixs) == 0:
            return

        for ix in ixs:
            curve_plot = pg.PlotDataItem()
            curve = self.tc.df[self.tc.data_column].iloc[ix]
            curve_plot.setData(curve/min(curve))

            self.graphicsView.addItem(curve_plot)

            # peak_ixs = self.tpb.df[self.tpb.data_column].iloc[ix].index[self.tpb.df[self.tpb.data_column].iloc[ix]['label'] == 'peak'].tolist()

            peaks = self.tpb.df[self.tpb.data_column].iloc[ix]['event'][
                self.tpb.df[self.tpb.data_column].iloc[ix]['label'] == 'peak'].tolist()

            peaks_plot = pg.ScatterPlotItem(name='peaks', pen=None, symbol='o', size=self.brush_size, brush=(255, 0, 0, 150))
            peaks_plot.setData(peaks, np.take(curve, peaks)/min(curve))

            bases = self.tpb.df[self.tpb.data_column].iloc[ix]['event'][
                self.tpb.df[self.tpb.data_column].iloc[ix]['label'] == 'base'].tolist()

            bases_plot = pg.ScatterPlotItem(name='bases', pen=None, symbol='o', size=self.brush_size, brush=(0, 255, 0, 150))
            bases_plot.setData(bases, np.take(curve, bases)/min(curve))

            self.graphicsView.addItem(peaks_plot)
            self.s_plots.append(peaks_plot)
            self.graphicsView.addItem(bases_plot)
            self.s_plots.append(bases_plot)

        if len(ixs) == 1:
            self.lastClicked = []
            peaks_plot.sigClicked.connect(self._clicked)
            bases_plot.sigClicked.connect(self._clicked)

    def _clicked(self, plot, points):
        for p in self.lastClicked:
            p.resetPen()
        print("clicked points", points)
        for p in points:
            p.setPen('b', width=3)
        self.lastClicked = points

    def _set_pens(self, n):
        for plot in self.s_plots:
            plot.setSize(n)
            self.brush_size = n

    def updateAll(self, trans_curve, trans_peaks_bases):
        self.tpb = trans_peaks_bases.copy()
        self.tc = trans_curve
        self._set_row()

    def _getBases(self):
        pass

    def getData(self):
        return self.tpb


class workEnv():
    pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    r, t = Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_save_tranmission.trn')

    pbw = PBWindow(t.df['curve'], t.df['curve'])
    pbw.show()

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
