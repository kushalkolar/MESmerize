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
from psutil import cpu_count

if os.name == 'nt':
    IS_WINDOWS = True
else:
    IS_WINDOWS = False
cfg = configparser.RawConfigParser(allow_no_value=True)
cfg.optionxform = str

sys_cfg = configparser.RawConfigParser(allow_no_value=True)
# sys_cfg.optionxform = str

configpath = None
projPath = None
special = {}

df_refs = {}

install_config_path = ''
# n_processes = sys_cfg['HARDWARE']['n_processes']#int(cpu_count() / 2) - 1


def write_new_sys_config():
    if not os.path.isdir(sys_cfg_path):
        os.makedirs(sys_cfg_path)
    sys_cfg['HARDWARE'] = {'n_processes': str(int(cpu_count() / 2) - 1)}
    sys_cfg['PATHS'] = {'caiman': '', 'anaconda3': ''}
    sys_cfg['BATCH'] = {'anaconda_env': ''}
    write_sys_config()


def write_sys_config():
    with open(sys_cfg_file, 'w') as cf:
        sys_cfg.write(cf)


def open_sys_config():
    sys_cfg.read(sys_cfg_file)


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


if not IS_WINDOWS:
    sys_cfg_path = os.environ['HOME'] + '/.mesmerize'
    sys_cfg_file = sys_cfg_path + '/config'
    if os.path.isfile(sys_cfg_file):
        open_sys_config()
    else:
        write_new_sys_config()
