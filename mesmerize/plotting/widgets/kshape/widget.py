#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .control_widget import *
from . import kshape_process
import psutil
import os
from signal import SIGKILL
from ....common.utils import make_workdir, make_runfile
from ....common.qdialogs import *
import pickle
from ....analysis import Transmission, organize_dataframe_columns
import numpy as np
from functools import partial
from collections import deque
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.console import ConsoleWidget
from itertools import product as iter_product
from seaborn import lineplot
from ..proportions import ProportionsWidget
from ..base import BasePlotWidget
from math import sqrt, ceil
from ...utils import auto_colormap
from typing import Union


class KShapeControlDock(QtWidgets.QDockWidget):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_KShapeControl()
        self.ui.setupUi(self)
        self.setFloating(False)

    def get_params(self) -> dict:
        if self.ui.checkBoxRandom.isChecked():
            random_state = None
        else:
            random_state = self.ui.spinBoxRandom.value()

        d = {'n_clusters':      self.ui.spinBoxN_clusters.value(),
             'max_iter':        self.ui.spinBoxMaxIter.value(),
             'tol':             10 ** self.ui.spinBoxTol.value(),
             'n_init':          self.ui.spinBoxN_init.value(),
             'random_state':    random_state,
             'train_percent':   self.ui.spinBoxTrainSubsetPercentage.value()
             }

        return d

    def set_active(self):
        self.ui.pushButtonStart.setDisabled(True)
        self.ui.pushButtonAbort.setEnabled(True)

        self.ui.groupBoxKShapeParams.setEnabled(True)

    def set_inactive(self):
        self.ui.pushButtonStart.setEnabled(True)
        self.ui.pushButtonAbort.setDisabled(True)
        self.ui.groupBoxKShapeParams.setDisabled(False)


class KShapePlot(QtWidgets.QDockWidget):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.plot = MatplotlibWidget()
        self.setWidget(self.plot)

        self.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.setMinimumSize(QtCore.QSize(300, 300))

        self.fig = self.plot.fig
        self.ax_curves = self.fig.add_subplot(111)
        self.draw = self.plot.draw
        self.setWindowTitle('Samples of raw curves in a cluster')


class KShapeMeansPlot(MatplotlibWidget):
    def __init__(self, parent):
        # QtWidgets.QDockWidget.__init__(self, parent=parent)
        MatplotlibWidget.__init__(self)
        self.axs = None

    def set_plots(self, input_arrays: np.ndarray, n_clusters: int, y_pred: np.ndarray, xzero_pos: str, error_band):
        ncols, nrows = (int(ceil(sqrt(n_clusters))),) * 2

        if n_clusters < 11:
            cmap = 'tab10'
        elif 10 < n_clusters < 21:
            cmap = 'tab20'
        elif 20 < n_clusters < 211:
            cmap = 'nipy_spectral'
        else:
            raise ValueError("Cannot generate colormap for greater than 210 clusters.\n"
                             "What are you trying to do with > 210 clusters, what's wrong with you?")

        colors = auto_colormap(n_clusters, cmap, 'mpl', 'subsequent')

        self.fig.clear()
        self.axs = self.fig.subplots(nrows, ncols)
        for c_ix, i in enumerate(iter_product(range(nrows), range(ncols))):
            if c_ix == n_clusters:
                return
            ys = input_arrays[y_pred == c_ix]
            xs = []
            for y in ys:
                if xzero_pos == 'zero':
                    zero_ix = 0
                elif xzero_pos == 'maxima':
                    zero_ix = np.argmax(y)
                else:
                    raise ValueError('xzer_post argument accepts only either "zero" or "maxima"')
                xs.append(np.arange((0 - zero_ix), y.size - zero_ix))
            xsh = np.hstack(xs)
            ysh = np.hstack(ys)
            lineplot(x=xsh, y=ysh, ax=self.axs[i], err_style='band', color=colors[c_ix], ci=error_band)
            self.axs[i].set_title(f"cluster {c_ix}")

        self.draw()


class ProportionsDock(QtWidgets.QDockWidget):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)

        self.plot = ProportionsWidget()
        self.setWidget(self.plot)

        self.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.setMinimumSize(QtCore.QSize(100, 600))
        self.setWindowTitle('Proportions')


