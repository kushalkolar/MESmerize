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
sys.path.append('..')
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np
#
# if __name__ == '__main__':
#     from stim_plots_pytemplate import *
#     from stats_peak_plots_pytemplate import *
# else:
#     from stim_plots_pytemplate import *
#     from stats_peak_plots_pytemplate import *
#     # from stats_gui import StatsWindow
#
#
# class MPLW(MatplotlibWidget):
#     def __init__(self):
#         MatplotlibWidget.__init__(self)
#
# class Plots:
#     def __init__(self, curve_plot, violin_plot):
#         self.curve_plot = curve_plot
#         self.violin_plot = violin_plot
#
#     def setData(self, groups):
#         print(groups)
#         colors = ['b', 'g', 'r', 'c', 'm', 'y']
#         ci = 0
#         ax = self.curve_plot.fig.add_subplot(111)
#
#         for group in groups:
#             c = colors[ci]
#             for ix, r in group.df.iterrows():
#                 if (r['peak_curve'] is not None) and (len(r['peak_curve']) > 0):
#                     ax.plot(r['peak_curve']/min(r['peak_curve']), color=c)
#             ci +=1
#
#         self.curve_plot.canvas.draw()
#         # self.violin_plot.draw()
#
#     def setColor(self):
#         pass
#
#     def addGroup(self):
#         pass
#
#     def removeGroup(self):
#         pass
#
#
# class PlotInterface:
#     def __init__(self, parent):
#         assert isinstance(parent, StatsWindow)
#         self.stims = StimPlots()
#         parent.stim_plots_tab.layout().addWidget(self.stims)
#         self.peaks = PeakPlots()
#         parent.peak_plots_tab.layout().addWidget(self.peaks)
#
#         self.plots = [self.stims, self.peaks]
#
#     def set_data(self, df, group_dict):
#         for plot in self.plots:
#             plot.set_data(df, group_dict)
#
#     def set_colors(self):
#         pass
#
#
# class PeakPlots(QtWidgets.QWidget, Ui_stats_peak_plots_template):
#     def __init__(self, parent=None):
#         super(PeakPlots, self).__init__()
#         self.setupUi(self)
#
#     def set_data(self):
#         pass
#
#     def plot_all(self):
#         pass
#
#     def plot_overlaps(self):
#         pass
#
#     def plot_group_subplots(self):
#         pass
#
#     def plot_headmaps(self):
#         pass
#
#
# class StimPlots(QtWidgets.QWidget, Ui_stim_plots_template):
#     def __init__(self, parent=None):
#         super(StimPlots, self).__init__()
#         self.setupUi(self)
#
#     def set_data(self):
#         pass
#
#     def plot_all(self):
#         pass
#
#     def plot_overlaps(self):
#         pass
#
#     def plot_group_subplots(self):
#         pass
#
#     def plot_headmaps(self):
#         pass
#
#
# class ViolinPlots():
#     pass
#
#
# class BoxPlots():
#     pass
#
#
# class ParaCorPlots():
#     pass
#
#

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()