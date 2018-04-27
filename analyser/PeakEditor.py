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
from MesmerizeCore import misc_funcs

if __name__ == '__main__':
    from pytemplates.PeakEditor_pytemplate import *
    from DataTypes import Transmission
else:
    from .pytemplates.PeakEditor_pytemplate import *
    from .DataTypes import Transmission
    from .HistoryWidget import HistoryTreeWidget


class PBWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, trans_curves, trans_peaks_bases):
        # super().__init__()
        super(PBWindow, self).__init__()
        # Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Peak-Base editor')
        self.history_tree = HistoryTreeWidget()
        self.history_tree.fill_widget([trans_peaks_bases.src])
        self.update_transmission(trans_curves, trans_peaks_bases)
        self._reset_listw()
        self.listwIndices.currentItemChanged.connect(self._set_row)
        self.listwIndices.itemClicked.connect(self._set_row)
        self.sliderDotSize.valueChanged.connect(self._set_pens)
        self.dockWidget.setWidget(self.history_tree)
        self.brush_size = 12

    def update_transmission(self, trans_curves, trans_peaks_bases):
        assert isinstance(trans_curves, Transmission)

        if hasattr(self, 'tc'):
            if self.tc.df.index.size != trans_curves.df.index.size:
                self.tc = trans_curves
                self._reset_listw()

            elif self.tc != trans_curves:
                self.tc = trans_curves
                self._set_row()
        else:
            self.tc = trans_curves

        assert isinstance(trans_peaks_bases, Transmission)
        self.tpb = trans_peaks_bases.copy()
        self._set_row()
        self.history_tree.fill_widget([trans_peaks_bases.src])

    def _reset_listw(self):
        self.listwIndices.clear()
        self.listwIndices.addItems(list(map(str, [*range(self.tc.df.index.size)])))

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
            curve = self.tc.df['curve'].iloc[ix]
            # print('curve: ')
            # print(curve)
            # if curve is None:
            #     QtGui.QMessageBox.warning(None, 'Empty Curve')

            if min(curve) != 0:
                min_curve = min(curve)
            else:
                min_curve = 0.00000001

            curve_plot.setData(curve / min_curve)

            self.graphicsView.addItem(curve_plot)

            # peak_ixs = self.tpb.df[self.tpb.data_column].iloc[ix].index[self.tpb.df[self.tpb.data_column].iloc[ix]['label'] == 'peak'].tolist()
            try:
                # print(self.tpb.df['peaks_bases'].iloc[ix])
                peaks = self.tpb.df['peaks_bases'].iloc[ix]['event'][
                    self.tpb.df['peaks_bases'].iloc[ix]['label'] == 'peak'].tolist()

                peaks_plot = pg.ScatterPlotItem(name='peaks', pen=None, symbol='o', size=self.brush_size,
                                                brush=(255, 0, 0, 150))

                peaks_plot.setData(peaks, np.take(curve, peaks) / min_curve)

                bases = self.tpb.df['peaks_bases'].iloc[ix]['event'][
                    self.tpb.df['peaks_bases'].iloc[ix]['label'] == 'base'].tolist()

                bases_plot = pg.ScatterPlotItem(name='bases', pen=None, symbol='o', size=self.brush_size,
                                                brush=(0, 255, 0, 150))

                bases_plot.setData(bases, np.take(curve, bases) / min_curve)

                self.graphicsView.addItem(peaks_plot)
                self.s_plots.append(peaks_plot)
                self.graphicsView.addItem(bases_plot)
                self.s_plots.append(bases_plot)

            except Exception as e:
                if QtGui.QMessageBox.question(None, 'Error!', 'The curve probably contains no peaks.'
                                                                   'Exception:\n' + \
                        str(e) + '\n\nWould you like to view the DataFrame?',
                                              QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    pass
                return

        if len(ixs) == 1:
            self.lastClicked = []
            peaks_plot.sigClicked.connect(self._clicked)
            bases_plot.sigClicked.connect(self._clicked)

    def _set_next_row(self):
        pass

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
