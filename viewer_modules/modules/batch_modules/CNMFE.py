#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 23 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..common import ViewerInterface, BatchRunInterface
from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import json
import caiman as cm


class Batch(BatchRunInterface):
    @staticmethod
    def process(input_imgseq, input_params):
        pass

    @staticmethod
    def show_output(output_imgseq, output_params):
        pass


class Process:
    @staticmethod
    def correlation_pnr():
        pass

    @staticmethod
    def preview_correlation_pnr():
        pass

    @staticmethod
    def cnmfe():
        pass


class VisualizeComponents(ViewerInterface, QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QWidget.__init__(self, parent)


class VisualizeCorrelationPNR(ViewerInterface, QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QWidget.__init__(self, parent)
