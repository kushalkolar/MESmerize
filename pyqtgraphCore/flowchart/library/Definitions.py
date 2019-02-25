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
from caiman.source_extraction.cnmf.utilities import detrend_df_f
from common import configuration


class AlignStims(CtrlNode):
    """Align Stimulus Definitions"""
    nodeName = 'AlignStims'
    # Cannot use QComboBox for Stim_type since it leads to a stack overflow in Node.__getattr__ when removing or clearing the combobox
    uiTemplate = [('Stim_Type', 'lineEdit', {'text': '', 'placeHolder': 'Enter Stimulus type'}),
                  ('Stimulus', 'lineEdit', {'placeHolder': 'Stimulus and/or Substim', 'text': ''}),
                  ('start_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('end_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('zero_pos', 'combo', {'values': ['start_offset', 'stim_end', 'stim_center']}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}})
        self.ctrls['Stim_Type'].returnPressed.connect(self.setAutoCompleter)

    def setAutoCompleter(self):
        stim_def = self.ctrls['Stim_Type'].text()
        try:
            stims = list(set([a for b in self.transmission.df[stim_def].tolist() for a in b]))
        except (KeyError, IndexError) as e:
            QtWidgets.QMessageBox.warning(None, 'Stimulus type not found',
                                          'The stimulus type which you have entered'
                                          ' does not exist in the incoming dataframe\n'
                                          + str(e))
            return
        autocompleter = QtWidgets.QCompleter(stims, self.ctrls['Stimulus'])
        self.ctrls['Stimulus'].setCompleter(autocompleter)
        self.ctrls['Stimulus'].setToolTip('\n'.join(stims))

    def _setAutoCompleterLineEdit(self):
        pass

    def processData(self, transmission: Transmission):
        self.transmission = transmission
        ac = QtWidgets.QCompleter(self.transmission.STIM_DEFS, self.ctrls['Stim_Type'])
        self.ctrls['Stim_Type'].setCompleter(ac)
        self.ctrls['Stim_Type'].setToolTip('\n'.join(self.transmission.STIM_DEFS))

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.transmission = transmission.copy()

        stim_def = self.ctrls['Stim_Type'].text()
        stim_tag = self.ctrls['Stimulus'].text()
        start_offset = self.ctrls['start_offset'].value()
        end_offset = self.ctrls['end_offset'].value()
        zero_pos = self.ctrls['zero_pos'].currentText()

        params = {'stim_def': stim_def,
                  'stim_tag': stim_tag,
                  'start_offset': start_offset,
                  'end_offset': end_offset,
                  'zero_pos': zero_pos
                  }

        t = Transmission.empty_df(self.transmission)  # empty_df(), self.transmission.src)
        for ix, r in transmission.df.iterrows():
            try:
                smap = r['stim_maps'][0][0][stim_def]
            except KeyError:
                continue
            curve = r['curve']
            if curve is None:
                continue
            for i, stim in smap.iterrows():
                stim_start = stim['start']
                stim_end = stim['end']

                if zero_pos == 'start_offset':

                    tstart = max(stim_start + start_offset, 0)
                    tend = min(stim_end + end_offset, len(curve) - 1)

                elif zero_pos == 'stim_end':
                    tstart = stim_end
                    tend = min(tstart + end_offset, len(curve) - 1)

                elif zero_pos == 'stim_center':
                    tstart = int(((stim_start + stim_end) / 2)) + start_offset
                    tend = min(stim_end + end_offset, len(curve) - 1)

                rn = r.copy()

                stim_extract = np.take(curve, np.arange(int(tstart), int(tend)))

                rn['curve'] = stim_extract

                rn[stim_def] = ['name']

                t.df = t.df.append(rn, ignore_index=True)

        t.src.append({'AlignStims': params})
        # print('ALIGN_STIMS APPENDED')
        # print(t.src)
        return t


