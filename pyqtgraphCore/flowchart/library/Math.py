# -*- coding: utf-8 -*-
import numpy as np
from .common import *
from analyser.DataTypes import Transmission
from scipy import signal
from functools import partial
from scipy import fftpack


class AbsoluteValue(CtrlNode):
    """Performs numpy.abs(<input>). Returns root-mean-square value if <input> is complex\n
    Output Column -> _abs"""
    nodeName = 'AbsoluteValue'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {})]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        data_column = self.ctrls['data_column'].currentText()

        self.t = transmission.copy()

        self.t.df['_abs'] = self.t.df[data_column].apply(lambda x: np.abs(x))

        self.t.src.append({self.nodeName: data_column})

        return self.t


class LogTransform(CtrlNode):
    """Can perform various log transforms\n
    Output Column -> _log_transform"""
    nodeName = 'LogTransform'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('transform', 'combo', {'values': ['log10', 'ln', 'modlog10']}),
                  ('data_column', 'combo', {})]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        data_column = self.ctrls['data_column'].currentText()

        self.t = transmission.copy()

        transform = self.ctrls['transform'].currentText()

        if transform == 'log10':
            self.t.df['_log_transform'] = self.t.df[data_column].apply(lambda x: np.log10(x))
            self.t.src.append({'log10': data_column})

        elif transform == 'ln':
            self.t.df['_log_transform'] = self.t.df[data_column].apply(lambda x: np.log(x))
            self.t.src.append({'ln': data_column})

        elif transform == 'modlog10':
            logmod = lambda x: np.sign(x) * (np.log10(np.abs(x) + 1))
            self.t.df['_log_transform'] = self.t.df[data_column].apply(logmod)
            self.t.src.append({'logmod': data_column})

        return self.t


class RFFT(CtrlNode):
    """Uses fftpack.rfft, 'Discrete Fourier transform of a real sequence.\n
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html#scipy.fftpack.rfft\n
    Output Column -> _rfft
    """
    nodeName = 'RFFT'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {})
                  ]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        data_column = self.ctrls['data_column'].currentText()

        self.t.df['_rfft'] = self.t.df[data_column].apply(fftpack.rfft)

        self.t.src.append({'fftpack.rfft': {'data_column': data_column}})

        return self.t


class iRFFT(CtrlNode):
    """Uses fftpack.irfft, 'Return inverse discrete Fourier transform of real sequence.'\n
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.irfft.html#scipy.fftpack.irfft\n
    Input must have an _rfft column from the RFFT node.\n
    Output Column -> _irfft
    """
    nodeName = 'iRFFT'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        self.t.df['_irfft'] = self.t.df['_rfft'].apply(fftpack.irfft)

        self.t.src.append({'fftpack.irfft': {'data_column': '_rfft'}})

        return self.t
