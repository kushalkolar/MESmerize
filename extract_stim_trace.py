#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 21:27:39 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
import pyqtgraph as pg
import numpy as np
import pickle
from analyser.DataTypes import Transmission
from MesmerizeCore import configuration
from MesmerizeCore.misc_funcs import empty_df

p = pg.plot()


stim_def = 'odor'
stim_tag = 'NH4'
#stim_tag = 'ASW//MS-222'
curves = []

pick = pickle.load(open('./df_with_curves', 'rb'))
#data = list(pick['curve'][0])
data = pick

configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
configuration.openConfig()

transmission = Transmission(data, 'curve')
t = Transmission(empty_df(), transmission.src, transmission.dst)

def extractStimTrace(stim_def, stim_tag, start_offset=0, end_offset=0, zero_pos='start_offset'):
        for ix, r in transmission.df.iterrows():
            try:
                smap = r['stimMaps'].flatten()[0][stim_def]
            except KeyError:
                continue
            
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
                    
                    rn['curve'] = curve
                    rn[stim_def] = stim[0][0]
#                    
                    t.df = t.df.append(rn, ignore_index=True)
                    
                    p.plot(curve[tstart:tend] / min(curve[tstart:tend]))
#        return rd
                
                
extractStimTrace(stim_def, stim_tag, start_offset=0, end_offset=300, zero_pos='stim_end')


#%%
def extractStimTrace(stim_def, stim_tag, start_offset=0, end_offset=0, zero_pos='start_offset'):
    for file in df['CurvePath']:
        npz = np.load(file)
        curve = npz.f.curve
        
        smap = npz.f.stimMaps.flatten()[0][stim_def]
        for stim in smap:
            if stim_tag in stim[0][0]:
                if curve[1] is None:
                    continue
                stim_start = stim[-1][0]
                stim_end = stim[-1][1]
                
                if zero_pos == 'start_offset':
                    
                    tstart = max(stim_start + start_offset, 0)
                    tend = min(stim_end + end_offset, int(curve[0][-1]))
                    
                elif zero_pos == 'stim_end':
                    tstart = stim_end
                    tend = tstart + end_offset
                    
                elif zero_pos == 'stim_center':
                    tstart = int(((stim_start + stim_end) / 2)) + start_offset
                    tend = min(stim_end + end_offset, int(curve[0][-1]))
                
                p.plot(curve[1][tstart:tend]/min(curve[1][tstart:tend]))
#

extractStimTrace(stim_def, stim_tag, 0, 600, zero_pos='start_offset')