class ROI_Selection(CtrlNode):
    """Pass-through DataFrame rows if they have the chosen tags"""
    nodeName = 'ROI_Selection'
    # Cannot use QComboBox for ROI_Type since it leads to a stack overflow in Node.__getattr__ when removing or clearing the combobox
    uiTemplate = [('ROI_Type', 'lineEdit', {'text': '', 'placeHolder': 'Enter ROI type'}),
                  ('availTags', 'label', {'toolTip': 'All tags found under this ROI_Def'}),
                  ('ROI_Tags', 'lineEdit', {'toolTip': 'Enter one or many tags separated by commas (,)\n' + \
                                                       'Spaces before or after commas do not matter'}),
                  ('Include', 'radioBtn', {'checked': True}),
                  ('Exclude', 'radioBtn', {'checked': False}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}})
        self.ctrls['ROI_Type'].returnPressed.connect(self._setAvailTags)

    def _setAvailTags(self):
        try:
            tags = list(set(self.transmission.df[self.ctrls['ROI_Type'].text()]))
        except (KeyError, IndexError) as e:
            QtWidgets.QMessageBox.warning(None, 'ROI type not found',
                                          'The ROI type which you have entered'
                                          ' does not exist in the incoming dataframe\n' + str(e))
            return
        self.ctrls['availTags'].setText(', '.join(tags))
        self.ctrls['availTags'].setToolTip('\n'.join(tags))
        self._setROITagAutoCompleter(tags)

    def _setROITagAutoCompleter(self, tags):
        ac = QtWidgets.QCompleter(tags, self.ctrls['ROI_Tags'])
        self.ctrls['ROI_Tags'].setCompleter(ac)

    def processData(self, transmission: Transmission):
        self.transmission = transmission
        ac = QtWidgets.QCompleter(self.transmission.ROI_DEFS, self.ctrls['ROI_Type'])
        self.ctrls['ROI_Type'].setCompleter(ac)
        self.ctrls['ROI_Type'].setToolTip('\n'.join(self.transmission.ROI_DEFS))

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.transmission = transmission.copy()

        chosen_tags = [tag.strip() for tag in self.ctrls['ROI_Tags'].text().split(',')]

        t = self.transmission.copy()
        '''***************************************************************************'''
        ## TODO: CHECK IF THIS IS ACTUALLY DOING THE RIGHT THING!!!!
        if self.ctrls['Include'].isChecked():
            t.df = t.df[t.df[self.ctrls['ROI_Type'].text()].isin(chosen_tags)]
            prefix = 'include tags'
        elif self.ctrls['Exclude'].isChecked():
            t.df = t.df[~t.df[self.ctrls['ROI_Type'].text()].isin(chosen_tags)]
            prefix = 'exclude tags'
        '''***************************************************************************'''

        params = {'ROI_DEF': self.ctrls['ROI_Type'].text(),
                  prefix: chosen_tags}

        t.src.append({'ROI_Include': params})

        return t


