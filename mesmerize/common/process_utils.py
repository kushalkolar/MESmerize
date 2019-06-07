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
from . import get_sys_config
from typing import Optional


def make_workdir(prefix: str = '') -> str:
    main_workdir = get_sys_config()['_MESMERIZE_WORKDIR']

    if main_workdir == '':
        raise ValueError('You have not set the working directory in the System Configuration')
    if not os.access(main_workdir, os.W_OK):
        raise PermissionError(f'You do not have write permissions for the chosen work folder:\n{main_workdir}')

    date = datetime.fromtimestamp(time())
    dirname = f'{prefix}_{date.strftime("%Y%m%d")}_{date.strftime("%H%M%S")}'
    workdir = os.path.join(main_workdir, dirname)
    os.makedirs(workdir)

    return workdir


def make_runfile(module_path: str, savedir: str, args_str: Optional[str] = None, filename: Optional[str] = None,
                 pre_run: Optional[str] = None, post_run: Optional[str] = None) -> str:
    """
    :param module_path: absolute module path
    :param args_str:    str of args that is directly passed with the python command in the bash script
    :param savedir:     working directory
    :param filename:    optional, specific filename for the script
    :param pre_run:     optional, str to run before module is ran
    :param post_run:    optional, str to run after module has run

    :return: path to the shell script that can be run
    """
    if filename is None:
        sh_file = os.path.join(savedir, 'run.sh')
    else:
        sh_file = os.path.join(savedir, filename)

    sys_cfg = get_sys_config()

    if pre_run is None:
        pre_run = ''
    if post_run is None:
        post_run = ''

    n_threads = sys_cfg['_MESMERIZE_N_THREADS']
    use_cuda = sys_cfg['_MESMERIZE_USE_CUDA']
    python_call = sys_cfg['_MESMERIZE_PYTHON_CALL']

    cmd_prefix = sys_cfg['_MESMERIZE_PREFIX_COMMANDS']

    if not os.path.isdir(savedir):
        try:
            os.makedirs(savedir)
        except PermissionError:
            raise PermissionError('You do not have permission to write to the chosen working directory.')

    elif os.path.isfile(savedir):
        raise FileExistsError("Choose a different working dir path")

    if args_str is None:
        args_str = ''

    to_write = '\n'.join(['#!/bin/bash',
                          f'{cmd_prefix}',
                          f'export _MESMERIZE_N_THREADS={n_threads}',
                          f'export _MESMERIZE_USE_CUDA={use_cuda}',
                          f'{pre_run}',
                          f'{python_call} {module_path} {args_str}',
                          f'{post_run}'])

    with open(sh_file, 'w') as sf:
        sf.write(to_write)

    st = os.stat(sh_file)
    os.chmod(sh_file, st.st_mode | S_IEXEC)

    return sh_file
