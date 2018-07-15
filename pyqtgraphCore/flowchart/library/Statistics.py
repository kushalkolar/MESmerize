# -*- coding: utf-8 -*-
import numpy as np
from ...Qt import QtCore, QtGui, QtWidgets
from ..Node import Node
# from . import functions
from ... import functions as pgfn
from .common import *
from ...python2_3 import xrange
from ... import PolyLineROI
from ... import Point
from ... import metaarray as metaarray
from analyser.DataTypes import *
from functools import partial
from analyser import PeakEditor
from analyser import Extraction
from analyser.stats_gui import StatsWindow
from analyser.plot_window.beeswarms_window import BeeswarmPlotWindow
from analyser import pca_gui
import pickle
import traceback


class BeeswarmPlots(CtrlNode):
    """Beeswarm and Violin plots"""
    nodeName = 'BeeswarmPlots'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_gui = None

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_gui is None:
            return

        transmissions = kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        transmissions_list = []

        for t in transmissions.items():
            t = t[1]
            if t is None:
                QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                continue

            transmissions_list.append(t.copy())

        self.plot_gui.update_input(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_gui is None:
            self.plot_gui = BeeswarmPlotWindow(parent=self)
        self.plot_gui.show()


class CurveAnalysis(CtrlNode):
    """Simple analysis of curves"""
    nodeName = 'CurveAnalysis'
    uiTemplate = [('Stats', 'button', {'text': 'Statistics/Plotting'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.ctrls['Stats'].clicked.connect(self._open_stats_gui)
        self.peak_results = None

    def process(self, **kwargs):
        self.kwargs = kwargs.copy()
        self.transmissions = self.kwargs['In']

    def _open_stats_gui(self):
        if hasattr(self, 'stats_gui'):
            self.stats_gui.show()
            return
        self.stats_gui = StatsWindow()
        self.stats_gui.input_transmissions(self.peak_results)
        self.stats_gui.show()


class PeakFeaturesExtract(CtrlNode):
    """Extract peak features. Use this after the Peak_Detect node."""
    nodeName = 'Peak_Features'
    uiTemplate = [('Extract', 'button', {'text': 'Compute'}),
                  ('Stats', 'button', {'text': 'Statistics/Plotting'})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.ctrls['Extract'].clicked.connect(self._extract)
        self.ctrls['Stats'].setEnabled(False)
        self.ctrls['Stats'].clicked.connect(self._open_stats_gui)
        self.peak_results = None

    def process(self, **kwargs):
        self.kwargs = kwargs.copy()
        # return {'Out': self.peak_results}

    def _extract(self):
        if self.kwargs is None:
            self.peak_results = None
            return

        transmissions = self.kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        self.peak_results = []
        for t in transmissions.items():
            t = t[1]
            if t is None:
                QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                continue
            elif not any('Peak_Detect' in d for d in t.src):
                raise IndexError('Peak data not found in incoming DataFrame! You must first pass through '
                                 'a Peak_Detect node before this one.')
            # t = t.copy()
            try:
                pf = Extraction.PeakFeaturesIter(t)
                tran_with_features = pf.get_all()

                self.peak_results.append(tran_with_features)

            except Exception as e:
                QtWidgets.QMessageBox.warning(None, 'Error computing', 'The following error occured during peak extraction:\n'
                                                                   + traceback.format_exc())

        self.changed()
        self.ctrls['Stats'].setEnabled(True)

    def _open_stats_gui(self):
        if hasattr(self, 'stats_gui'):
            self.stats_gui.show()
            return
        self.stats_gui = StatsWindow()
        self.stats_gui.input_transmissions(self.peak_results)
        self.stats_gui.show()


class PCA(CtrlNode):
    """PCA (Principal component analysis)"""
    nodeName = 'PCA'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.ctrls['ShowGUI'].clicked.connect(self._open_pca_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or not hasattr(self, 'pca_gui'):
            return

        transmissions = kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        transmissions_list = []

        for t in transmissions.items():
            t = t[1]
            if t is None:
                QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                continue

            if not any('Power Spectral Density' in d for d in t.src):
                raise KeyError('Cannot perform PCA with incoming transmissions. '
                               'You must pass through one of the following nodes before performing a PCA:\n'
                               'Power Spectral Density')

            transmissions_list.append(t.copy())

        self.pca_gui.update_input(transmissions_list)

    def _open_pca_gui(self):
        if hasattr(self, 'pca_gui'):
            self.pca_gui.show()
            return

        self.pca_gui = pca_gui.PCA_GUI()
        self.pca_gui.show()
        self.changed()
