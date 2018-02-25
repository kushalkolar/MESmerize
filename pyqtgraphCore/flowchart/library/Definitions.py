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


configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
configuration.openConfig()

class AlignStims(CtrlNode):
    """Align Stimulus Definitions"""
    nodeName = 'AlignStims'
    uiTemplate = [('Stimulus_Type', 'combo', {'values': []}),
                  ('Stimulus', 'lineEdit', {'placeHolder': 'Stimulus and/or Substim', 'text': 'NH4'}),
                  ('start_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('end_offset', 'doubleSpin', {'min': 0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('zero_pos', 'combo', {'values': ['start_offset', 'stim_end', 'stim_center']}),
                  ('Apply', 'check', {'checked': False})
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

        t = Transmission(empty_df(), self.transmission.src, self.transmission.dst)

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

                    rn['curve'] = curve[int(tstart):int(tend)] / min(curve[int(tstart):int(tend)])
                    rn[stim_def] = stim[0][0]
                    #
                    t.df = t.df.append(rn, ignore_index=True)
        print(t.df)
        t.src = 'AlignStims'
        return t

class ROI_Include(CtrlNode):
    """Align ROI Definitions"""
    nodeName = 'ROI_Include'
