#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 8 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import sys
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np


class MPLW(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)


class Curves(MPLW):
    def plot(self):
        pass

    def set_color(self, ax):
        pass


class Violins(MPLW):
    def plot(self):
        pass


class Plots:
    def __init__(self, curve_plot, violin_plot):
        assert isinstance(curve_plot, Curves)
        assert isinstance(violin_plot, Violins)
        self.curve_plot = curve_plot
        self.violin_plot = violin_plot

    def setData(self, groups):
        print(groups)
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        ci = 0
        ax = self.curve_plot.fig.add_subplot(111)

        for group in groups:
            c = colors[ci]
            for ix, r in group.df.iterrows():
                if (r['peak_curve'] is not None) and (len(r['peak_curve']) > 0):
                    ax.plot(r['peak_curve']/min(r['peak_curve']), color=c)
            ci +=1

        self.curve_plot.canvas.draw()
        # self.violin_plot.draw()

    def setColor(self):
        pass

    def addGroup(self):
        pass

    def removeGroup(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    cw = Curves()
    cw.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()