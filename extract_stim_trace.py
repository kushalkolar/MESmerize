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

p = pg.plot()
#%%

stim_def = 'odor'
stim_tag = 'NH4//0.25 mM'
curves = []
def extractStimTrace(stim_def, stim_tag):
    for file in df['CurvePath']:
        npz = np.load(file)
        curve = npz.f.curve[1]
        smap = npz.f.stimMaps.flatten()[0][stim_def]
        for stim in smap:
            if stim[0][0] == stim_tag:
                if curve is None:
                    continue
                p.plot(curve[stim[-1][0]:stim[-1][1]]/min(curve[stim[-1][0]:stim[-1][1]]))
#                print(stim[-1][0] stim[-1][1])
                
                print(stim[0][0])
#            
        
        
#        curves.append(curve)

extractStimTrace(stim_def, stim_tag)