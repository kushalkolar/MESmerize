# -*- coding: utf-8 -*-
import numpy as np
from .common import *
from analyser.DataTypes import Transmission
from scipy import signal
from functools import partial
from scipy import fftpack


class AbsoluteValue(CtrlNode):
    """Performs numpy.abs(<input>). Returns root-mean-square value if <input> is complex"""
    nodeName = 'AbsoluteValue'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        output_column = '_ABSOLUTE_VALUE'

        self.t = transmission.copy()

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.abs(x))

        params = {'data_column': self.data_column}
        self.t.history_trace.add_operation(data_block_id='all', operation='absolute_value', parameters=params)
        self.t.last_output = output_column

        return self.t


class LogTransform(CtrlNode):
    """Can perform various log transforms"""
    nodeName = 'LogTransform'
    uiTemplate = [('data_column', 'combo', {}),
                  ('transform', 'combo', {'values': ['log10', 'ln', 'modlog10']}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_LOG_TRANSFORM'

        transform = self.ctrls['transform'].currentText()
        params = {'data_column': self.data_column,
                  'transform': transform}

        if transform == 'log10':
            self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.log10(x))

        elif transform == 'ln':
            self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.log(x))

        elif transform == 'modlog10':
            logmod = lambda x: np.sign(x) * (np.log10(np.abs(x) + 1))
            self.t.df[output_column] = self.t.df[self.data_column].apply(logmod)

        self.t.history_trace.add_operation(data_block_id='all', operation='log_transform', parameters=params)
        self.t.last_output = output_column

        return self.t


class RFFT(CtrlNode):
    """
    Uses fftpack.rfft, 'Discrete Fourier transform of a real sequence.\n
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html#scipy.fftpack.rfft
    """
    nodeName = 'RFFT'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_RFFT'

        self.t.df[output_column] = self.t.df[self.data_column].apply(fftpack.rfft)

        params = {'data_column': self.data_column}
        self.t.history_trace.add_operation(data_block_id='all', operation='rfft', parameters=params)
        self.t.last_output = output_column

        return self.t


class iRFFT(CtrlNode):
    """
    Uses fftpack.irfft, 'Return inverse discrete Fourier transform of real sequence.'\n
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.irfft.html#scipy.fftpack.irfft\n
    Input must have an _RFFT column from the RFFT node.\n
    """
    nodeName = 'iRFFT'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_IRFFT'

        self.t.df[output_column] = self.t.df['_RFFT'].apply(fftpack.irfft)

        params = {'data_column': '_RFFT'}
        self.t.history_trace.add_operation(data_block_id='all', operation='irfft', parameters=params)
        self.t.last_output = output_column

        return self.t
