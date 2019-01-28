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
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return

        t = transmission.copy()

        t.df['curve'].values = transmission.df['curve'].values

        return np.abs(t)


class LogTransform(CtrlNode):
    """Can perform various log transforms"""
    nodeName = 'LogTransform'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('transform', 'combo', {'values': ['log10', 'ln', 'modlog10']}),
                  ('data_column', {'text': '', 'placeHolder': 'Data column to transform'})]

    def setAutoCompleter(self):
        autocompleter = QtWidgets.QCompleter(self.columns, self.ctrls['data_column'])
        self.ctrls['data_column'].setCompleter(autocompleter)
        self.ctrls['data_column'].setToolTip('\n'.join(self.data_columns))

    def processData(self, transmission: Transmission):
        self.columns = transmission.df.columns
        self.setAutoCompleter()
        if self.ctrls['Apply'].isChecked() is False:
            return

        data_column = self.ctrls['data_column'].text()

        t = transmission.copy()

        a = t.df[data_column].values
        #a = np.vstack(a)

        if self.ctrls['transform'].value is 'log10':
            t[data_column] = np.log10(a)

        elif self.ctrls['transform'].value is 'ln':
            t[data_column] = np.log(a)

        elif self.ctrls['transform'].value is 'modlog10':
            logmod = lambda x: np.sign(x) * (np.log10(np.abs(x) + 1))
            t[data_column] = logmod(a)

        return t


class RFFT(CtrlNode):
    """Uses fftpack.rfft, 'Discrete Fourier transform of a real sequence.'
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html#scipy.fftpack.rfft
    """
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return

        t = transmission.copy()

        a = transmission.df['rfft'].values

        return fftpack.rfft(a)


class iRFFT(CtrlNode):
    """Uses fftpack.irfft, 'Return inverse discrete Fourier transform of real sequence.'
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.irfft.html#scipy.fftpack.irfft
    """
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return

        a = transmission.df['irfft'].values

        return fftpack.irfft(a)

