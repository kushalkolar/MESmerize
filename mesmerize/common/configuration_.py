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
from ..common.window_manager import WindowManager
from ..project_manager.project_manager import ProjectManager
import json

window_manager = WindowManager()
project_manager = ProjectManager(None)

#################################################################

# System Configuration

#################################################################

if os.name == 'nt':
    IS_WINDOWS = True
else:
    IS_WINDOWS = False

sys_cfg = {}

num_types = [int, float, np.int64, np.float64]

sys_cfg_path = os.environ['HOME'] + '/.mesmerize/config.json'

_prefix_commands = ["export MKL_NUM_THREADS=1",
                    "export OPENBLAS_NUM_THREADS=1"]

_default_sys_config = {'_MESMERIZE_N_THREADS': cpu_count() - 1,
                       '_MESMERIZE_USE_CUDA': False,
                       '_MESMERIZE_PYTHON_CALL': 'python3',
                       '_MESMERIZE_PREFIX_COMMANDS': '\n'.join(_prefix_commands)
                       }


def create_new_sys_config() -> dict:
    if not os.path.isdir(sys_cfg_path):
        os.makedirs(sys_cfg_path)

    with open(sys_cfg_path, 'w') as f:
        json.dump(_default_sys_config, f)

    return _default_sys_config


def get_sys_config() -> dict:
    if not os.path.isfile(sys_cfg_path):
        return create_new_sys_config()

    with open(sys_cfg_path, 'r') as f:
        sys_cfg = json.load(f)

    return sys_cfg


def save_sys_config(cfg: dict):
    if not set(cfg.keys()).issubset(_default_sys_config.keys()):
        raise KeyError('Required config fields are missing. The following fields must be present:\n' + str(cfg.keys()))

    with open(sys_cfg_path, 'w') as f:
        json.dump(cfg, f)


