#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 1 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from skimage import transform
import numpy as np
from ..modules.common import ViewerInterface


class ResizeDialogBox(QtWidgets.QWidget):
    def __init__(self, viewer_interface):
        QtWidgets.QWidget.__init__(self, parent=None)
        assert isinstance(viewer_interface, ViewerInterface)
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
        self.btn.clicked.connect(self._resize_fast(self.spinBox / 100))
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setValue(0)
        layout.addWidget(self.progressBar)
        self.show()

    def _resize_fast(self, factor):
        try:
            self.resize_gui = None
        except Exception as e:
            print(e)

        template = transform.rescale(self.vi.viewer_ref.workEnv.imgdata.seq[:, :, :2], factor)
        r = np.zeros((template.shape[0], template.shape[1], self.vi.viewer_ref.workEnv.imgdata.seq.shape[2]),
                     dtype=self.vi.viewer_ref.workEnv.imgdata.seq.dtype)

        for i in range(0, self.vi.viewer_ref.workEnv.imgdata.seq[2]):
            r[:, :, i] = transform.rescale(self.vi.viewer_ref.workEnv.imgdata.seq[:, :, i], factor, preserve_range=True)
            self.progressBar.setValue(int(i / self.vi.viewer_ref.workEnv.imgdata.seq[2]))

        self.vi.viewer_ref.workEnv.imgdata.seq = r
        self.vi.VIEWER_update_workEnv()