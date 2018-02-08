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
#%%
p = pg.plot()


stim_def = 'odor'
stim_tag = 'NH4//0.25 mM'
#stim_tag = 'ASW//MS-222'
curves = []
def extractStimTrace(stim_def, stim_tag, start_offset=0, end_offset=0, zero_pos='start_offset'):
    for file in df['CurvePath']:
        npz = np.load(file)
        curve = npz.f.curve
        
        smap = npz.f.stimMaps.flatten()[0][stim_def]
        for stim in smap:
            if stim[0][0] == stim_tag:
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