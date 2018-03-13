#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 17:50:20 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
#from matplotlib import pyplot as pl
import os
import pyqtgraph as pg
from scipy import signal
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,800)
view = pg.GraphicsLayoutWidget()  ## GraphicsView with GraphicsLayout inserted by default
mw.setCentralWidget(view)
mw.show()
mw.setWindowTitle('pyqtgraph example: ScatterPlot')

## create four areas to add plots
w1 = view.addPlot()

df = pd.read_csv('/home/kushal/Sars_stuff/Riccardo_Ca_data/62.txt', sep='\t')

curve = df.R2[:880]
#fi = pl.figure(figsize=(16,7))
#pl.plot(curve)
#pl.show()
#pl.close()

b,a = signal.butter(2, (0.199)/0.5)
sig = signal.filtfilt(b, a, curve)
#fig1 = pl.figure(figsize=(16,7))
#pl.plot(sig)

pl = pg.PlotDataItem()
pl.setData(sig)
w1.addItem(pl)

#pl = pg.PlotDataItem()
#w = view.addPlot()
#view.addPlot(w)
#w.addItem(pl)
#mw.setCentralWidget(pl)
#pl.curve



s = pd.Series(sig)
s1 = np.gradient(sig)
s2 = np.gradient(s1)

signs = np.diff(np.sign(s1))

#peaks = pd.Series(np.sign(signs)).loc[(np.sign(signs)<0)]
peaks = np.where(signs < 0)[0]
bases = np.where(signs > 0)[0]
#bases = pd.Series(np.sign(signs)).loc[(np.sign(signs)>0)]
# sc = sc[50:]

#%%matplotlib inline
#fig = pl.figure(figsize=(16,7))
#ax1 = pl.subplot()
#ax1.plot(sig, "g")
#ax2 = pl.twinx(ax1)
# ax2.plot(s1, c = "r")
# ax2.plot([0,860], [0,0], c = "k", alpha = 0.5)
#ax2.scatter(sc.index, sig[sc.index], c='r')

#
#p2.scatter.setData(peaks.index, sig[peaks.index], pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(255, 0, 0, 125))
#peaks_plot = pg.PlotDataItem()
peaks_plot = pg.ScatterPlotItem(name = 'peaks', pen=None, symbol='o', size=10, brush=(255, 0, 0, 150))
peaks_plot.setData(peaks, np.take(sig, peaks))#, pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(255, 0, 0, 125))
w1.addItem(peaks_plot)
bases_plot = pg.ScatterPlotItem(name = 'bases', pen=None, symbol='o', size=10, brush=(0, 255, 0, 150))
bases_plot.setData(bases, np.take(sig, bases))#, pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(0, 255, 0, 125))
w1.addItem(bases_plot)

lastClicked = []
def clicked(plot, points):
    global lastClicked
    for p in lastClicked:
        p.resetPen()
    print("clicked points", points)
    for p in points:
        p.setPen('b', width=3)
    lastClicked = points
    
peaks_plot.sigClicked.connect(clicked)
bases_plot.sigClicked.connect(clicked)

#ax2.scatter(peaks.index, sig[peaks.index], c='r')
#ax2.scatter(bases.index, sig[bases.index], c='b')
#pl.show()
#pl.close()