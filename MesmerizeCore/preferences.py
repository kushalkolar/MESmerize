#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 27 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from psutil import cpu_count
from . import configuration
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .preferences_pytemplate import *

configuration.n_processes = cpu_count() - 1


class PreferencesGUI(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.spinBoxThreads.setValue(configuration.n_processes)
        self.ui.spinBoxThreads.setMaximum(cpu_count())

        self.ui.btnApply.clicked.connect(self.apply)
        self.ui.btnClose.clicked.connect(self.hide)

    def apply(self):
        configuration.n_processes = self.ui.spinBoxThreads.value()
