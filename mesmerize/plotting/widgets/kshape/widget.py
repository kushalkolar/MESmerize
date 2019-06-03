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
from ....common.process_utils import make_workdir, make_runfile
import pickle
from ....analysis.data_types import Transmission
import numpy as np
import traceback
from functools import partial
from collections import deque
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from matplotlib.gridspec import GridSpec
from ....analysis.utils import get_cluster_proportions


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
             'random_state':    random_state
             }

        return d

    def set_active(self):
        self.ui.pushButtonStart.setDisabled(True)
        self.ui.pushButtonAbort.setEnabled(True)

    def set_inactive(self):
        self.ui.pushButtonStart.setEnabled(True)
        self.ui.pushButtonAbort.setDisabled(True)


class KShapePlot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        gs = GridSpec(1, 3, wspace=0.3)
        self.ax_curves = self.fig.add_subplot(gs[0, :2])
        self.ax_prop = self.fig.add_subplot(gs[0, 2])
        self.ax_prop.set_title('Proportions')


class KShapeWidget(QtWidgets.QMainWindow):
    sig_output_changed = QtCore.pyqtSignal(Transmission)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.setWindowTitle('k-Shape Clustering')
        self.resize(1200, 400)
        self.control_widget = KShapeControlDock(parent=self)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.control_widget)

        self.finished = False
        self.process = None

        self._workdir = None

        self.input_data = None
        self.params = None

        self.ks = None
        self.y_pred = None

        self.transmission = None
        self.data_column = None

        self.std_out = deque(maxlen=500)

        self.control_widget.ui.pushButtonStart.clicked.connect(self.start_process)
        self.control_widget.ui.pushButtonAbort.clicked.connect(self.abort_process)

        self.control_widget.ui.listWidgetClusterNumber.currentItemChanged.connect(self.set_plot)

        self.control_widget.ui.comboBoxGroups.currentTextChanged.connect(self.plot_proportions)

        self.plot = KShapePlot()

        self.setCentralWidget(self.plot)

    def set_input(self, transmission: Transmission):
        assert isinstance(transmission, Transmission)
        self.transmission = transmission
        self.transmission.df.reset_index(drop=True, inplace=True)

        cols = self.transmission.df.columns.tolist()
        cols.sort()

        self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.addItems(cols)

        self.control_widget.ui.comboBoxGroups.clear()
        self.control_widget.ui.comboBoxGroups.addItems(cols)

    def get_params_dict(self) -> dict:
        d = self.control_widget.get_params()
        return d

    def pad_input_data(self, a: np.ndarray) -> np.ndarray:
        l = 0

        for c in a:
            s = c.size
            if s > l:
                l = s

        p = np.zeros(shape=(a.size, l))

        for i in range(p.shape[0]):
            s = a[i].size

            if s == l:
                p[i, :] = a[i]
                continue

            max_pad_en_ix = l - s

            pre = np.random.randint(0, max_pad_en_ix)
            post = l - (pre + s)
            p[i, :] = np.pad(a[i], (pre, post), 'minimum')

        return p

    def start_process(self):
        if self.finished:
            if QtWidgets.QMessageBox.warning(self, 'Discard data?',
                                             'Would you like to discard the current clustering data?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
            self.plot.fig.clear()
            # self.plot.clear()

        scaler = TimeSeriesScalerMeanVariance()
        try:
            self.data_column = self.control_widget.ui.comboBoxDataColumn.currentText()
            arrays = self.transmission.df[self.data_column].values
            arrays = self.pad_input_data(arrays)
            self.input_data = scaler.fit_transform(arrays)[:, :, 0]
        except:
            QtWidgets.QMessageBox.warning(self, 'Invalid data column',
                                          'The data types in the chosen '
                                          'data column is not appropriate.\n' + traceback.format_exc())
            return

        workdir = self.get_workdir()

        self.clear_workdir()

        self.params = {'kwargs': self.get_params_dict(),
                       'workdir': workdir,
                       'out': workdir + '/out'}

        params_path = os.path.abspath(workdir + '/params.pickle')
        pickle.dump(self.params, open(params_path, 'wb'))

        data_path = os.path.abspath(workdir + '/data.npy')
        np.save(data_path, self.input_data)

        self.process = QtCore.QProcess()
        self.process.setWorkingDirectory(self.get_workdir())

        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(partial(self.print_stdout, self.process))
        self.process.finished.connect(self.process_finished)

        m = os.path.abspath(kshape_process.__file__)
        args = data_path + ' ' + params_path
        sh_file_path = make_runfile(module_path=m, workdir=self.get_workdir(), args_str=args)

        self.control_widget.ui.textBrowser.clear()

        self.process.start(sh_file_path)

        self.finished = False
        self.control_widget.set_active()

    def print_stdout(self, process: QtCore.QProcess):
        std_out = process.readAllStandardOutput().data().decode('utf8')
        self.control_widget.ui.textBrowser.append(std_out)

    def get_workdir(self):
        if self._workdir is None:
            self._workdir = make_workdir('kshape')
        return os.path.abspath(self._workdir)

    def clear_workdir(self):
        if self._workdir is None:
            return

        workdir = self.get_workdir()

        for f in ['params.pickle', 'data.npy', 'ks.pickle', 'out.pickle']:
            try:
                os.remove(workdir + '/' + f)
            except FileNotFoundError:
                pass

    def abort_process(self):
        if QtWidgets.QMessageBox.warning(self, 'Abort?',
                                         'Confirm abort',
                                         QtWidgets.QMessageBox.Yes,
                                         QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return
        self.terminate_qprocess()
        self.control_widget.set_inactive()

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

        ks_path = self.params['workdir'] + '/ks.pickle'
        self.ks = pickle.load(open(ks_path, 'rb'))

        y_pred_path = self.params['workdir'] + '/y_pred.pickle'
        self.y_pred = pickle.load(open(y_pred_path, 'rb'))

        num_clusters = self.params['kwargs']['n_clusters']

        self.control_widget.ui.listWidgetClusterNumber.clear()
        self.control_widget.ui.listWidgetClusterNumber.addItems(list(map(str, range(num_clusters))))

        self.finished = True

        self.plot_proportions(self.control_widget.ui.comboBoxGroups.currentText())

        self.send_output_transmission()

    def send_output_transmission(self):
        self.transmission.df['_KSHAPE'] = self.y_pred
        params = self.params['kwargs']
        self.transmission.history_trace.add_operation('all', operation='kshape', parameters=params)
        self.sig_output_changed.emit(self.transmission)

    def set_plot(self, item: QtWidgets.QListWidgetItem):
        if item is None:
            return

        if not self.finished:
            QtWidgets.QMessageBox.warning(self, 'Nothing to plot', 'Clustering must finish '
                                                                   'before you can plot anything')
            return

        cluster_num = int(item.text())

        self.plot.ax_curves.cla()

        for xx in self.input_data[self.y_pred == cluster_num]:
            self.plot.ax_curves.plot(xx.ravel(), 'k-', alpha=0.2)

        center = self.ks.cluster_centers_[cluster_num].ravel()
        self.plot.ax_curves.plot(center, 'r-')

        low = np.min(self.input_data)
        high = np.max(self.input_data)

        self.plot.ax_curves.set_ylim(low, high)

        self.plot.ax_curves.set_title('Cluster ' + str(cluster_num))

        self.plot.draw()

    def plot_proportions(self, grouping_column):
        if not self.finished:
            return

        group_labels = self.transmission.df[grouping_column]

        try:
            self.plot.ax_prop.cla()
            props = get_cluster_proportions(self.y_pred, group_labels)
            props.plot(kind='bar', stacked=True, ax=self.plot.ax_prop)
            self.plot.ax_prop.legend(loc='best', bbox_to_anchor=(1.0, 0.5))
            self.plot.draw()
        except:
            QtWidgets.QMessageBox.warning(self, 'Error showing proportions',
                                          'You probably did not select an '
                                          'appropriate grouping column\n' + traceback.format_exc())
