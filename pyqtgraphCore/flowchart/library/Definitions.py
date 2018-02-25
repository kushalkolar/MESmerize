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


configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
configuration.openConfig()

class AlignStims(CtrlNode):
    """Align Stimulus Definitions"""
    nodeName = 'AlignStims'
    uiTemplate = [('Stimulus_Type', 'combo', {'values': []}),
                  ('Stimulus', 'lineEdit', {'placeHolder': 'Stimulus and/or Substim', 'text': ''}),
                  ('start_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('end_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('zero_pos', 'combo', {'values': ['start_offset', 'stim_end', 'stim_center']}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def setAutoCompleter(self, stim_def):
        stims = list(set([a for b in self.transmission.df[stim_def].tolist() for a in b]))
        autocompleter = QtGui.QCompleter(stims, self.ctrls['Stimulus'])
        self.ctrls['Stimulus'].setCompleter(autocompleter)

    # def connected(self, localTerm, remoteTerm):
    #     pass

    def processData(self, transmission):
        self.transmission = transmission
        # Very messy work-around because the usual widget clear() and removeItem() result in
        # stack overflow from recursion over here. Something to do with Node.__get__attr I think.
        # Results in a really stupid bug where stuff in the comboBox is duplicated.

        all_stims = []
        for i in range(self.ctrls['Stimulus_Type'].count()):
            all_stims.append(self.ctrls['Stimulus_Type'].itemText(i))
        for item in transmission.STIM_DEFS:
            if item in all_stims:
                continue
            else:
                self.ctrls['Stimulus_Type'].addItem(item)

        self.ctrls['Stimulus_Type'].currentTextChanged.connect(self.setAutoCompleter)
        if self.ctrls['Apply'].isChecked() is False:
            return

        stim_def = self.ctrls['Stimulus_Type'].currentText()
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

        t = Transmission(empty_df(), self.transmission.src, self.transmission.dst)
        for ix, r in self.transmission.df.iterrows():
            try:
                smap = r['stimMaps'].flatten()[0][stim_def]
                # print(smap)
            except KeyError:
                continue
            # print(r)
            curve = r[self.transmission.data_column]
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

                    rn[self.transmission.data_column] = curve[int(tstart):int(tend)] / min(curve[int(tstart):int(tend)])
                    rn[stim_def] = stim[0][0]
                    #
                    t.df = t.df.append(rn, ignore_index=True)
        print(t.df)

        t.src.append({'AlignStims': params})
        t.data_column = self.transmission.data_column
        t.plot_this = t.data_column
        return t

class DF_IDX(CtrlNode):
    """Pass only one or multiple DataFrame Indices"""
    nodeName = 'DF_IDX'
    uiTemplate = [('Index', 'intSpin', {'min': 0, 'step': 1, 'value': 0}),
                  ('Indices', 'lineEdit', {'text': '0', 'toolTip': 'Index numbers separated by commas'})
                  ]

    def processData(self, transmission):
        self.ctrls['Index'].setMaximum(len(transmission.df.index)-1)
        self.ctrls['Index'].valueChanged.connect(partial(self.ctrls['Indices'].setText, str(self.ctrls['Index'].value())))

        indices = [int(ix.strip()) for ix in self.ctrls['Indices'].text().split(',')]
        print(indices)
        t = transmission.copy()
        t.df = t.df.iloc[indices, :]
        t.src.append({'DF_IDX': {'indices': indices}})
        return t


class ROI_Include(CtrlNode):
    """Align ROI Definitions"""
    nodeName = 'ROI_Include'
    uiTemplate = [('ROI_Type', 'combo', {'values': []}),
                  ('availTags', 'label', {'toolTip': 'All tags found under this ROI_Def'}),
                  ('ROI_Tags', 'lineEdit', {'toolTip': 'Enter one or many tags separated by commas (,)\n' +\
                                                       'Spaces before or after commas do not matter'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def _setAvailTags(self, roi_def):
        tags = list(set(self.transmission.df[roi_def]))
        self.ctrls['availTags'].setText(', '.join(tags))
        self.ctrls['availTags'].setToolTip('\n'.join(tags))

    def processData(self, transmission):
        self.transmission = transmission

        all_roi_defs = []
        for i in range(self.ctrls['ROI_Type'].count()):
            all_roi_defs.append(self.ctrls['ROI_Type'].itemText(i))
        for item in transmission.ROI_DEFS:
            if item in all_roi_defs:
                continue
            else:
                self.ctrls['ROI_Type'].addItem(item)

        self.ctrls['ROI_Type'].currentTextChanged.connect(self._setAvailTags)

        if self.ctrls['Apply'].isChecked() is False:
            return

        chosen_tags = [tag.strip() for tag in self.ctrls['ROI_Tags'].text().split(',')]

        t = self.transmission.copy()

        t.df = t.df[~t.df[self.ctrls['ROI_Type'].currentText()].isin(chosen_tags)]

        return t



        # for item in transmission.ROI_DEFS:
        #     if item in all_ri_defs:
        #         continue
        #     else:
        #         self.ctrls['Stimulus_Type'].addItem(item)
