#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 13:17:26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

A simple module that can be imported to apply the configuration in a module that imports it.
"""

import configparser
import numpy as np
import os

if os.name == 'nt':
    IS_WINDOWS = True
else:
    IS_WINDOWS = False
cfg = configparser.RawConfigParser(allow_no_value=True)
cfg.optionxform = str
configpath = None
projPath = None
special = {}

df_refs = {}

install_config_path = ''
n_processes = 1


def add_df_ref(ref):
    global df_refs
    df_refs.update(ref)

num_types = [int, float, np.int64, np.float64]

def saveConfig():
    setSpecial()
    with open(configpath, 'w') as configfile:
        cfg.write(configfile)

def newConfig():
    defaultInclude = ['SampleID', 'Genotype', 'Date', 'comments']
    cfg['INCLUDE'] = dict.fromkeys(defaultInclude)

    defaultExclude = ['CurvePath', 'ImgInfoPath', 'ImgPath', 'uuid_curve']
    cfg['EXCLUDE'] = dict.fromkeys(defaultExclude)

    cfg['ROI_DEFS'] = {}

    cfg['STIM_DEFS'] = {}

    cfg['ALL_STIMS'] = {}

    cfg['CHILD_DFS'] = {}

    setSpecial()

    saveConfig()

def openConfig():
    cfg.read(configpath)
    setSpecial()

def setSpecial():
        special['Timings'] = cfg.options('STIM_DEFS')