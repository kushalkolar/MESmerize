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
from analyser.DataTypes import Transmission
from scipy import signal
from functools import partial
import pandas as pd
from analyser.math.tvregdiff import tv_reg_diff
from scipy import fftpack


class AbsoluteValue(CtrlNode):
    """Performs numpy.abs(<input>). Returns root-mean-square value if <input> is complex"""
    nodeName = 'AbsoluteValue'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'lineEdit', {'text': '', 'placeHolder': 'Data column to transform'})]

    def setAutoCompleter(self):
        autocompleter = QtWidgets.QCompleter(self.columns, self.ctrls['data_column'])
        self.ctrls['data_column'].setCompleter(autocompleter)
        self.ctrls['data_column'].setToolTip('\n'.join(self.columns))

    def processData(self, transmission: Transmission):
        self.columns = transmission.df.columns
        self.setAutoCompleter()
        if self.ctrls['Apply'].isChecked() is False:
            return

        data_column = self.ctrls['data_column'].text()

        t = transmission.copy()

        t.df[data_column] = t.df[data_column].apply(lambda x: np.abs(x))

        t.src.append({self.nodeName: data_column})

        return t


class LogTransform(CtrlNode):
    """Can perform various log transforms"""
    nodeName = 'LogTransform'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('transform', 'combo', {'values': ['log10', 'ln', 'modlog10']}),
                  ('data_column', 'lineEdit', {'text': '', 'placeHolder': 'Data column to transform'})]

    def setAutoCompleter(self):
        autocompleter = QtWidgets.QCompleter(self.columns, self.ctrls['data_column'])
        self.ctrls['data_column'].setCompleter(autocompleter)
        self.ctrls['data_column'].setToolTip('\n'.join(self.columns))

    def processData(self, transmission: Transmission):
        self.columns = transmission.df.columns
        self.setAutoCompleter()
        if self.ctrls['Apply'].isChecked() is False:
            return

        data_column = self.ctrls['data_column'].text()

        t = transmission.copy()

        transform = self.ctrls['transform'].currentText()

        if transform == 'log10':
            t.df[data_column] = t.df[data_column].apply(lambda x: np.log10(x))
            t.src.append({'log10': data_column})

        elif transform == 'ln':
            t.df[data_column] = t.df[data_column].apply(lambda x: np.log(x))
            t.src.append({'ln': data_column})

        elif transform == 'modlog10':
            logmod = lambda x: np.sign(x) * (np.log10(np.abs(x) + 1))
            t.df[data_column] = t.df[data_column].apply(logmod)
            t.src.append({'logmod': data_column})

        return t


class RFFT(CtrlNode):
    """Uses fftpack.rfft, 'Discrete Fourier transform of a real sequence.'
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html#scipy.fftpack.rfft
    """
    nodeName = 'RFFT'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'lineEdit', {'text': '', 'placeHolder': 'Data column to splice'})
                  ]

    def setAutoCompleter(self):
        autocompleter = QtWidgets.QCompleter(self.columns, self.ctrls['data_column'])
        self.ctrls['data_column'].setCompleter(autocompleter)
        self.ctrls['data_column'].setToolTip('\n'.join(self.columns))

    def processData(self, transmission: Transmission):
        self.columns = transmission.df.columns
        self.setAutoCompleter()
        if self.ctrls['Apply'].isChecked() is False:
            return

        t = transmission.copy()

        data_column = self.ctrls['data_column'].text()

        t.df['rfft'] = t.df[data_column].apply(fftpack.rfft)

        t.src.append({'fftpack.rfft': {'data_column': data_column}})

        return t


class iRFFT(CtrlNode):
    """Uses fftpack.irfft, 'Return inverse discrete Fourier transform of real sequence.'
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.irfft.html#scipy.fftpack.irfft

    Input must have an rfft column from the RFFT node.
    """
    nodeName = 'iRFFT'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return

        t = transmission.copy()

        t.df['irfft'] = t.df['rfft'].apply(fftpack.irfft)

        t.src.append({'fftpack.irfft': {'data_column': 'rfft'}})

        return t
