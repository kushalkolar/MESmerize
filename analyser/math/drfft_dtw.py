from tslearn.metrics import dtw
from scipy.fftpack import rfft, irfft
import numpy as np
from multiprocessing import Pool
from PyQt5 import QtCore, QtWidgets


def single_curve(start: int, step: int, interpolate: bool, raw_curve: np.ndarray = None, rf_curve: np.ndarray = None) -> np.ndarray:
    """Compute for a single curve and return a 1D array of distances where each element is an incremental step.
    Must provide either raw curve or rfft of curve"""
    if (raw_curve is None) and (rf_curve is None):
        raise ValueError('Must provide either raw curve or rfft of curve')

    steps = np.arange(start, len(raw_curve), step)

    if rf_curve is None:
        rf = rfft(raw_curve)
    else:
        rf = rf_curve

    if not interpolate:
        return _single_curve(raw_curve, rf, start, steps)

    else:
        return _single_curve_interp()


def _single_curve(raw_curve, rf, steps) -> np.ndarray:
    dtw_dists = []
    for step in steps:
        irf = irfft(rf[:step])
        dist = dtw(raw_curve, irf)
        dtw_dists.append(dist)

    return np.array(dtw_dists)


def _single_curve_interp(raw_curve, rf, start, steps):
    dtw_dists = []
    x = np.arange(0, len(raw_curve))
    for step in steps:
        irf = irfft(rf[:step])
        xp = np.linspace(0, raw_curve.size, step)
        interp = np.interp(x, xp, fp=irf)

        dist = dtw(raw_curve, interp)
        dtw_dists.append(dist)

    return np.array(dtw_dists)


def curves_2d(raw_curves: np.ndarray, start: int, step: int, interpolate: bool) -> np.ndarray:
    """Compute for a 2D array of curves
    :param raw_curves: (n_curves, y_values of curve)"""

    p = Pool()


class _Signals(QtCore.QObject):
    curve_processed = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)


class _Runner(QtCore.QRunnable):
    def __init__(self, raw_curves: np.ndarray, start: int, step: int, interpolate: bool, n_processes: int):
        QtCore.QRunnable.__init__(self)
        self.signals = _Signals()


class Widget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        layout = QtWidgets.QVBoxLayout()

        abort_button = QtWidgets.QPushButton()
        abort_button.setText('Abort')
        abort_button.clicked.connect(self.abort_requested)
        layout.addWidget(abort_button)


    def abort_requested(self):
        if QtWidgets.QMessageBox.question(self, 'Abort processes?',
                                         'Are you sure you want to abort?') == QtWidgets.QMessageBox.No:
            return
