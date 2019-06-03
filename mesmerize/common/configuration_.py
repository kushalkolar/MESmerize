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
from common.window_manager import WindowManager
from project_manager.project_manager import ProjectManager
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


def write_new_sys_config():
    if not os.path.isdir(sys_cfg_path):
        os.makedirs(sys_cfg_path)
    sys_cfg = {'HARDWARE': {'n_processes': str(cpu_count() - 2),
                            'USE_CUDA': str(False),
                            },

               'PATHS': {'caiman': '',
                         'env': '',
                         'env_type': '',
                         },

               'ENV': {'MKL_NUM_THREADS': 1,
                       'OPENBLAS_NUM_THREADS': 1
                       }
               }



def open_sys_config():
    sys_cfg = json.load(open(sys_cfg_path, 'r'))


if not IS_WINDOWS:
    sys_cfg_path = os.environ['HOME'] + '/.mesmerize'
    sys_cfg_file = sys_cfg_path + '/config'
    if os.path.isfile(sys_cfg_file):
        open_sys_config()
    else:
        write_new_sys_config()