class PeakDetect(CtrlNode):
    """Detect peaks & bases by finding local maxima & minima. Use this after the Derivative Filter"""
    nodeName = 'Peak_Detect'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('Fictional_Bases', 'check', {'checked': False}),
                  ('Edit', 'button', {'text': 'Open Editor'}),
                  ('SlopeThr', 'doubleSpin', {'min': -100.00, 'max': 1.0, 'step': 0.010}),
                  ('AmplThrAbs', 'doubleSpin', {'min': 0.00, 'max': 100000.00, 'step': 100.00}),
                  ('AmplThrRel', 'doubleSpin', {'min': 0.00, 'max': 100000.00, 'step': 100.00})
                  ]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Derivative': {'io': 'in'},
                                                 'Curve': {'io': 'in'},
                                                 'Out': {'io': 'out', 'bypass': 'Curve'}}, **kwargs)
        self.data_modified = False
        self.editor_output = False
        self.ctrls['Edit'].clicked.connect(self._peak_editor)
        self.t = None

    def _get_zero_crossings(self, dsig: np.ndarray, fictional_bases: bool = False) -> pd.DataFrame:
        """
        Find the peaks and bases of the signal by finding zero crossing in the first derivative of the filtered signal
        :param dsig: The first derivative of the signal
        :return: DataFrame, all zero crossing events in one column, another column denotes it as a peak or base.
        """
        # Get array of all sign switches
        sc = np.diff(np.sign(dsig))

        peaks_raw = np.where(sc < 0)[0]
        bases = np.where(sc > 0)[0]

        # Remove all peaks where amplitude is below the specified threshold
        peak_yvals = np.take(self.t.df.iloc[self.row_ix]['raw_curve'], peaks_raw)
        # print('peak_yvals: ' + str(peak_yvals))
        ix_below_ampl_thr = np.where(peak_yvals < self.ctrls['AmplThrAbs'].value())
        # print('ix_below_ampl_thr: ' + str(ix_below_ampl_thr))
        peaks_ampl_thr = np.delete(peaks_raw, ix_below_ampl_thr)

        s2 = np.gradient(dsig)
        # Remove all peaks where the 2nd derivative is below a certain threshold
        peak_d2 = np.take(s2, peaks_ampl_thr)
        ix_below_slope_thr = np.where(peak_d2 > self.ctrls['SlopeThr'].value())
        # print('peak_d2: ' + str(peak_d2))
        # print('ix_below_slope_thr: ' + str(ix_below_slope_thr))
        peaks = np.delete(peaks_ampl_thr, ix_below_slope_thr)

        ## TODO; DEBATE ABOUT HOW TO PROPERLY DEAL WITH TRACES THAT HAVE NO PEAKS !!!!
        if peaks.size == 0:
            peaks = np.array([0])
            bases = np.array([0, 1])

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
        assert isinstance(peaks_bases_df, pd.DataFrame)
        peaks_bases_df = peaks_bases_df.sort_values('event')
        peaks_bases_df.reset_index(drop=True, inplace=True)

        peaks_bases_df['peak'] = peaks_bases_df['label'] == 'peak'
        peaks_bases_df['base'] = peaks_bases_df['label'] == 'base'

        # Set the peaks at the index of the local maxima of the raw curve instead of the approximate maxima inferred
        # from the derivative after .
        # Also remove peaks which are lower than the relative amplitude threshold
        rows_drop = []
        for ix, r in peaks_bases_df.iterrows():
            if r['peak'] and ix > 0:
                if peaks_bases_df.iloc[ix - 1]['base'] and peaks_bases_df.iloc[ix + 1]['base']:
                    ix_left_base = peaks_bases_df.iloc[ix - 1]['event']
                    ix_right_base = peaks_bases_df.iloc[ix + 1]['event']

                    #  Adjust the xval of the curve by finding the absolute maxima of this section of the raw curve,
                    # flanked by the bases of the peak
                    peak_revised = np.where(self.t.df.iloc[self.row_ix]['raw_curve'] == np.max(
                        np.take(self.t.df.iloc[self.row_ix]['raw_curve'], np.arange(ix_left_base, ix_right_base))))[0][0]

                    # Get rising and falling amplitudes
                    rise_ampl = self.t.df.iloc[self.row_ix]['raw_curve'][peak_revised] - self.t.df.iloc[self.row_ix]['raw_curve'][ix_left_base]
                    fall_ampl = self.t.df.iloc[self.row_ix]['raw_curve'][peak_revised] - self.t.df.iloc[self.row_ix]['raw_curve'][ix_right_base]

                    # Check if above relative amplitude threshold
                    if (rise_ampl + fall_ampl) > self.ctrls['AmplThrRel'].value():
                        peaks_bases_df.set_value(ix, 'event', peak_revised)
                    else:
                        rows_drop.append(ix)

        peaks_bases_df.drop(peaks_bases_df.index[rows_drop], inplace=True)
        peaks_bases_df.reset_index(drop=True, inplace=True)

        self.row_ix += 1
        # print(peaks_bases_df)
        return peaks_bases_df

    def process(self, display=True, **kwargs):
        out = self.processData(**kwargs)
        return {'Out': out}

    def processData(self, **inputs):
        if self.editor_output:
            return self.t

        if self.data_modified is True:
            if QtWidgets.QMessageBox.question(None, 'Discard peak edits?',
                                              'You have made modifications to peak data passing '
                                              'through this node! Would you like to discard all '
                                              'changes and load the newly transmitted data?',
                                              QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return self.t
        self.data_modified = False

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

        self.t = inputs['Derivative'].copy()

        selected = inputs['Curve'].copy()
        self.t.df['raw_curve'] = selected.df['curve']

        assert isinstance(self.t, Transmission)

        # self.t.data_column['peaks_bases'] = 'peaks_bases'
        fb = self.ctrls['Fictional_Bases'].isChecked()
        self.row_ix = 0
        self.t.df['peaks_bases'] = self.t.df['curve'].apply(lambda s: self._get_zero_crossings(s, fb))

        self.t.df['curve'] = self.t.df['raw_curve']
        self.t.df.drop(columns=['raw_curve'])

        if hasattr(self, 'pbw'):
            self.pbw.update_transmission(self.t, self.t)

        self.t.src.append({'Peak_Detect':
                           {'SlopeThr': self.ctrls['SlopeThr'].value(),
                            'AmplThrRel': self.ctrls['AmplThrRel'].value(),
                            'AmplThrAbs': self.ctrls['AmplThrAbs'].value()}})
        return self.t

    def _set_editor_output(self):
        self.pbw.close()
        self.editor_output = True
        self.t = self.pbw.getData()
        self.pbw = None
        self.data_modified = True
        self.changed()

    def _peak_editor(self):
        self.pbw = PeakEditor.PBWindow(self.t, self.t)
        self.pbw.show()
        self.pbw.btnDone.clicked.connect(self._set_editor_output)


class DeltaFoF(CtrlNode):
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('OpenGUI', 'button', {'text': 'Open GUI'})]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Derivative': {'io': 'in'},
                                                 'Curve': {'io': 'in'},
                                                 'Out': {'io': 'out', 'bypass': 'Curve'}}, **kwargs)
        self.data_modified = False
        self.editor_output = False
        self.ctrls['Edit'].clicked.connect(self._peak_editor)


