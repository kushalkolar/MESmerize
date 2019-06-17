# -*- coding: utf-8 -*-
"""
Created on July 7 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .template import *
import numpy as np
from ...variants import TimeseriesPlot
from ....analysis import Transmission
from ....analysis.math.sosd import get_residuals
import traceback


class SOSD_Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.plot = TimeseriesPlot()
        groupBoxPlot_layout = QtWidgets.QVBoxLayout(self.ui.groupBoxPlot)
        groupBoxPlot_layout.addWidget(self.plot)

        self.transmission = None
        self.residuals = None

        self.ui.pushButtonStart.clicked.connect(self._compute_residuals)

    def set_input(self, transmission: Transmission):
        if not isinstance(transmission, Transmission):
            raise TypeError('Input must be an instance of Transmission')

        self.transmission = transmission
        cols = self.transmission.df.columns.tolist()
        cols.sort()

        self.ui.comboBoxDataColumn.clear()
        self.ui.comboBoxDataColumn.addItems(cols)

    def _compute_residuals(self):
        data_column = self.ui.comboBoxDataColumn.currentText()
        data = np.vstack(self.transmission.df[data_column].values)

        compute_run = Compute(data)

        compute_run.signals.update_progress.connect(self.update_progress_bar)
        compute_run.signals.result.connect(self.set_residuals)
        compute_run.signals.finished.connect(self.show_finished_message)
        compute_run.signals.error.connect(self.show_error_message)

        self.thread_pool = QtCore.QThreadPool()
        self.thread_pool.setMaxThreadCount(8)
        self.thread_pool.start(compute_run)

    @QtCore.pyqtSlot(int)
    def update_progress_bar(self, p: int):
        self.ui.progressBar.setValue(p)

    @QtCore.pyqtSlot(np.ndarray)
    def set_residuals(self, data: np.ndarray):
        self.residuals = data
        self.set_plot()

    def set_plot(self):
        self.plot.clear_all()
        if self.ui.radioButtonSqrtResiduals.isChecked():
            data = np.sqrt(self.residuals)
        else:
            data = self.residuals

        if self.ui.checkBoxMean.isChecked():
            data = np.mean(data, axis=0)
            self.plot.set_single_line(data)

            if self.ui.checkBoxD1Mean.isChecked():
                d1 = np.gradient(data)
                self.plot.add_line(d1, color='g')

            if self.ui.checkBoxD2Mean.isChecked():
                d2 = np.gradient(np.gradient(data))
                self.plot.add_line(d2, color='r')

        else:
            self.plot.set(data=data)

    @QtCore.pyqtSlot()
    def show_finished_message(self):
        QtWidgets.QMessageBox.information(self, 'Finished', 'Finished computing residuals. \n'
                                                            'Wait a minute for the plot to be drawn.')

    @QtCore.pyqtSlot(str)
    def show_error_message(self, msg: str):
        QtWidgets.QMessageBox.warning(self, 'Error while computing',
                                      f'The following error occured while computing residuals:\n{msg}')


class Signals(QtCore.QObject):
    update_progress = QtCore.pyqtSignal(int)
    result = QtCore.pyqtSignal(np.ndarray)
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)


class Compute(QtCore.QRunnable):
    def __init__(self, curves: np.ndarray):
        super(Compute, self).__init__()
        self.signals = Signals()
        self.curves = curves

    def run(self):
        a = self.curves
        try:
            r = np.zeros(shape=(a.shape[0], a.shape[1] - 1), dtype=np.float64)
            for i in range(a.shape[0]):
                r[i, :] = get_residuals(a[i, :])
                self.signals.update_progress.emit(int((i / (a.shape[0] - 1)) * 100))
            self.signals.finished.emit()
        except:
            self.signals.error.emit(str(traceback.format_exc()))
        else:
            self.signals.result.emit(r)
        finally:
            pass
