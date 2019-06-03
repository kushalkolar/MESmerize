#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from . import get_sys_config
import os
from stat import S_IEXEC
from time import time
from datetime import datetime


def make_workdir(suffix: str = '') -> str:
    date = datetime.fromtimestamp(time())
    time_str = date.strftime('%Y%m%d') + '_' + date.strftime('%H%M%S')
    workdir = '/work/' + os.environ['USER'] + '/' + time_str + '_' + suffix
    os.makedirs(workdir)
    return workdir


def make_runfile(module_path: str, workdir: str, args_str: str = None, filename: str = None,
                 pre_run: str = '', post_run: str = '') -> str:
    """
    :param module_path: absolute module path
    :param args_str:    str of args that is directly passed with the python command in the bash script
    :param workdir:     working directory
    :param filename:    optional, specific filename for the script
    :param pre_run:     optional, str to run before module is ran
    :param post_run:    optional, str to run after module has run

    :return: path to the shell script that can be run
    """
    if filename is None:
        sh_file = workdir + '/' + 'run.sh'
    else:
        sh_file = workdir + '/' + filename

    sys_cfg = get_sys_config()

    if sys_cfg['PATHS']['env_type'] == 'anaconda':
        env_path = sys_cfg['PATHS']['env']
        anaconda_dir = os.path.dirname(os.path.dirname(os.path.dirname(env_path)))
        env_name = os.path.basename(os.path.normpath(env_path))
        env_activation = 'export PATH=' + anaconda_dir + ':$PATH\nsource activate ' + env_name
    elif sys_cfg['PATHS']['env_type'] == 'virtual':
        env_path = sys_cfg['PATHS']['env']
        env_activation = 'source ' + env_path + '/bin/activate'
    else:
        raise ValueError('Invalid configruation value for environment path. Please check the entry for "env" under'
                         'section [PATH] in the config file.')
    caiman_path = sys_cfg['PATHS']['caiman']
    n_processes = sys_cfg['HARDWARE']['n_processes']

    if not os.path.isdir(workdir):
        try:
            os.makedirs(workdir)
        except PermissionError:
            raise PermissionError('You do not appear to have permission to write to the chosen working directory.')

    elif os.path.isfile(workdir):
            raise FileExistsError("Choose a different working dir path")

    if args_str is None:
        args_str = ''
    else:
        args_str = ' ' + args_str

    with open(sh_file, 'w') as sf:
        sf.write('#!/bin/bash\n' +
                 env_activation + '\n' +
                 'export PYTHONPATH="' + caiman_path + '"\n' +
                 'export MKL_NUM_THREADS=1\n' +
                 'export OPENBLAS_NUM_THREADS=1\n'
                 'export MESMERIZE_N_PROCESSES=' + str(n_processes) + '\n'
                 'export USE_CUDA=' + sys_cfg['HARDWARE']['USE_CUDA'] + '\n' +
                 pre_run +
                 'python ' + module_path + args_str + '\n' +
                 post_run
                 )

    st = os.stat(sh_file)
    os.chmod(sh_file, st.st_mode | S_IEXEC)

    return sh_file
