#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 28 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
sys.path.append('..')
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
if __name__ != '__main__':
    from .pytemplates.pca_window_pytemplate import *
    from . import data_types
    from common import configuration
else:
    from pytemplates.pca_window_pytemplate import *
    import DataTypes
    from MesmerizeCore import configuration

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from mpl_toolkits.mplot3d import Axes3D
import seaborn
from pyqtgraphCore.console import ConsoleWidget
import pickle
import scipy
import os
from matplotlib import cm
from matplotlib import animation
import traceback


class PCA_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_PCA_Window()
        self.ui.setupUi(self)

        self.plot_widget = MatplotlibWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
        self.plot_widget.setSizePolicy(sizePolicy)
        self.ui.gridLayout.addWidget(self.plot_widget, 2, 0, 1, 7)

        self.ui.btnPlot.clicked.connect(lambda: self.update_pca(True))
        self.ui.comboBoxTarget.currentIndexChanged.connect(self.set_targets)
        self.ui.comboBoxLog.currentIndexChanged.connect(lambda: self.update_pca(False))
        self.ui.sliderMaxFreqIndex.sliderReleased.connect(lambda: self.update_pca(False))
        self.ui.spinBoxTrimStart.valueChanged.connect(lambda: self.update_pca(False))
        self.ui.comboBoxDataColumn.currentIndexChanged.connect(lambda: self.update_pca(False))

        ns = {'np': np,
              'pickle': pickle,
              'scipy': scipy,
              'pd': pd,
              'DataTypes': data_types,
              'main': self,
              'animation': animation
              }

        txt = "Namespaces:\n" \
              "pickle as pickle\n" \
              "numpy as 'np'\n" \
              "scipy as 'scipy'\n" \
              "dt as 'DataTypes'\n" \
              "matplotlib.animation as animation" \
              "self as 'main'\n\n" \
              "plot is main.plot_widget\n" \

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/pca_window.pik'

        self.ui.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))
        self.ui.dockConsole.setVisible(False)
        self.setWindowTitle('PCA')

    def update_input(self, transmissions):
        dfs = []
        for t in transmissions:
            dfs.append(t.df)

        self.df = pd.concat(dfs)

        columns = [self.ui.comboBoxDataColumn.itemText(i)
                   for i in range(self.ui.comboBoxDataColumn.count())]

        if list(self.df.columns) != columns:
            self.ui.comboBoxDataColumn.clear()
            self.ui.comboBoxDataColumn.addItems(self.df.columns)
            self.ui.comboBoxTarget.clear()
            self.ui.comboBoxTarget.addItems(self.df.columns)

        self.set_targets()

    def set_targets(self):
        target_column = self.ui.comboBoxTarget.currentText()
        targets_str_list = list(self.df[target_column])

        try:
            self.targets_str = sorted(list(set(targets_str_list)))
            self.ui.labelTargetColumn.setText('Target Column')
            self.ui.labelTargetColumn.setStyleSheet('color: black')
        except TypeError:
            self._block = True
            self.ui.labelTargetColumn.setText('Target Column - INVALID')
            self.ui.labelTargetColumn.setStyleSheet('color: red')
            return

        self.number_of_targets = len(self.targets_str)

        mapping = dict([(t_str, t_int + 1)
                        for t_int, t_str in enumerate(self.targets_str)])

        self.targets = [mapping[t] for t in targets_str_list]

        if self.ui.checkBoxLiveUpdate.isChecked():
            self.update_pca(True)

    def update_pca(self, ev):
        if (ev is False) and (self.ui.checkBoxLiveUpdate.isChecked() is False):
            return

        if self.df is None:
            return

        print('PLOTTING PCA!!')
        log_option = self.ui.comboBoxLog.currentText()
        end_freq = self.ui.sliderMaxFreqIndex.value()
        start_trim = self.ui.spinBoxTrimStart.value()
        data_column = self.ui.comboBoxDataColumn.currentText()

        self.ui.centralwidget.setEnabled(False)

        try:
            arrays = np.vstack(self.df[data_column].values)[:, start_trim:end_freq]
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Invalid Data Column?', 'Error while trying to stack arrays for PCA. '
                                                                        'Probably an invalid data column choice.\n' +
                                          str(e))
            self.ui.centralwidget.setEnabled(True)
            return


        self.setStatusTip('Fitting your data, please wait')
        try:
            if log_option == 'log2':
                data = np.log(arrays)
            elif log_option == 'log10':
                data = np.load(arrays)
            else:
                data = arrays

            pca = PCA(end_freq - start_trim)
            pca.fit_transform(data)
        except Exception:
            QtWidgets.QMessageBox.warning(self, 'Could not fit PCA',
                                          'The following error occured while trying to fit the data:\n' +
                                          traceback.format_exc())
            self.ui.centralwidget.setEnabled(True)
            return

        self.setStatusTip('Preparing figure, please wait')
        try:
            self.plot_widget.fig.clear()
            self.plot_widget.canvas.draw()
            result = pd.DataFrame(pca.transform(data), columns=['PCA%i' % i
                                                                for i in range(end_freq - start_trim)])

            fig = self.plot_widget.fig
            ax = Axes3D(fig)
            self.plot_widget.ax = ax
            self.plot_widget.color_map = cm.get_cmap('jet', self.number_of_targets)
            self.plot_widget.ax_scatter = ax.scatter(result['PCA0'], result['PCA1'], result['PCA2'], c=self.targets, edgecolors='black',
                           cmap=self.plot_widget.color_map, s=300, alpha=0.65)

            # make simple, bare axis lines through space:
            xAxisLine = ((min(result['PCA0']), max(result['PCA0'])), (0, 0), (0, 0))
            ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'black')
            yAxisLine = ((0, 0), (min(result['PCA1']), max(result['PCA1'])), (0, 0))
            ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'black')
            zAxisLine = ((0, 0), (0, 0), (min(result['PCA2']), max(result['PCA2'])))
            ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'black')

            # fig.legend

            # color_bar = fig.colorbar(p, ticks=self.targets, orientation='vertical')
            # color_bar.ax.set_yticklabels(self.targets_str)

        except Exception:
            QtWidgets.QMessageBox.warning(self, 'Could not prepare the figure',
                                          'The following error occured while trying to prepare the figure:\n' +
                                          traceback.format_exc())
            self.ui.centralwidget.setEnabled(True)
            return

        self.setStatusTip('Canvas is drawing, please wait')
        try:
            self.plot_widget.canvas.draw()
            self.setStatusTip('Done drawing')
        except Exception:
            QtWidgets.QMessageBox.warning(self, 'Could not draw',
                                          'The following error occured while trying to draw:\n' +
                                          traceback.format_exc())

            self.ui.centralwidget.setEnabled(True)
            return

        self.ui.centralwidget.setEnabled(True)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = PCA_GUI()
    w.show()
    app.exec_()
