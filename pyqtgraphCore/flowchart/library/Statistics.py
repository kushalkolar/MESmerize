# -*- coding: utf-8 -*-
import numpy as np
from ...Qt import QtCore, QtGui, QtWidgets
from ..Node import Node
from . import functions
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
import pickle

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
                                                                   + str(e))

        self.changed()
        self.ctrls['Stats'].setEnabled(True)

    def _open_stats_gui(self):
        if hasattr(self, 'stats_gui'):
            self.stats_gui.show()
            return
        self.stats_gui = StatsWindow()
        self.stats_gui.input_transmissions(self.peak_results)
        self.stats_gui.show()