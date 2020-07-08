#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ....pyqtgraphCore.widgets.ColorButton import ColorButton
import pandas as pd


class Row(QtWidgets.QWidget):
    def __init__(self, pd_series=None, label=None):
        """
        :type pd_series: pd.Series
        :type label: str
        """
        QtWidgets.QWidget.__init__(self)

        self.hlayout = QtWidgets.QHBoxLayout()

        if label is not None:
            self.qlabel = QtWidgets.QLabel(self)
            self.qlabel.setText(label)
            self.hlayout.addWidget(self.qlabel)
        else:
            self.qlabel = QtWidgets.QLabel(self)

        self.name = QtWidgets.QLineEdit(self)
        self.name.setPlaceholderText('Stimulus Name')
        self.name.setMaxLength(32)
        self.hlayout.addWidget(self.name)

        self.start = QtWidgets.QLineEdit(self)
        self.start.setValidator(QtGui.QDoubleValidator())
        self.start.setPlaceholderText('Start time')
        self.hlayout.addWidget(self.start)

        self.end = QtWidgets.QLineEdit(self)
        self.end.setPlaceholderText('End time')
        self.end.setValidator(QtGui.QDoubleValidator())
        self.hlayout.addWidget(self.end)

        self.color_btn = ColorButton(self)
        self.hlayout.addWidget(self.color_btn)

        self.btn_remove = QtWidgets.QPushButton(self)
        self.btn_remove.setText('Remove stim')
        self.hlayout.addWidget(self.btn_remove)

        if pd_series is not None:
            self.set_series(pd_series)

    def set_series(self, pd_series: pd.Series):
        self.name.setText(pd_series['name'])
        self.start.setText(str(pd_series['start']))
        self.end.setText(str(pd_series['end']))
        self.color_btn.setColor(pd_series['color'])

    def get_dict(self) -> dict:
        d = {'name': self.name.text(),
             'start': float(self.start.text()),
             'end': float(self.end.text()),
             'color': self.color_btn.color(mode='byte')
             }
        return d

    def delete(self):
        self.qlabel.deleteLater()
        self.name.deleteLater()
        self.start.deleteLater()
        self.end.deleteLater()
        self.btn_remove.deleteLater()
        self.color_btn.deleteLater()
