# -*- coding: utf-8 -*-
import traceback
from PyQt5 import QtWidgets
from ....plotting.widgets.peak_editor import peak_editor
from .common import *
from ....analysis import Transmission
from scipy import signal
from scipy import fftpack
import pandas as pd
from ....analysis.compute_peak_features import ComputePeakFeatures
from ....common.configuration import HAS_TSLEARN
if HAS_TSLEARN:
    from tslearn.preprocessing import TimeSeriesScalerMeanVariance


class ButterWorth(CtrlNode):
    """Butterworth Filter"""
    nodeName = 'ButterWorth'
    uiTemplate = [('data_column', 'combo', {}),
                  ('order', 'intSpin', {'min': 1, 'max': 100, 'step': 1, 'value': 2}),
                  ('freq_divisor', 'doubleSpin', {'min': 0.01, 'max': 100.00, 'step': 0.05, 'value': 2.00}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    output_column = '_BUTTERWORTH'

    def _func(self, x: np.ndarray, meta: dict):
        N = self.ctrls['order'].value()
        freq = 1 / meta['fps']

        self.Wn = freq/self.freq_divisor

        b, a = signal.butter(N, self.Wn)
        sig = signal.filtfilt(b, a, x)

        return pd.Series({self.output_column: sig})

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'] is False:
            return

        self.t = transmission.copy()

        self.order = self.ctrls['order'].value()
        self.freq_divisor = self.ctrls['freq_divisor'].value()

        # try:
        tqdm.pandas()
        self.t.df[self.output_column] = self.t.df.progress_apply(lambda x: self._func(x[self.data_column], x['meta']), axis=1)
        # except KeyError as e:
        #     raise KeyError(str(e))

        params = {'data_column': self.data_column,
                  'order': self.order,
                  'Wn': self.Wn,
                  'freq_divider': self.freq_divisor,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='butterworth', parameters=params)
        self.t.last_output = self.output_column

        return self.t


class SavitzkyGolay(CtrlNode):  # Savitzky-Golay filter for example
    """Savitzky-Golay filter."""
    nodeName = 'Savitzky_Golay'
    uiTemplate = [('data_column', 'combo', {}),
                  ('window_length', 'intSpin', {'min': 3, 'max': 999, 'value': 3, 'step': 2}),
                  ('polyorder', 'intSpin', {'min': 1, 'max': 998, 'value': 1, 'step': 1}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        w = self.ctrls['window_length'].value()
        p = self.ctrls['polyorder'].value()

        if p > w:
            raise ValueError('Invalid value! polyorder MUST be less than window_length')

        if w % 2 == 0:
            raise ValueError('Invalid value! window_length MUST be an odd number!')

        output_column = '_SAVITZKY_GOLAY'

        tqdm.pandas()
        self.t.df[output_column] = self.t.df[self.data_column].progress_apply(signal.savgol_filter, window_length=w, polyorder=p)

        params = {'data_column': self.data_column,
                  'window_length': w,
                  'polyorder': p,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='savitzky_golay', parameters=params)
        self.t.last_output = output_column

        return self.t


class PowerSpectralDensity(CtrlNode):
    """Return the Power Spectral Density of a curve."""
    nodeName = 'PowSpecDens'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_POWER_SPECTRAL_DENSITY'

        tqdm.pandas()
        self.t.df[output_column] = self.t.df[self.data_column].progress_apply(self._func)

        params = {'data_column': self.data_column}
        self.t.history_trace.add_operation(data_block_id='all', operation='power_spectral_density', parameters=params)
        self.t.last_output = output_column

        return self.t

    def _func(self, curve):
        f, p = signal.periodogram(curve)
        return p


class Resample(CtrlNode):
    """
    Resample 1D data, uses scipy.signal.resample. "Rs" is the new sampling rate in "Tu" units of time.
    If "Tu" = 1, then Rs is the new sampling rate in Hertz.
    """

    nodeName = 'Resample'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Rs', 'intSpin', {'min': 1, 'max': 9999, 'value': 10, 'step': 5}),
                  ('Tu', 'intSpin', {'min': 1, 'max': 9999, 'value': 1, 'step': 1}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        self.Rs = self.ctrls['Rs'].value()
        self.Tu = self.ctrls['Tu'].value()
        self.new_rate = self.Rs / self.Tu

        output_column = '_RESAMPLE'

        tqdm.pandas()
        self.t.df[output_column] = self.t.df.progress_apply(self._func, axis=1)

        params = {'data_column': self.data_column,
                  'output_rate': self.new_rate,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='resample', parameters=params)
        self.t.last_output = output_column

        return self.t

    def _func(self, row: pd.Series):
        Nf = row['meta']['fps']
        if Nf == 0:
            raise ValueError('Framerate not set for SampleID: ' + row['SampleID']
                             + '. You must set a framerate for this SampleID to continue')
        Ns = row[self.data_column].shape[0]

        Rn = int((Ns / Nf) * (self.new_rate))

        return signal.resample(row[self.data_column], Rn)


class ScalerMeanVariance(CtrlNode):
    """Scaler for time series. Scales time series so that their mean (resp. standard deviation) in each dimension is mu (resp. std).\n
    See https://tslearn.readthedocs.io/en/latest/gen_modules/preprocessing/tslearn.preprocessing.TimeSeriesScalerMeanVariance.html#tslearn.preprocessing.TimeSeriesScalerMeanVariance"""
    nodeName = 'ScalerMeanVar'
    uiTemplate = [('data_column', 'combo', {}),
                   ('mu', 'doubleSpin', {'value': 0.0, 'step': 0.1, 'toolTip': 'Mean of the output time series'}),
                   ('std', 'doubleSpin', {'value': 1.0, 'step': 1.0, 'toolTip': 'Standard deviation of the output time series'}),
                   ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        mu = self.ctrls['mu'].value()
        std = self.ctrls['std'].value()

        params = {'data_column': self.data_column,
                  'mu': mu,
                  'std': std,
                  'units': self.t.last_unit
                  }

        output_column = '_SCALER_MEAN_VARIANCE'

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda a: TimeSeriesScalerMeanVariance(mu=mu, std=std).fit_transform(a)[:, :, 0])
        self.t.history_trace.add_operation(data_block_id='all', operation='scaler_mean_variance', parameters=params)
        self.t.last_output = output_column

        return self.t


class Normalize(CtrlNode):
    """Normalize a column containing 1-D arrays such that values in each array are normalized between 0 and 1\n
    Output Column -> Input Column"""

    nodeName = 'Normalize'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_NORMALIZE'

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda a: ((a - np.min(a)) / (np.max(a - np.min(a)))))

        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='normalize', parameters=params)
        self.t.last_output = output_column

        return self.t


class RFFT(CtrlNode):
    """
    Uses fftpack.rfft, 'Discrete Fourier transform of a real sequence.\n
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.rfft.html#scipy.fftpack.rfft
    """
    nodeName = 'RFFT'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        # TODO: Replace this code block with the DataTypes.get_framerate() method
        ##############################################################################################################
        sampling_rates = []

        for db in transmission.history_trace.data_blocks:
            if transmission.history_trace.check_operation_exists(db, 'resample'):
                sampling_rates.append(transmission.history_trace.get_operation_params(db, 'resample')['output_rate'])
            else:
                r = pd.DataFrame(transmission.get_data_block_dataframe(db).meta.to_list())['fps'].unique()
                # if rates.size > 1:
                #     raise ValueError("Sampling rates for the data do not match")
                # else:
                sampling_rates.append(r)

        rates = np.hstack([sampling_rates])

        if np.ptp(rates) > 0.1:
            raise ValueError("Sampling rates of the data differ by greater than the tolerance of 0.1 Hz")

        framerate = int(np.mean(sampling_rates))
        ##############################################################################################################

        array_size = transmission.df[self.data_column].apply(lambda a: a.size).unique()

        if array_size.size > 1:
            raise ValueError("Size of all arrays in data column must match exactly.")

        array_size = array_size[0]

        freqs = fftpack.rfftfreq(array_size) * framerate

        self.t = transmission.copy()

        output_column = '_RFFT'

        self.t.df[output_column] = self.t.df[self.data_column].apply(fftpack.rfft)

        self.t.last_unit = 'frequency'

        params = {'data_column':    self.data_column,
                  'frequencies':    freqs.tolist(),
                  'sampling_rate':  framerate,
                  'nyquist_frequency': float(freqs.max()),
                  'units': 'frequency'
                  }

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
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_IRFFT'

        self.t.df[output_column] = self.t.df['_RFFT'].apply(fftpack.irfft)
        self.t.last_unit = 'time'

        params = {'data_column': '_RFFT',
                  'units': 'time'
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='irfft', parameters=params)
        self.t.last_output = output_column

        return self.t


class PeakDetect(CtrlNode):
    """Detect peaks & bases by finding local maxima & minima. Use this after the Derivative Filter"""
    nodeName = 'PeakDetect'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Fictional_Bases', 'check', {'checked': True}),
                  ('Edit', 'button', {'text': 'Open GUI'}),
                  ('SlopeThr', 'doubleSpin', {'min': -100.00, 'max': 1.0, 'step': 0.010}),
                  ('AmplThrAbs', 'doubleSpin', {'min': 0.00, 'max': 9999.00, 'step': 0.05}),
                  ('AmplThrRel', 'doubleSpin', {'min': 0.00, 'max': 9999.00, 'step': 0.05}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Derivative': {'io': 'in'},
                                                 'Normalized': {'io': 'in'},
                                                 'Curve': {'io': 'in'},
                                                 'PB_Input': {'io': 'in'},
                                                 'Out': {'io': 'out', 'bypass': 'Curve'}}, **kwargs)
        self.data_modified = False
        self.editor_output = False
        self.pbw = None
        self.ctrls['Edit'].clicked.connect(self._peak_editor)
        self.t = None
        self.params = {}

    def _get_zero_crossings(self, d1: np.ndarray, sig: np.ndarray, norm_sig: np.ndarray, fictional_bases: bool = False) -> pd.DataFrame:
        """
        Find the peaks and bases of the signal by finding zero crossing in the first derivative of the filtered signal
        :param dsig: The first derivative of the signal
        :return: DataFrame, all zero crossing events in one column, another column denotes it as a peak or base.
        """
        # Get array of all sign switches
        sc = np.diff(np.sign(d1))

        peaks_raw = np.where(sc < 0)[0]
        bases = np.where(sc > 0)[0]

        # Remove all peaks where amplitude is below the specified threshold
        peak_yvals = np.take(norm_sig, peaks_raw)
        # print('peak_yvals: ' + str(peak_yvals))
        ix_below_ampl_thr = np.where(peak_yvals < self.ctrls['AmplThrAbs'].value())
        # print('ix_below_ampl_thr: ' + str(ix_below_ampl_thr))
        peaks_ampl_thr = np.delete(peaks_raw, ix_below_ampl_thr)

        s2 = np.gradient(d1)
        # Remove all peaks where the 2nd derivative is below a certain threshold
        peak_d2 = np.take(s2, peaks_ampl_thr)
        ix_below_slope_thr = np.where(peak_d2 > self.ctrls['SlopeThr'].value())
        # print('peak_d2: ' + str(peak_d2))
        # print('ix_below_slope_thr: ' + str(ix_below_slope_thr))
        peaks = np.delete(peaks_ampl_thr, ix_below_slope_thr)

        ## TODO; DEBATE ABOUT HOW TO PROPERLY DEAL WITH TRACES THAT HAVE NO PEAKS
        if peaks.size == 0:
            # abort = True
            # peaks = np.array([1])
            # bases = np.array([0, 2])
            return pd.DataFrame()
        # else:
        #     self.row_ix += 1
        #     return pd.DataFrame()

        # Add bases to beginning and end of sequence if first or last peak is lonely
        if fictional_bases:
            if bases.size == 0:
                bases = np.array([0, sc.size])
            else:
                if bases[0] > peaks[0]:
                    bases = np.insert(bases, 0, 0)

                if bases[-1] < peaks[-1]:
                    bases = np.insert(bases, -1, sc.size)

        # Construct peak & base columns on dataframe
        peaks_df = pd.DataFrame()
        peaks_df['event'] = peaks
        peaks_df['label'] = 'peak'

        bases_df = pd.DataFrame()
        bases_df['event'] = bases
        bases_df['label'] = 'base'

        peaks_bases_df = pd.concat([peaks_df, bases_df])
        peaks_bases_df = peaks_bases_df.sort_values('event')
        peaks_bases_df.reset_index(drop=True, inplace=True)

        # if abort:
        #     self.row_ix += 1
        #     warn(f'No peaks detected at index: {self.row_ix}')
        #     return peaks_bases_df

        # peaks_bases_df['peak'] = peaks_bases_df['label'] == 'peak'
        # peaks_bases_df['base'] = peaks_bases_df['label'] == 'base'

        # Set the peaks at the index of the local maxima of the raw curve instead of the maxima inferred
        # from the derivative
        # Also remove peaks which are lower than the relative amplitude threshold
        rows_drop = []
        for ix, r in peaks_bases_df.iterrows():
            if r['label'] == 'peak' and ix > 0:
                if peaks_bases_df.iloc[ix - 1]['label'] == 'base' and peaks_bases_df.iloc[ix + 1]['label'] == 'base':
                    ix_left_base = peaks_bases_df.iloc[ix - 1]['event']
                    ix_right_base = peaks_bases_df.iloc[ix + 1]['event']

                    #  Adjust the xval of the curve by finding the absolute maxima of this section of the raw curve,
                    # flanked by the bases of the peak
                    peak_revised = np.where(sig == np.max(
                        np.take(sig, np.arange(ix_left_base, ix_right_base))))[0][0]

                    # Get rising and falling amplitudes
                    rise_ampl = sig[peak_revised] - sig[ix_left_base]
                    fall_ampl = sig[peak_revised] - sig[ix_right_base]

                    # Check if above relative amplitude threshold
                    if ((rise_ampl + fall_ampl) / 2) > self.ctrls['AmplThrRel'].value():
                        peaks_bases_df.set_value(ix, 'event', peak_revised)
                    else:
                        rows_drop.append(ix)

        peaks_bases_df = peaks_bases_df.drop(peaks_bases_df.index[rows_drop])
        peaks_bases_df = peaks_bases_df.reset_index(drop=True)

        # remove bases that aren't around any peak
        for ix, r in peaks_bases_df.iterrows():
            if r['label'] == 'base' and 1 < ix < (peaks_bases_df.index.size - 1):
                if peaks_bases_df.iloc[ix - 1]['label'] != 'peak' and peaks_bases_df.iloc[ix + 1]['label'] != 'peak':
                    rows_drop.append(ix)

        # Weird behavior dealing with bases at the end of a curve
        try:
            peaks_bases_df = peaks_bases_df.drop(peaks_bases_df.index[rows_drop])
            peaks_bases_df = peaks_bases_df.reset_index(drop=True)
        except:
            pass

        self.row_ix += 1
        # print(peaks_bases_df)
        return peaks_bases_df

    def process(self, display=True, **kwargs):
        out = self.processData(**kwargs)
        return {'Out': out}

    def processData(self, **inputs):
        if self.editor_output:
            return self.t

        pb_input = inputs['PB_Input']
        if isinstance(pb_input, Transmission):
            self.t = pb_input
            self.t.df.reset_index(drop=True, inplace=True)
            if self.pbw is None:
                self._peak_editor()
            else:
                self.pbw.update_transmission(self.t, self.t)
            self.pbw.btnDisconnectFromFlowchart.setDisabled(True)
            return self.t

        columns = inputs['Curve'].df.columns.to_list()
        self.ctrls['data_column'].setItems(organize_dataframe_columns(columns)[0])

        if self.data_modified is True:
            if QtWidgets.QMessageBox.question(None, 'Discard peak edits?',
                                              'You have made modifications to peak data passing '
                                              'through this node! Would you like to discard all '
                                              'changes and load the newly transmitted data?',
                                              QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return self.t
        self.data_modified = False

        if not self.ctrls['Apply'].isChecked():
            return
        # if inputs['Derivative'] is None:
        #     raise Exception('No incoming Derivative transmission. '
        #                     'You must input at least a derivative')
        #
        # self.t = inputs['Derivative'].copy()
        #
        # if inputs['Curve'] is not None:
        #     if inputs['Derivative'].df.index.size != inputs['Curve'].df.index.size:
        #         QtWidgets.QMessageBox.warning(None, 'ValueError!', 'Input diemensions of Derivative and Curve transmissions'
        #                                                        ' MUST match!')
        #         raise ValueError('Input diemensions of Derivative and Curve transmissions MUST match!')

        if inputs['Derivative'] is None:
            raise KeyError('No incoming Derivative transmission. '
                           'You must input both a curve and its derivative '
                           'You must input at least a derivative')

        if inputs['Curve'] is None:
            raise KeyError('No incoming Curve transmission.'
                           ' You must input both a curve and its derivative')

        if inputs['Derivative'].df.index.size != inputs['Curve'].df.index.size:
            raise ValueError('Input diemensions of Derivative and Curve transmissions MUST match!')

        t_d1 = inputs['Derivative'].copy()
        assert isinstance(t_d1, Transmission)
        d1 = t_d1.df['_DERIVATIVE']

        t_norm = inputs['Normalized'].copy()
        assert isinstance(t_norm, Transmission)
        norm_series = t_norm.df[t_norm.last_output]

        self.t = inputs['Curve'].copy()
        self.t.df['_DERIVATIVE'] = d1
        self.t.df['_NORM_PD'] = norm_series
        data_column = self.ctrls['data_column'].currentText()
        # self.t.df['raw_curve'] = self.t.df[data_column]

        assert isinstance(self.t, Transmission)

        # self.t.data_column['peaks_bases'] = 'peaks_bases'
        fb = self.ctrls['Fictional_Bases'].isChecked()
        self.row_ix = 0

        tqdm.pandas()
        self.t.df['peaks_bases'] = self.t.df.progress_apply(lambda r: self._get_zero_crossings(r['_DERIVATIVE'], r[data_column], r['_NORM_PD'], fb), axis=1)

        self.t.df['curve'] = self.t.df[data_column]
        self.t.df.drop(columns=['_NORM_PD'], inplace=True)
        self.t.df.reset_index(inplace=True, drop=True)
        # self.t.df.drop(columns=['raw_curve'])

        if self.pbw is not None:
            # self.pbw.curve_column = data_column
            self.pbw.update_transmission(self.t, self.t)

        params = {'data_column': data_column,
                  'SlopeThr': self.ctrls['SlopeThr'].value(),
                  'AmplThrRel': self.ctrls['AmplThrRel'].value(),
                  'AmplThrAbs': self.ctrls['AmplThrAbs'].value(),
                  'derivative_input_history_trace': t_d1.history_trace.get_all_data_blocks_history(),
                  'normalized_input_history_trace': t_norm.history_trace.get_all_data_blocks_history(),
                  'units': self.t.last_unit
                  }

        self.params = params

        self.t.history_trace.add_operation('all', operation='peak_detect', parameters=params)

        return self.t

    def _set_editor_output(self, edited_transmission: Transmission):
        self.t = edited_transmission
        self.t.history_trace.add_operation('all', operation='peak_detect', parameters=self.params)
        self.editor_output = True
        self.data_modified = True
        # self.pbw.close()
        # self.editor_output = True
        # self.t = self.pbw.getData()
        # self.pbw = None
        # self.data_modified = True
        self.changed()

    def _peak_editor(self):
        if self.pbw is None:
            self.pbw = peak_editor.PeakEditorWindow(self.t, self.t)
            self.pbw.sig_send_data.connect(self._set_editor_output)
            self.pbw.sig_reconnect_flowchart.connect(self.changed)
            self.pbw.setWindowTitle(self.name())

        self.pbw.show()


class PeakFeatures(CtrlNode):
    """Extract peak features after peak detection"""
    nodeName = 'PeakFeatures'
    uiTemplate = [('data_column', 'combo', {}),
                  # ('Compute', 'button', {'text': 'compute'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def __init__(self, *args, **kwargs):
        super(PeakFeatures, self).__init__(*args, **kwargs)
        self.peak_results = None

    def processData(self, transmission: Transmission):
        dcols = organize_dataframe_columns(transmission.df.columns)[0]
        self.ctrls['data_column'].setItems(dcols)

        if not self.apply_checked():
            return

        self.computer = ComputePeakFeatures()

        self.t = self.computer.compute(transmission=transmission.copy(), data_column=self.data_column)

        params = {'data_column': self.data_column}
        self.t.history_trace.add_operation('all', 'peak-features', params)

        # Data units cannot be relied on anymore since any user specifid data column
        # can be used for computing peak features
        self.t.last_output = None

        return self.t


class SigmaMAD(CtrlNode):
    nodeName = 'SigmaMAD'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'applyBox': True, 'checked': True})
                  ]

    def processData(self, transmission: Transmission):
        dcols = organize_dataframe_columns(transmission.df.columns)[0]
        self.ctrls['data_column'].setItems(dcols)

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        output_column = '_' + self.__class__.__name__.upper()
        params = {'data_column': self.data_column}

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.median(np.abs(x - np.median(x))))
        self.t.history_trace.add_operation('all', self.__class__.__name__.lower(), params)

        return self.t
