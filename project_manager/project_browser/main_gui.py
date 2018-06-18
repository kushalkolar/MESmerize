#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 17 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .tab_area_widget import TabAreaWidget
import pandas as pd


class Main(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(parent)

        self.tabs = {}

    @property
    def dataframe(self):
        pass

    @dataframe.setter
    def dataframe(self, df: pd.DataFrame):
        pass

    def add_tab(self):
        pass

    def populate_tab(self):
        pass

    def initialize(self):
        pass

    @QtCore.pyqtSlot(dict)
    def filter(self):
        pass

    def close_tab(self):
        pass