class DetrendDFoF(CtrlNode):
    """Uses detrend_df_f from Caiman library"""
    nodeName = 'DetrendDFoF'
    uiTemplate=[('quantileMin', 'intSpin', {'min': 1, 'max': 100, 'step': 1, 'value': 20}),
                ('frames_window', 'intSpin', {'min': 2, 'max': 5000, 'step': 10, 'value': 100}),
                ('auto_quantile', 'check', {'checked': True, 'toolTip': 'determine quantile automatically'}),
                ('fast_filter', 'check', {'checked': True, 'tooTip': 'use approximate fast percentile filtering'}),
                ('Apply', 'check', {'applyBox': True, 'checked': False})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return
        t = transmission.copy()
        self.df = t.df

        self.params = {'quantileMin':  self.ctrls['quantileMin'].value(),
                       'frames_window': self.ctrls['frames_window'].value(),
                       'auto_quantile': self.ctrls['auto_quantile'].isChecked(),
                       'fast_filter':   self.ctrls['fast_filter'].isChecked()
                       }

        self._load_data()

        t.df = self.df.reset_index(drop=True)

        t.src.append({'DetrendDFoF': self.params})

        return t

    def _load_data(self):
        self.current_sample_id = None
        self.ix = 0
        dfof_curves = None

        proj_path = configuration.proj_path

        for index, row in self.df.iterrows():
            self.ix += 1

            if row['SampleID'] != self.current_sample_id:
                self.idx_components = None
                self.ix = 0

                self.current_sample_id = row['SampleID']

                pikPath = proj_path + row['ImgInfoPath']
                pik = pickle.load(open(pikPath, 'rb'))

                cnmA = pik['roi_states']['cnmf_output']['cnmA']
                cnmb = pik['roi_states']['cnmf_output']['cnmb']
                cnmC = pik['roi_states']['cnmf_output']['cnmC']
                cnm_f = pik['roi_states']['cnmf_output']['cnm_f']
                cnmYrA = pik['roi_states']['cnmf_output']['cnmYrA']

                self.idx_components = pik['roi_states']['cnmf_output']['idx_components']

                dfof_curves = detrend_df_f(cnmA, cnmb, cnmC, cnm_f, YrA=cnmYrA,
                                           quantileMin=self.params['quantileMin'],
                                           frames_window=self.params['frames_window'])#,
                                           # flag_auto=self.ctrls['auto_quantile'].isChecked(),
                                           # use_fast=self.ctrls['fast_filter'].isChecked())
                if self.idx_components[self.ix] != row['ROI_State']['cnmf_idx']:
                    raise Exception(
                        'CNMF component index Mismatch Error! Something went very wrong. Check the indices of your'
                        'CNMF components from SampleID: ' + self.current_sample_id)

            self.df.iloc[index]['curve'] = dfof_curves[self.idx_components[self.ix]]


class SpliceArrays(CtrlNode):
    """Splice 1-D numpy arrays in a particular column"""
    nodeName = 'SpliceArrays'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {}),
                  ('indices', 'lineEdit', {'text': '', 'placeHolder': 'start_ix:end_ix'})]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        t = transmission.copy()
        indices = self.ctrls['indices'].text()

        if indices == '':
            return
        if ':' not in indices:
            return
        else:
            indices = indices.split(':')

        start_ix = int(indices[0])
        end_ix = int(indices[1])

        data_column = self.ctrls['data_column'].currentText()

        t.df[data_column] = t.df[data_column].apply(lambda a: a[start_ix:end_ix])

        t.src.append({'SpliceArrays': {'data_column': data_column, 'start_ix': start_ix, 'end_ix': end_ix}})

        return t


class ManualDFoF(CtrlNode):
    """Set Fo for dF/Fo using a particular time period. Useful for looking at stimulus responses"""
    nodeName = 'ManualDFoF'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {}),
                  ('OpenGUI', 'button', {'text': 'OpenGUI'})]

