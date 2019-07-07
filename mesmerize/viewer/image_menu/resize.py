#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 1 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from skimage.transform import rescale
import numpy as np
from ..core.common import ViewerUtils
from functools import partial
from multiprocessing.pool import ThreadPool as Pool
from ...common import get_sys_config
import traceback


class ResizeDialogBox(QtWidgets.QWidget):
    sig_increase_progressBar = QtCore.pyqtSignal()

    def __init__(self, viewer_interface):
        QtWidgets.QWidget.__init__(self)
        assert isinstance(viewer_interface, ViewerUtils)
        self.vi = viewer_interface
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel()
        label.setText('Set scaling factor in %')
        layout.addWidget(label)

        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMaximum(100)
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(60)
        layout.addWidget(self.spinBox)

        self.btn = QtWidgets.QPushButton()
        self.btn.setText('Apply')
        layout.addWidget(self.btn)
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setMaximum(100)
        layout.addWidget(self.progressBar)
        self.status_label = QtWidgets.QLabel()
        self.status_label.setText('')
        layout.addWidget(self.status_label)
        self.btn.clicked.connect(partial(self.resize_img_seq, self.spinBox.value() / 100))
        self.setLayout(layout)
        self.setWindowTitle('Resize')
        self.frames_processed = 0

    def resize_img_seq(self, factor):
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Cannot resize', 'Your work environment is empty, nothing to resize!')
            self.hide()
            return
        self.vi.viewer.status_bar_label.showMessage('Resizing, please wait...')
        n_processes = int(get_sys_config()['_MESMERIZE_N_THREADS'])

        seq = self.vi.viewer.workEnv.imgdata.seq
        self.num_frames_to_process = seq.shape[2]
        self.frames_processed = 0

        resizer = ResizeObject(seq, factor, n_processes)

        resizer.signals.frame_processed.connect(self.increase_progress_bar)
        resizer.signals.result.connect(self.set_resized_array)
        resizer.signals.error.connect(self.show_error_message)
        resizer.signals.finished.connect(lambda: self.vi.viewer.status_bar_label.showMessage('Resize completed!'))
        resizer.signals.finished.connect(lambda: self.status_label.setText('Done!'))
        resizer.signals.finished.connect(lambda: self.progressBar.setValue(0))

        self.thread_pool = QtCore.QThreadPool()
        self.thread_pool.setMaxThreadCount(n_processes)
        self.thread_pool.start(resizer)

    @QtCore.pyqtSlot()
    def increase_progress_bar(self):
        self.frames_processed += 1
        self.progressBar.setValue(int(self.frames_processed * 100 / self.num_frames_to_process))

    @QtCore.pyqtSlot(np.ndarray)
    def set_resized_array(self, array):
        self.vi.viewer.workEnv.imgdata.seq = array
        self.vi.update_workEnv()

    @QtCore.pyqtSlot(str)
    def show_error_message(self, error_msg):
        QtWidgets.QMessageBox.warning(self, 'Error', 'The following error occured while resizing:\n' + str(error_msg))
        self.vi.viewer.status_bar_label.clearMessage()


class Signals(QtCore.QObject):
    frame_processed = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(np.ndarray)
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)


class ResizeObject(QtCore.QRunnable):
    def __init__(self, seq, factor, n_processes):
        super(ResizeObject, self).__init__()
        self.signals = Signals()
        self.seq = seq
        self.factor = factor
        self.n_processes = n_processes

    def resize_split(self, template_factor, img):
        tmpl = template_factor[0]
        factor = template_factor[1]
        r = np.zeros((tmpl.shape[0], tmpl.shape[1], img.shape[2]), dtype=img.dtype)

        for i in range(0, img.shape[2]):
            r[:, :, i] = rescale(img[:, :, i], factor, preserve_range=True)
            self.signals.frame_processed.emit()

        return r

    def run(self):
        try:
            tmpl = rescale(self.seq[:, :, :2], self.factor)

            template_factor = [tmpl, self.factor]

            pool = Pool(self.n_processes)
            splits_resized = pool.map(partial(self.resize_split, template_factor),
                                      np.array_split(self.seq, self.n_processes, axis=2))

            resized_array = np.concatenate(splits_resized, axis=2)
        except:
            self.signals.error.emit(str(traceback.format_exc()))
        else:
            self.signals.result.emit(resized_array)
        finally:
            self.signals.finished.emit()
