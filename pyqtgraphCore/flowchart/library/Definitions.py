# -*- coding: utf-8 -*-
import numpy as np
from ...Qt import QtCore, QtGui
from ..Node import Node
from . import functions
from ... import functions as pgfn
from .common import *
from ...python2_3 import xrange
from ... import PolyLineROI
from ... import Point
from ... import metaarray as metaarray
from analyser.DataTypes import *
from MesmerizeCore.misc_funcs import empty_df
from MesmerizeCore import configuration
from functools import partial
from analyser import PeakEditor
from analyser import Extraction
from analyser.HistoryWidget import HistoryTreeWidget
configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
configuration.openConfig()


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
            QtGui.QMessageBox.warning(None, 'Stimulus type not found',
                                      'The stimulus type which you have entered'
                                      ' does not exist in the incoming dataframe\n'
                                      + str(e))
            return
        autocompleter = QtGui.QCompleter(stims, self.ctrls['Stimulus'])
        self.ctrls['Stimulus'].setCompleter(autocompleter)
        self.ctrls['Stimulus'].setToolTip('\n'.join(stims))

    def _setAutoCompleterLineEdit(self):
        pass

    def processData(self, transmission):
        assert isinstance(transmission, Transmission)
        self.transmission = transmission
        ac = QtGui.QCompleter(self.transmission.STIM_DEFS, self.ctrls['Stim_Type'])
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

        t = Transmission.empty_df(self.transmission)#empty_df(), self.transmission.src)
        for ix, r in self.transmission.df.iterrows():
            try:
                smap = r['stimMaps'].flatten()[0][stim_def]
                # print(smap)
            except KeyError:
                continue
            # print(r)
            curve = r['curve']
            for stim in smap:
                if stim_tag in stim[0][0]:
                    if curve is None:
                        continue
                    stim_start = stim[-1][0]
                    stim_end = stim[-1][1]

                    if zero_pos == 'start_offset':

                        tstart = max(stim_start + start_offset, 0)
                        tend = min(stim_end + end_offset, len(curve))

                    elif zero_pos == 'stim_end':
                        tstart = stim_end
                        tend = tstart + end_offset

                    elif zero_pos == 'stim_center':
                        tstart = int(((stim_start + stim_end) / 2)) + start_offset
                        tend = min(stim_end + end_offset, len(curve))

                    rn = r.copy()
                    # stim_extract = curve[int(tstart):int(tend)]
                    stim_extract = np.take(curve, np.arange(int(tstart), int(tend)))
                    rn['curve'] = stim_extract / np.min(stim_extract)
                    rn[stim_def] = stim[0][0]
                    #
                    t.df = t.df.append(rn, ignore_index=True)

        t.src.append({'AlignStims': params})
        # print('ALIGN_STIMS APPENDED')
        # print(t.src)
        return t


class DF_IDX(CtrlNode):
    """Pass only one or multiple DataFrame Indices"""
    nodeName = 'DF_IDX'
    uiTemplate = [('Index', 'intSpin', {'min': 0, 'step': 1, 'value': 0}),
                  ('Indices', 'lineEdit', {'text': '0', 'toolTip': 'Index numbers separated by commas'})
                  ]

    def processData(self, transmission):
        self.ctrls['Index'].setMaximum(len(transmission.df.index) - 1)
        self.ctrls['Index'].valueChanged.connect(
            partial(self.ctrls['Indices'].setText, str(self.ctrls['Index'].value())))

        indices = [int(ix.strip()) for ix in self.ctrls['Indices'].text().split(',')]
        t = transmission.copy()
        t.df = t.df.iloc[indices, :]
        t.src.append({'DF_IDX': {'indices': indices}})
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
            QtGui.QMessageBox.warning(None, 'ROI type not found',
                                      'The ROI type which you have entered'
                                      ' does not exist in the incoming dataframe\n' + str(e))
            return
        self.ctrls['availTags'].setText(', '.join(tags))
        self.ctrls['availTags'].setToolTip('\n'.join(tags))
        self._setROITagAutoCompleter(tags)

    def _setROITagAutoCompleter(self, tags):
        ac = QtGui.QCompleter(tags, self.ctrls['ROI_Tags'])
        self.ctrls['ROI_Tags'].setCompleter(ac)

    def processData(self, transmission):
        assert isinstance(transmission, Transmission)
        self.transmission = transmission
        ac = QtGui.QCompleter(self.transmission.ROI_DEFS, self.ctrls['ROI_Type'])
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


class CaPreStats(CtrlNode):
    """Converge incoming transmissions and label what groups they belong to"""
    nodeName = 'CaPreStats'
    uiTemplate = [('SetGrps', 'button', {'text': 'Set Groups'}),
                  ('Save', 'button', {'text': 'Save Groups'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}, 'Out': {'io': 'Out'}})

    def process(self, **kwargs):
        transmissions = kwargs['In']
        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        for t in transmissions.items():
            t = t[1]

            if t is None:
                raise IndexError('One of your incoming tranmissions is None')


