#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 13:17:26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
import configparser
import numpy as np
cfg = configparser.RawConfigParser(allow_no_value=True)
cfg.optionxform = str

configpath = None

special = {}

num_types = [int, float, np.int64, np.float64]

def saveConfig():
    setSpecial()
    with open(configpath, 'w') as configfile:
        cfg.write(configfile)

def newConfig():
    defaultInclude = ['SampleID', 'Genotype', 'Date']
    cfg['INCLUDE'] = dict.fromkeys(defaultInclude)

    defaultExclude = ['CurvePath', 'ImgInfoPath', 'ImgPath']
    cfg['EXCLUDE'] = dict.fromkeys(defaultExclude)

    cfg['ROI_DEFS'] = {}

    cfg['STIM_DEFS'] = {}

    cfg['ALL_STIMS'] = {}

    setSpecial()

    saveConfig()

def openConfig():
    cfg.read(configpath)
    setSpecial()

def setSpecial():
        special['Timings'] = cfg.options('STIM_DEFS')