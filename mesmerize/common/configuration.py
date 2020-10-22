#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

A module that is globally accessible from all modules.
"""

import numpy as np
import os
from psutil import cpu_count
import json
from configparser import RawConfigParser
from warnings import warn

#################################################################

# System Configuration

#################################################################

if os.name == 'nt':
    IS_WINDOWS = True
    HOME = 'USERPROFILE'
else:
    IS_WINDOWS = False
    HOME = 'HOME'

try:
    import caiman
except ImportError:
    warn(
        "Caiman package not found. "
        "Caiman features will be disabled."
    )
    HAS_CAIMAN = False
else:
    HAS_CAIMAN = True

try:
    import tensorflow
except ImportError:
    warn(
        "tensorflow not found. Nuset segementaiton will be disabled"
    )
    HAS_TENSORFLOW = False
else:
    HAS_TENSORFLOW = True

try:
    import tslearn
except ImportError:
    warn(
        "tslearn package not found. "
        "tslearn features will be disabled."
    )
    HAS_TSLEARN = False
else:
    HAS_TSLEARN = True

sys_cfg = {}

num_types = [int, float, np.int64, np.float64]

sys_cfg_dir = os.path.join(os.environ[HOME], '.mesmerize')

sys_cfg_file = os.path.join(sys_cfg_dir, 'config.json')

console_history_path = os.path.join(sys_cfg_dir, 'console_history')
if not os.path.isdir(console_history_path):
    os.makedirs(console_history_path)

_prefix_comments = \
    [
        '# For example if you are running in an anaconda environment',
        '# export PATH="/home/<user>/anaconda3:$PATH"',
        '# source activate my_environment',
        '# Or if you are using a python virtual environment',
        '# source /<path_to_env>/activate',
        '# Adjust these according to your hardware'
    ]

if IS_WINDOWS:
    _prefix_commands = \
        [
            "# If using anaconda, you may need a command to activate the conda environment.",
            "# If this is the case, uncomment the following line.",
            "# conda activate mesmerize",
            "\n"
        ]

else:
    _prefix_commands = _prefix_comments + ["export MKL_NUM_THREADS=1",
                                           "export OPENBLAS_NUM_THREADS=1", '\n']

default_sys_config = {'_MESMERIZE_N_THREADS': cpu_count() - 1,
                      '_MESMERIZE_USE_CUDA': False,
                      '_MESMERIZE_PYTHON_CALL': 'python3',
                      '_MESMERIZE_PREFIX_COMMANDS': '\n'.join(_prefix_commands),
                      '_MESMERIZE_CUSTOM_MODULES_DIR': os.environ[HOME] + '/mesmerize_custom_modules',
                      '_MESMERIZE_WORKDIR': '',
                      'recent_projects': []
                      }

if IS_WINDOWS:
    default_sys_config.update({'_MESMERIZE_PYTHON_CALL': 'python'})


# patching in something that will probably be used in mesmerize v1.0 to simplify sys config things
class ENVIRONMENT:
    def __init__(self):
        self.LRU_CACHE_MAXSIZE: int = 64  # `maxsize` argument for @lru_cache


# update the default env vars with any that are specified in the env
def get_environment() -> ENVIRONMENT:
    e = ENVIRONMENT()
    for opt, val in e.__dict__.items():
        # user can prefix the env vars with "MESMERIZE" if they want, but not necessary
        if (opt in os.environ.keys()) or (f'MESMERIZE_{opt}' in os.environ.keys()):
            setattr(e, opt, type(val)(os.environ[opt]))  # to convert str to other types, like str -> int/float

    return e


class SysConfig:
    def __init__(self, n_threads: int,
                 use_cuda: bool,
                 python_call: str,
                 prefix_commands: str,
                 custom_modules_dir: str,
                 workdir: str,
                 recent_projects: list):
        self.n_threads = n_threads
        self.use_cuda = use_cuda
        self.python_call = python_call
        self.prefix_commands = prefix_commands
        self.custom_modules_dir = custom_modules_dir
        self.workdir = workdir
        self.recent_projects = recent_projects


def create_new_sys_config() -> dict:
    if not os.path.isdir(sys_cfg_dir):
        os.makedirs(sys_cfg_dir)

    save_sys_config(default_sys_config)

    return default_sys_config


def get_sys_config() -> dict:
    """Get the user-set system configuration"""

    if not os.path.isfile(sys_cfg_file):
        return create_new_sys_config()

    with open(sys_cfg_file, 'r') as f:
        sys_cfg = json.load(f)

    return sys_cfg


def save_sys_config(cfg: dict):
    if not set(cfg.keys()).issubset(default_sys_config.keys()):
        raise KeyError('Required config fields are missing. The following fields must be present:\n' + str(cfg.keys()))

    if not cfg['_MESMERIZE_PREFIX_COMMANDS'].endswith('\n'):
        cfg['_MESMERIZE_PREFIX_COMMANDS'] += '\n'

    with open(sys_cfg_file, 'w') as f:
        json.dump(cfg, f, indent=4)


#################################################################

# Project Configuration

#################################################################

proj_path = None
proj_cfg = RawConfigParser(allow_no_value=True)
proj_cfg['ROI_DEFS'] = {}
proj_cfg['STIM_DEFS'] = {}

proj_cfg.optionxform = str
special = {}
df_refs = {}


def save_proj_config():
    set_proj_special()
    with open(proj_path + '/config.cfg', 'w') as configfile:
        proj_cfg.write(configfile)


def create_new_proj_config():
    defaultInclude = ['SampleID', 'date', 'comments']
    proj_cfg['INCLUDE'] = dict.fromkeys(defaultInclude)

    defaultExclude = ['ImgInfoPath', 'ImgPath', 'ImgUUID', 'ROI_State', 'uuid_curve', 'misc', 'AnimalID']
    proj_cfg['EXCLUDE'] = dict.fromkeys(defaultExclude)

    proj_cfg['ROI_DEFS'] = {}

    proj_cfg['STIM_DEFS'] = {}

    proj_cfg['ALL_STIMS'] = {}

    proj_cfg['CUSTOM_COLUMNS'] = {}

    proj_cfg['CHILD_DFS'] = {}

    set_proj_special()

    save_proj_config()


def open_proj_config():
    proj_cfg.read(proj_path + '/config.cfg')
    set_proj_special()


def set_proj_special():
    special['Timings'] = proj_cfg.options('STIM_DEFS')
