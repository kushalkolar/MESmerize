#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .pytemplates.window_pytemplate import *
import pandas as pd
from ..DataTypes import Transmission, GroupTransmission, StatsTransmission


class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dataframe = pd.DataFrame()
        self.data_columns = []
        self.groups = []

    def set_plot_controls_ui(self, control_widget):
        self.ui.tabWidget.widget(0).layout().addWidget(control_widget)