class KShapeWidget(QtWidgets.QMainWindow, BasePlotWidget):
    sig_output_changed = QtCore.pyqtSignal(Transmission)
    drop_opts = None

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        BasePlotWidget.__init__(self)
        self.setWindowTitle('k-Shape Clustering')

        self.control_widget = KShapeControlDock(parent=self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_widget)

        self.proportions_widget = ProportionsDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.proportions_widget)

        self.plot_proportions = self.proportions_widget.plot

        self.finished = False
        self.process = None

        self._workdir = None

        self._input_arrays = None
        self._params = None

        self._ks = None
        self._train_data = None
        self._y_pred = None
        self._cluster_centers = None
        self._cluster_means = None

        self.data_column = None
        self.input_connected = True

        self.std_out = deque(maxlen=500)

        self.control_widget.ui.pushButtonStart.clicked.connect(self.start_process)
        self.control_widget.ui.pushButtonAbort.clicked.connect(self.abort_process)

        self.control_widget.ui.listWidgetClusterNumber.currentItemChanged.connect(self.update_plot)

        self.control_widget.ui.pushButtonApplyPlotOptions.clicked.connect(self.update_plot)
        self.control_widget.ui.pushButtonApplyPlotOptions.clicked.connect(self.update_plot_means)

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot_dialog)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

        self.control_widget.ui.pushButtonReconnectFlowchartInput.clicked.connect(self.input_connect)
        self.control_widget.ui.pushButtonReconnectFlowchartInput.setVisible(False)

        self.plot = KShapePlot(parent=self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.plot)

        self.dockConsole = QtWidgets.QDockWidget(self)
        self.dockConsole.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setWidget(ConsoleWidget(parent=self, namespace={'this': self}))

        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockConsole)

        self.plot_means = KShapeMeansPlot(parent=self)
        # self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.plot_means)

        self.setCentralWidget(self.plot_means)

        self.resize(1500, 900)

    @property
    def input_arrays(self) -> np.ndarray:
        if self._input_arrays is None:
            raise ValueError('Input array not set')
        return self._input_arrays

    @input_arrays.setter
    def input_arrays(self, a: Union[np.ndarray, list]):
        if isinstance(a, list):
            a = np.array(a)
        if not isinstance(a, np.ndarray):
            raise TypeError('Must pass np.ndarray or list')
        elif a.ndim > 2:
            raise ValueError('Array must be 2D')

        self._input_arrays = a

    @property
    def ks(self) -> kshape_process.KShape:
        if self._ks is None:
            raise ValueError('KShape not instantiated')
        return self._ks

    @ks.setter
    def ks(self, ks: kshape_process.KShape):
        if not isinstance(ks, kshape_process.KShape):
            raise TypeError('Must pass KShape instance')
        self._ks = ks

    @property
    def n_clusters(self) -> int:
        if self._n_clusters is None:
            raise ValueError('Must finish clustering first')
        return self._n_clusters

    @n_clusters.setter
    def n_clusters(self, n: int):
        if type(n) is not int:
            raise TypeError('n_clusters must be int')
        self._n_clusters = n

    @property
    def train_data(self) -> np.ndarray:
        if self._train_data is None:
            raise ValueError('Must run clustering first')
        return self._train_data

    @train_data.setter
    def train_data(self, data: Union[np.ndarray, list]):
        if isinstance(data, list):
            data = np.array(data)
        if not isinstance(data, np.ndarray):
            raise ValueError('Must pass numpy array or list')
        self._train_data = data

    @property
    def y_pred(self) -> np.ndarray:
        if self._y_pred is None:
            raise ValueError('No predictions have been fit')
        return self._y_pred

    @y_pred.setter
    def y_pred(self, y_pred: Union[np.ndarray, list]):
        if isinstance(y_pred, list):
            y_pred = np.array(y_pred)
        if not isinstance(y_pred, np.ndarray):
            raise TypeError('Must pass numpy array or list')
        self._y_pred = y_pred

    @property
    def cluster_centers(self) -> np.ndarray:
        if self._cluster_centers is None:
            raise ValueError('Must finish clustering first')
        return self._cluster_centers

    @cluster_centers.setter
    def cluster_centers(self, c: Union[np.ndarray, list]):
        if isinstance(c, list):
            c = np.array(c)
        if not isinstance(c, np.ndarray):
            raise TypeError('Must pass numpy array or list')
        self._cluster_centers = c

    @property
    def cluster_means(self) -> np.ndarray:
        if self._cluster_means is None:
            raise ValueError('No predictions have been fit')
        return self._cluster_centers

    @cluster_means.setter
    def cluster_means(self, cms: Union[np.ndarray, list]):
        if isinstance(cms, list):
            self.cms = np.array(cms)
        if not isinstance(cms, np.ndarray):
            raise TypeError('Must pass np.ndarray or list')
        self._cluster_means = cms

    @property
    def params(self) -> dict:
        if self._params is None:
            raise ValueError('Params not set')
        return self._params

    @params.setter
    def params(self, d: dict):
        self._params = d

    def clear_data(self):
        self._ks = None
        self._y_pred = None
        self._input_arrays = None

    def set_input(self, transmission: Transmission):
        if not self.input_connected:
            return
        super(KShapeWidget, self).set_input(transmission)
        self.transmission.df.reset_index(drop=True, inplace=True)
        self.proportions_widget.plot.set_input(self.transmission)

        dcols, ccols, ucols = organize_dataframe_columns(self.transmission.df.columns.tolist())
        dcols.sort()

        self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.addItems(dcols)

    def pad_input_data(self, a: np.ndarray, method: str = 'random') -> np.ndarray:
        l = 0  # size of largest time series

        # Get size of largest time series
        for c in a:
            s = c.size
            if s > l:
                l = s

        # pre-allocate output array
        p = np.zeros(shape=(a.size, l))

        # pad each 1D time series
        for i in range(p.shape[0]):
            s = a[i].size

            if s == l:
                p[i, :] = a[i]
                continue

            max_pad_en_ix = l - s

            if method == 'random':
                pre = np.random.randint(0, max_pad_en_ix)
            elif method == 'fill-size':
                pre = 0
            else:
                raise ValueError('Must specific method as either "random" or "fill-size"')

            post = l - (pre + s)
            p[i, :] = np.pad(a[i], (pre, post), 'minimum')

        return p

    @present_exceptions('Start process error', 'Make sure you have selected an appropriate Data Column')
    def start_process(self, *args, **kwargs):
        if self.finished:
            if QtWidgets.QMessageBox.warning(self, 'Discard data?',
                                             'Would you like to discard the current clustering data?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            self.plot.ax_curves.cla()

        self.finished = False
        self.input_disconnect()
        self.clear_data()

        self.data_column = self.control_widget.ui.comboBoxDataColumn.currentText()
        self.input_arrays = self.transmission.df[self.data_column].values

        self.train_percentage = self.control_widget.ui.spinBoxTrainSubsetPercentage.value()

        padded = self.pad_input_data(self.input_arrays, method='fill-size')
        # scaler = TimeSeriesScalerMeanVariance()
        # self.input_arrays = scaler.fit_transform(padded)[:, :, 0]

        workdir = self.get_workdir()

        self.clear_workdir()

        self.params = {'kwargs': self.control_widget.get_params(),
                       'workdir': workdir,
                       'out': workdir + '/out'}

        params_path = os.path.abspath(workdir + '/params.pickle')
        pickle.dump(self.params, open(params_path, 'wb'))

        data_path = os.path.abspath(workdir + '/data.npy')
        np.save(data_path, padded)

        self.process = QtCore.QProcess()
        self.process.setWorkingDirectory(self.get_workdir())

        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(partial(self.print_stdout, self.process))
        self.process.readyReadStandardError.connect(partial(self.print_stdout, self.process))
        self.process.finished.connect(self.process_finished)

        m = os.path.abspath(kshape_process.__file__)
        args = data_path + ' ' + params_path
        sh_file_path = make_runfile(module_path=m, savedir=self.get_workdir(), args_str=args)

        self.control_widget.ui.textBrowser.clear()

        self.process.start(sh_file_path)

        self.control_widget.set_active()

    def print_stdout(self, process: QtCore.QProcess):
        std_out = process.readAll().data().decode('utf8')
        self.control_widget.ui.textBrowser.append(std_out)

    def get_workdir(self):
        if self._workdir is None:
            self._workdir = make_workdir('kshape')
        return os.path.abspath(self._workdir)

    def clear_workdir(self):
        if self._workdir is None:
            return

        workdir = self.get_workdir()

        for f in ['params.pickle', 'data.npy', 'train.npy', 'y_pred.npy', 'ks.pickle', 'out']:
            try:
                os.remove(workdir + '/' + f)
            except FileNotFoundError:
                pass

    def abort_process(self):
        if QtWidgets.QMessageBox.warning(self, 'Abort?',
                                         'Confirm abort',
                                         QtWidgets.QMessageBox.Yes,
                                         QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return False
        self.process.finished.disconnect(self.process_finished)
        self.terminate_qprocess()
        self.control_widget.set_inactive()

        return True

    def terminate_qprocess(self):
        try:
            py_proc = psutil.Process(self.process.pid()).children()[0].pid
        except psutil.NoSuchProcess:
            return
        children = psutil.Process(py_proc).children()
        os.kill(py_proc, SIGKILL)
        for child in children:
            os.kill(child.pid, SIGKILL)

    def process_finished(self):
        self.control_widget.set_inactive()

        if open(self.params['out'], 'r').read() == 0:
            return

        ks_path = os.path.join(self.params['workdir'], 'ks.pickle')
        self.ks = pickle.load(open(ks_path, 'rb'))

        train_path = os.path.join(self.params['workdir'], 'train.npy')
        self.train_data = np.load(train_path)

        y_pred_path = os.path.join(self.params['workdir'], 'y_pred.npy')
        self.y_pred = np.load(y_pred_path)

        self.n_clusters = self.params['kwargs']['n_clusters']
        self.cluster_centers = self.ks.cluster_centers_

        self.set_n_clusters_list()

        self.transmission.df['KSHAPE_CLUSTER'] = self.y_pred

        self.proportions_widget.plot.set_input(self.transmission)

        self.update_plot_means()

        self.send_output_transmission()
        self.finished = True

    def send_output_transmission(self):
        t = self.transmission.copy()
        params = self.params['kwargs']
        t.history_trace.add_operation('all', operation='kshape', parameters=params)
        self.sig_output_changed.emit(t)

    def set_n_clusters_list(self):
        self.control_widget.ui.listWidgetClusterNumber.clear()
        self.control_widget.ui.listWidgetClusterNumber.addItems(list(map(str, range(self.n_clusters))))
        self.control_widget.ui.listWidgetClusterNumber.setCurrentRow(0)

    def set_plot_opts(self, opts: dict):
        prop_opts = opts.pop('proportion_opts')
        self.plot_proportions.set_plot_opts(prop_opts)

        ui_state = opts.pop('ui_state')

        ix = self.control_widget.ui.comboBoxDataColumn.findText(ui_state['data_column'])
        self.control_widget.ui.comboBoxDataColumn.setCurrentIndex(ix)
        self.control_widget.ui.checkBoxShowKShapeCenters.setChecked(ui_state['show_centers'])
        self.control_widget.ui.spinBoxMaxNumCurves.setValue(ui_state['max_num_curves'])
        ix = self.control_widget.ui.comboBoxErrorBand.findText(ui_state['error_band'])
        self.control_widget.ui.comboBoxErrorBand.setCurrentIndex(ix)
        self.control_widget.ui.radioButtonXZeroZero.setChecked(ui_state['x-zero_zero'])
        self.control_widget.ui.radioButtonXZeroMaxima.setChecked(ui_state['x-zero_maxima'])

        self.data_column = ui_state['data_column']
        self.input_arrays = self.transmission.df[self.data_column].values

        for k in opts.keys():
            setattr(self, k, opts[k])

        self.set_n_clusters_list()

    def get_plot_opts(self, drop: bool) -> dict:
        """
        :param drop: Unused for this Plot Widget
        :return:
        """
        opts = {'proportion_opts':  self.plot_proportions.get_plot_opts(drop=True),
                'n_clusters':       self.n_clusters,
                'train_data':       self.train_data.tolist(),
                'y_pred':           self.y_pred.tolist(),
                'cluster_centers':  self.cluster_centers.tolist(),
                'ui_state':
                                {'data_column':     self.data_column,
                                 'show_centers':    self.control_widget.ui.checkBoxShowKShapeCenters.isChecked(),
                                 'max_num_curves':  self.control_widget.ui.spinBoxMaxNumCurves.value(),
                                 'error_band':      self.control_widget.ui.comboBoxErrorBand.currentText(),
                                 'x-zero_zero':     self.control_widget.ui.radioButtonXZeroZero.isChecked(),
                                 'x-zero_maxima':   self.control_widget.ui.radioButtonXZeroMaxima.isChecked()
                                 }
                }

        return opts

    @present_exceptions('Plotting error', 'The following error occurred when plotting the raw curves')
    def update_plot(self, *args, show_centers=True, **kwargs):
        max_num_curves = self.control_widget.ui.spinBoxMaxNumCurves.value()
        show_centers = self.control_widget.ui.checkBoxShowKShapeCenters.isChecked()

        cluster_num = int(self.control_widget.ui.listWidgetClusterNumber.currentItem().text())

        self.plot.ax_curves.cla()

        padded = self.pad_input_data(self.input_arrays)
        scaled = TimeSeriesScalerMeanVariance().fit_transform(padded)[:, :, 0]

        members = scaled[self.y_pred == cluster_num]
        # Plot only 'max_num_curves' to prevent the plot from being overcrowded and hard to visualize
        n_samples = min(members.shape[0], max_num_curves)
        samples = members[np.random.choice(members.shape[0], size=n_samples, replace=False)]

        for sample in samples:
            self.plot.ax_curves.plot(sample.ravel(), 'k-', alpha=0.2)

        if show_centers:
            center = self.cluster_centers[cluster_num].ravel()
            self.plot.ax_curves.plot(center, 'r-')

        low = np.min(scaled)
        high = np.max(scaled)

        self.plot.ax_curves.set_ylim(low, high)

        self.plot.ax_curves.set_title('Cluster ' + str(cluster_num))

        self.plot.draw()

    @present_exceptions('Plotting error', 'The following error occurred when plotting the means')
    def update_plot_means(self, *args, **kwargs):
        padded = self.pad_input_data(self.input_arrays, 'fill-size')
        scaled = TimeSeriesScalerMeanVariance().fit_transform(padded)[:, :, 0]

        if self.control_widget.ui.radioButtonXZeroZero.isChecked():
            xzero = 'zero'
        elif self.control_widget.ui.radioButtonXZeroMaxima.isChecked():
            xzero = 'maxima'
        else:
            raise ValueError('Must select an option for set x = 0 at')

        if self.control_widget.ui.comboBoxErrorBand.currentText() == 'standard deviation':
            ci = 'sd'
        elif self.control_widget.ui.comboBoxErrorBand.currentText() == 'confidence interval':
            ci = 95
        elif self.control_widget.ui.comboBoxErrorBand.currentText() == 'None':
            ci = None

        self.plot_means.set_plots(scaled, self.n_clusters, self.y_pred, xzero_pos=xzero, error_band=ci)
        self.plot_means.show()

    # Need to plot the means as well just once
    def open_plot(self, ptrn_path: str, proj_path: str) -> Union[Tuple[str, str], None]:
        super(KShapeWidget, self).open_plot(ptrn_path, proj_path)
        self.update_plot_means()
        self.input_disconnect()
        return ptrn_path, proj_path

    def input_disconnect(self):
        self.input_connected = False
        self.control_widget.ui.labelConnectedToFlowchart.setText('INPUT DISCONNECTED')
        self.control_widget.ui.pushButtonReconnectFlowchartInput.setVisible(True)

    def input_connect(self):
        self.input_connected = True
        self.control_widget.ui.labelConnectedToFlowchart.setText('INPUT CONNECTED TO FLOWCHART')
        self.control_widget.ui.pushButtonReconnectFlowchartInput.setVisible(False)

    def closeEvent(self, QCloseEvent):
        if self.abort_process():
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()
