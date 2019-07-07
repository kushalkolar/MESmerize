# from tslearn.metrics import dtw
from scipy.fftpack import rfft, irfft
import numpy as np
from multiprocessing import Pool, Manager
from PyQt5 import QtCore, QtWidgets
from functools import partial
from ...plotting.variants.timeseries import TimeseriesPlot
import traceback
from os import environ
try:
    n_processes = environ['n_processes']
except:
    n_processes = 4


def single_curve(steps: np.ndarray, interpolate: bool, q: Manager().Queue = None,
                 raw_curve: np.ndarray = None, rf_curve: np.ndarray = None) -> list:
    """Compute for a single curve and return a 1D array of distances where each element is an incremental step.
    Must provide either raw curve or rfft of curve"""
    if (raw_curve is None) and (rf_curve is None):
        raise ValueError('Must provide either raw curve or rfft of curve')

    if rf_curve is None:
        rf = rfft(raw_curve)
    else:
        rf = rf_curve

    if not interpolate:
        rval = _single_curve(raw_curve, rf, steps)

    else:
        rval = _single_curve_interp(raw_curve, rf, steps)

    if q is not None:
        q.put(1)

    return rval


def _single_curve(raw_curve, rf, steps) -> list:
    dtw_dists = []
    for step in steps:
        irf = irfft(rf[:step])
        dist = dtw(raw_curve, irf)
        dtw_dists.append(dist)

    return dtw_dists


def _single_curve_interp(raw_curve, rf, steps) -> list:
    dtw_dists = []
    x = np.arange(0, len(raw_curve))
    for step in steps:
        irf = irfft(rf[:step])
        xp = np.linspace(0, raw_curve.size, step)
        interp = np.interp(x, xp, fp=irf)

        dist = dtw(raw_curve, interp)
        dtw_dists.append(dist)

    return dtw_dists


def curves_2d(raw_curves: np.ndarray, start: int, step: int, interpolate: bool) -> np.ndarray:
    """Compute for a 2D array of curves
    :param raw_curves: (n_curves, y_values of curve)"""

    p = Pool(n_processes)
    fft_curves = rfft(raw_curves)

    dists = p.starmap(partial(single_curve, start, step, interpolate), zip(raw_curves, fft_curves))


class _Signals(QtCore.QObject):
    update_progress_bar = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(np.ndarray)
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)


class Widget(QtWidgets.QWidget):
    sig_set_progress_bar = QtCore.pyqtSignal(float)

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        layout = QtWidgets.QVBoxLayout()

        abort_button = QtWidgets.QPushButton()
        abort_button.setText('Abort')
        abort_button.clicked.connect(self.abort_requested)
        layout.addWidget(abort_button)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.label = QtWidgets.QLabel()
        self.label.setText('')
        layout.addWidget(self.label)

        self.plot = TimeseriesPlot()
        self.plot.hide()
        layout.addWidget(self.plot)

        self.setLayout(layout)

    def abort_requested(self):
        if QtWidgets.QMessageBox.question(self, 'Abort processes?',
                                         'Are you sure you want to abort?') == QtWidgets.QMessageBox.No:
            return
        self.runner.p.terminate()
        self.thread_pool.cancel(self.runner)

    @QtCore.pyqtSlot()
    def update_progress_bar(self):
        self.num_processed += 1
        v = int(self.num_processed / self.num_curves)
        print(v)
        self.progress_bar.setValue(v * 100)

    def start(self, start: int, step: int, interpolate: bool,
              raw_curves: np.ndarray):

        self.num_curves = raw_curves.shape[0]
        self.num_processed = 0

        self.runner = _Runner(start, step, interpolate, raw_curves)

        self.runner.signals.update_progress_bar.connect(self.update_progress_bar)
        self.runner.signals.result.connect(self.set_plot)
        self.runner.signals.finished.connect(lambda: self.label.setText('Done!'))
        self.runner.signals.finished.connect(lambda: self.progress_bar.setValue(100))
        self.runner.signals.error.connect(lambda e: QtWidgets.QMessageBox.warning(None, 'Error', e))

        self.thread_pool = QtCore.QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.thread_pool.start(self.runner)

    # @QtCore.pyqtSlot(np.ndarray)
    def set_plot(self, result: np.ndarray):
        self.plot.clear()
        self.plot.set(result)
        self.plot.show()


class _Runner(QtCore.QRunnable):
    def __init__(self, start: int, step: int, interpolate: bool,
              raw_curves: np.ndarray):
        super(_Runner, self).__init__()

        assert isinstance(raw_curves, np.ndarray)

        self.signals = _Signals()

        self.start_param = start
        self.step_param = step
        self.interpolate_param = interpolate
        self.raw_curves = raw_curves

    def run(self):
        try:
            self.p = Pool(n_processes)
            rf_curve = rfft(self.raw_curves)
            q = Manager().Queue()

            steps = np.arange(self.start_param, len(self.raw_curves[0, :]), self.step_param)

            self.dists = self.p.starmap(partial(single_curve, steps, self.interpolate_param, q), zip(self.raw_curves, rf_curve))

            num_finished = 0
            num_curves = self.raw_curves.shape[0]

            # while num_finished < num_curves:
            #     sleep(1)
            #     if q.qsize() > 0:
            #         q.get()
            #         self.signals.update_progress_bar.emit()

            dists_array = np.array(self.dists)

        except:
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.result.emit(dists_array)
        finally:
            self.p.terminate()
            self.signals.finished.emit()
