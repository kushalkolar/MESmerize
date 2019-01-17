#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from PyQt5 import QtCore, QtGui, QtWidgets
from zst_plot import ZSTPlot
from template import Ui_Form
from pyqtgraphCore.imageview.ImageView import ImageView
import numpy as np


class ZSTWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = ZSTPlot()

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.plot_widget)
        self.image_view = ImageView()
        self.splitter.addWidget(self.image_view)

        self.vlayout.addWidget(self.splitter)
        self.setLayout(self.vlayout)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ZSTWidget()

    data = np.load('/home/kushal/Sars_stuff/palp_project_mesmerize/zst_data.npy')
    w.plot_widget.set(data, cmap='jet')
    w.plot_widget.add_stimulus_indicator(144, 288, 'k')


    w.show()
    app.exec()