class PeakFeaturesExtract(CtrlNode):
    """Extract peak features. Use this after the Peak_Detect node."""
    nodeName = 'Peak_Features'
    uiTemplate = [('Extract', 'button', {'text': 'Compute'}),
                  ('Stats', 'button', {'text': 'Statistics/Plotting'})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True},
                                                 'Out': {'io': 'out'}})
        self.ctrls['Extract'].clicked.connect(self._extract)
        self.ctrls['GroupData'].setEnabled(False)
        self.ctrls['GroupData'].clicked.connect(self._open_stats_gui)
        self.peak_results = None

    def process(self, **kwargs):
        self.kwargs = kwargs.copy()
        return {'Out': self.peak_results}

    def _extract(self):
        if self.kwargs is None:
            self.peak_results = None
            return

        transmissions = self.kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        self.peak_results = []
        self.srcs = []
        for t in transmissions.items():
            t = t[1]
            if t is None:
                continue
                QtGui.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
            elif not any('Peak_Detect' in d for d in t.src):
                raise IndexError('Peak data not found in incoming DataFrame! You must first pass through '
                                 'a Peak_Detect node before this one.')
            t = t.copy()
            try:
                pf = Extraction.PeakFeaturesIter(t)
                tran_with_features = pf.get_all()

                self.srcs.append(tran_with_features.src)
                self.peak_results.append(tran_with_features)

            except Exception as e:
                QtGui.QMessageBox.warning(None, 'Error computing', 'The following error occured during peak extraction:\n'
                                                                   + str(e))

        self.changed()
        self.ctrls['GroupData'].setEnabled(True)

    def _open_stats_gui(self):
        if hasattr(self, 'stats_gui'):
            self.history_widget.show()
            return
        self.history_widget = HistoryTreeWidget()
        self.history_widget.fill_widget(self.srcs)
        self.history_widget.show()



class Universal_Statistics_Of_Type_ANOVA_For_Example(CtrlNode):
    """Takes in a transmission that comes from certain types of nodes that output data
    which can be used by this node to do the final stats and draw plots."""
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, **kwargs):
        pass


# class StatsPlots(CtrlNode):
#     """Perform statistics and draw plots"""

# TODO: BASED ON PARAMETERS DESCRIBED BY THAT UNI OF MARYLAND PROF. SUCH AS MINIMUM SLOPE AND AMPLITUDE ETC.
class PeakDetect(CtrlNode):
    """Detect peaks & bases by finding local maxima & minima. Use this after the Derivative Filter"""
    nodeName = 'Peak_Detect'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('Edit', 'button', {'text': 'Open Editor'}),
                  ('SlopeThr', 'label', {'text': ''}),
                  ('AmpThr', 'label', {'text': ''})
                  ]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Derivative': {'io': 'in'},
                                                 'Curve': {'io': 'in'},
                                                 'Out': {'io': 'out', 'bypass': 'Curve'}}, **kwargs)
        self.data_modified = False
        self.editor_output = False
        self.ctrls['Edit'].clicked.connect(self._peak_editor)
        self.t = None

    @staticmethod
    def _get_zero_crossings(dsig):
        """
        Determine the peaks and bases of the signal by finding zero crossing in the first derivative of the signal
        :param dsig: The first derivative of the signal
        :type dsig: np.array
        :return: DataFrame, all zero crossing events in one column, another column denotes it as a peak or base.
        :rtype: pd.DataFrame
        """
        sc = np.diff(np.sign(dsig))

        peaks = np.where(sc < 0)[0]
        bases = np.where(sc > 0)[0]

        peaks_df = pd.DataFrame()
        peaks_df['event'] = peaks
        peaks_df['label'] = 'peak'

        bases_df = pd.DataFrame()
        bases_df['event'] = bases
        bases_df['label'] = 'base'

        peaks_bases_df = pd.concat([peaks_df, bases_df])
        assert isinstance(peaks_bases_df, pd.DataFrame)
        peaks_bases_df = peaks_bases_df.sort_values('event')
        peaks_bases_df = peaks_bases_df.reset_index(drop=True)

        peaks_bases_df['peak'] = peaks_bases_df['label'] == 'peak'
        peaks_bases_df['base'] = peaks_bases_df['label'] == 'base'

        # print(peaks_bases_df)

        return peaks_bases_df

    def process(self, display=True, **kwargs):
        out = self.processData(**kwargs)
        return {'Out': out}

    def processData(self, **inputs):
        if self.editor_output:
            return self.t

        if self.data_modified is True:
            if QtGui.QMessageBox.question(None, 'Discard peak edits?',
                                          'You have made modifications to peak data passing '
                                          'through this node! Would you like to discard all '
                                          'changes and load the newly transmitted data?',
                                          QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                return self.t
        self.data_modified = False

        if inputs['Derivative'] is None:
            raise Exception('No incoming Derivative transmission. '
                            'You must input at least a derivative')


        self.t = inputs['Derivative'].copy()

        if inputs['Curve'] is not None:
            if inputs['Derivative'].df.index.size != inputs['Curve'].df.index.size:
                QtGui.QMessageBox.warning(None, 'ValueError!', 'Input diemensions of Derivative and Curve transmissions'
                                                               ' MUST match!')
                raise ValueError('Input diemensions of Derivative and Curve transmissions MUST match!')

            selected = inputs['Curve'].copy()
            self.t.df['raw_curve'] = selected.df['curve']
            selected = None
            on_raw = False
        else:
            on_raw = True

        assert isinstance(self.t, Transmission)

        # self.t.data_column['peaks_bases'] = 'peaks_bases'
        self.t.df['peaks_bases'] = self.t.df['curve'].apply(lambda s: PeakDetect._get_zero_crossings(s))

        self.t.df['curve'] = self.t.df['raw_curve']
        self.t.df.drop(columns=['raw_curve'])

        if hasattr(self, 'pbw'):
            self.pbw.update_transmission(self.t, self.t)

        self.t.src.append({'Peak_Detect': {'SlopeThr': 'Not Implemented', 'AmpThr': 'Not Implemented', 'on_raw': on_raw}})
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
