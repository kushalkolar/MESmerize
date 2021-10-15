#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#@author: kushal

#Chatzigeorgiou Group
#Sars International Centre for Marine Molecular Biology

#GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007


import os
from stat import S_IEXEC
from time import time
from datetime import datetime
from . import get_sys_config
from typing import *
import numpy as np
import h5py
import json
import pandas as pd
from warnings import warn
import traceback
from graphviz import Digraph
from .configuration import IS_WINDOWS



def make_workdir(prefix: str = '') -> str:
    """
    Make a workdir within the mesmerize_tmp directory of the workdir specified in the configuration
    The name of the created workdir is the date & time of its creation. You can add a prefix to this name.

    :param prefix: Prefix for the workdir namec

    :return:    full workdir path
    :rtype:     str
    """

    main_workdir = get_sys_config()['_MESMERIZE_WORKDIR']

    if main_workdir == '':
        raise ValueError('You have not set the working directory in the System Configuration')
    if not os.access(main_workdir, os.W_OK):
        raise PermissionError(f'You do not have write permissions for the chosen work folder:\n{main_workdir}')

    date = datetime.fromtimestamp(time())
    dirname = f'{prefix}_{date.strftime("%Y%m%d")}_{date.strftime("%H%M%S")}_r{np.random.randint(0, 1000)}'
    workdir = os.path.join(main_workdir, 'mesmerize_tmp', dirname)
    os.makedirs(workdir)

    return workdir


# def make_runfile(*args, **kwargs) -> str:
#     if not IS_WINDOWS:
#         return _make_runfile_posix(*args, **kwargs)
#
#     elif IS_WINDOWS:
#         return _make_runfile_windows(*args, **kwargs)
#
#
# def _make_runfile_windows(module_path: str, workdir: str, args_str: str = None, filename: str = None,
#                  pre_run: str = '', post_run: str = '') -> str:
#
#     if filename is None:
#         sh_file = os.path.join(workdir, 'run')
#     else:
#         sh_file = os.path.join(workdir, filename)
#
#     sys_cfg = get_sys_config()



def make_runfile(module_path: str, savedir: str, args_str: Optional[str] = None, filename: Optional[str] = None,
                 pre_run: Optional[str] = None, post_run: Optional[str] = None) -> str:
    """
    Make an executable bash script. Used for running python scripts in external processes.

    :param module_path: absolute module path
    :type module_path:  str

    :param args_str:    str of args that is directly passed with the python command in the bash script
    :type args_str:     str

    :param savedir:     working directory
    :type savedir:      Optional[str]

    :param filename:    optional, specific filename for the script
    :type filename:     Optional[str]

    :param pre_run:     optional, str to run before module is ran
    :type pre_run:      Optional[str]

    :param post_run:    optional, str to run after module has run
    :type post_run:     Optional[str]

    :return: path to the shell script that can be run
    :rtype:  str
    """

    if filename is None:
        if IS_WINDOWS:
            sh_file = os.path.join(savedir, 'run.ps1')
        else:
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

    if not IS_WINDOWS:
        to_write = '\n'.join(['#!/bin/bash',
                              f'{cmd_prefix}',
                              f'export _MESMERIZE_N_THREADS={n_threads}',
                              f'export _MESMERIZE_USE_CUDA={use_cuda}',
                              f'{pre_run}',
                              f'{python_call} {module_path} {args_str}',
                              f'{post_run}'])
    else:
        to_write = os.linesep.join(
            [
                f'{cmd_prefix}',
                f'$env:_MESMERIZE_N_THREADS="{n_threads}"',
                f'$env:_MESMERIZE_USE_CUDA="{use_cuda}"',
                f'{pre_run}',
                f'{python_call} {module_path} {args_str}',
                f'{post_run}'
            ]
        )

    with open(sh_file, 'w') as sf:
        sf.write(to_write)

    st = os.stat(sh_file)
    os.chmod(sh_file, st.st_mode | S_IEXEC)

    return sh_file


class HdfTools:
    """Functions for saving and loading HDF5 data"""

    @staticmethod
    def save_dataframe(path: str, dataframe: pd.DataFrame, metadata: Optional[dict] = None,
                       metadata_method: str = 'json', raise_meta_fail: bool = True):
        """
        Save DataFrame to hdf5 file along with a meta data dict.

        Meta data dict can either be serialized with json and stored as a str in the hdf5 file, or recursively saved
        into hdf5 groups if the dict contains types that hdf5 can deal with. Experiment with both methods and see what works best

        Currently the hdf5 method can work with these types: [str, bytes, int, float, np.int, np.int8, np.int16,
        np.int32, np.int64, np.float, np.float16, np.float32, np.float64, np.float128, np.complex].

        If it encounters an object that is not of these types it will store whatever that object's __str__() method
        returns if on_meta_fail is False, else it will raise an exception.

        :param path:            path to save the file to
        :type path:             str

        :param dataframe:       DataFrame to save in the hdf5 file
        :type dataframe:        pd.DataFrame

        :param metadata:        Any associated meta data to store along with the DataFrame in the hdf5 file
        :type metadata:         Optional[dict]

        :param metadata_method: method for storing the metadata dict, either 'json' or 'recursive'
        :type metadata_method:  str

        :param raise_meta_fail: raise an exception if recursive metadata saving encounters an unsupported object
                                If false, it will save the unsupported object's __str__() return value
        :type raise_meta_fail:  bool
        """

        if os.path.isfile(path):
            raise FileExistsError

        f = h5py.File(path, mode='w')

        f.create_group('DATAFRAME')

        if metadata is not None:
            mg = f.create_group('META')
            mg.attrs['method'] = metadata_method

            if metadata_method == 'json':
                bad_keys = []
                for k in metadata.keys():
                    try:
                        mg.create_dataset(k, data=json.dumps(metadata[k]))
                    except TypeError as e:
                        bad_keys.append(k + ': ' + str(e))

                if len(bad_keys) > 0:
                    bad_keys = '\n'.join(bad_keys)
                    raise TypeError(f"The following meta data keys are not JSON serializable\n{bad_keys}")

            elif metadata_method == 'recursive':
                HdfTools._dicts_to_group(h5file=f, path='META/', d=metadata, raise_meta_fail=raise_meta_fail)

        f.close()

        dataframe.to_hdf(path, key='DATAFRAME', mode='r+')

    @staticmethod
    def load_dataframe(filepath: str) -> Tuple[pd.DataFrame, Union[dict, None]]:
        """
        Load a DataFrame along with meta data that were saved using ``HdfTools.save_dataframe``

        :param filepath: file path to the hdf5 file
        :type filepath:  str

        :return: tuple, (DataFrame, meta data dict if present else None)
        :rtype: Tuple[pd.DataFrame, Union[dict, None]]
        """

        with h5py.File(filepath, 'r') as f:
            if 'META' in f.keys():

                if f['META'].attrs['method'] == 'json':
                    ks = f['META'].keys()
                    metadata = dict.fromkeys(ks)
                    for k in ks:
                        metadata[k] = json.loads(f['META'][k][()])

                elif f['META'].attrs['method'] == 'recursive':
                    metadata = HdfTools._dicts_from_group(f, 'META/')

            else:
                metadata = None
        df = pd.read_hdf(filepath, key='DATAFRAME', mode='r')

        return (df, metadata)

    @staticmethod
    def save_dict(d: dict, filename: str, group: str, raise_type_fail=True):
        """
        Recursively save a dict to an hdf5 group.

        :param d:        dict to save
        :type d:         dict

        :param filename: filename
        :type filename:  str

        :param group:    group name to save the dict to
        :type group:     str

        :param raise_type_fail: whether to raise if saving a piece of data fails
        :type raise_type_fail:  bool
        """

        if os.path.isfile(filename):
            raise FileExistsError

        with h5py.File(filename, 'w') as h5file:
            HdfTools._dicts_to_group(h5file, f'{group}/', d, raise_meta_fail=raise_type_fail)

    @staticmethod
    def _dicts_to_group(h5file: h5py.File, path: str, d: dict, raise_meta_fail: bool):
        for key, item in d.items():

            if isinstance(item, np.ndarray):

                if item.dtype == np.dtype('O'):
                    # see if h5py is ok with it
                    try:
                        h5file[path + key] = item
                        # h5file[path + key].attrs['dtype'] = item.dtype.str
                    except:
                        msg = f"numpy dtype 'O' for item: {item} not supported by HDF5\n{traceback.format_exc()}"

                        if raise_meta_fail:
                            raise TypeError(msg)
                        else:
                            h5file[path + key] = str(item)
                            warn(f"{msg}, storing whatever str(obj) returns.")

                # numpy array of unicode strings
                elif item.dtype.str.startswith('<U'):
                    h5file[path + key] = item.astype(h5py.special_dtype(vlen=str))
                    h5file[path + key].attrs['dtype'] = item.dtype.str  # h5py doesn't restore the right dtype for str types

                # other types
                else:
                    h5file[path + key] = item
                    # h5file[path + key].attrs['dtype'] = item.dtype.str

            # single pieces of data
            elif isinstance(item, (str, bytes, int, float, np.int, np.int8, np.int16, np.int32, np.int64, np.float,
                                   np.float16, np.float32, np.float64, np.float128, np.complex)):
                h5file[path + key] = item

            elif isinstance(item, dict):
                HdfTools._dicts_to_group(h5file, path + key + '/', item, raise_meta_fail)

            # last resort, try to convert this object to a dict and save its attributes
            elif hasattr(item, '__dict__'):
                HdfTools._dicts_to_group(h5file, path + key + '/', item.__dict__, raise_meta_fail)

            else:
                msg = f"{type(item)} for item: {item} not supported not supported by HDF5"

                if raise_meta_fail:
                    raise ValueError(msg)

                else:
                    h5file[path+key] = str(item)
                    warn(f"{msg}, storing whatever str(obj) returns.")

    @staticmethod
    def load_dict(filename: str, group: str) -> dict:
        """
        Recursively load a dict from an hdf5 group.

        :param filename: filename
        :type filename:  str

        :param group:    group name of the dict
        :type group:     str

        :return:         dict recursively loaded from the hdf5 group
        :rtype:          dict
        """

        with h5py.File(filename, 'r') as h5file:
            return HdfTools._dicts_from_group(h5file, f'{group}/')

    @staticmethod
    def _dicts_from_group(h5file: h5py.File, path: str) -> dict:
        ans = {}
        for key, item in h5file[path].items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                if item.attrs.__contains__('dtype'):
                    ans[key] = item[()].astype(item.attrs['dtype'])
                else:
                    ans[key] = item[()]
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = HdfTools._dicts_from_group(h5file, path + key + '/')
        return ans


def draw_graph(l: List[dict], filename: Optional[str] = None, view: bool = False) -> str:
    """
    Draw a graph from a list of dicts.

    :param l: list of dicts
    :type l: List[dict]

    :param filename: full path for storing the draw graph pdf file
    :type filename: Optional[str]

    :param view: view the graph in the system's default pdf reader after it is rendered
    :type view: Optional[bool]

    :return: full path to the graph pdf file
    :rtype: str
    """
    if filename is None:
        workdir = make_workdir(prefix='graph_')
        filename = os.path.join(workdir, 'graph')

    g = Digraph('G', filename=filename, format='pdf', node_attr={'shape': 'record'})

    o_encounters = []
    o_n_l = []

    for op in l:
        o = list(op.keys())[0]
        params = op[o]
        s = []
        for k in params.keys():
            p = str(params[k]).replace("{", "\\n   --\> ").replace("}", "").replace("|", "\|")  # .replace("[", " ").replace("(", " ").replace(")", " ")
            s.append(f"{k}: {p}")

        o_n = f"{o}.{o_encounters.count(o)}"
        o_n_l.append(o_n)
        s = '{ ' + o_n + ' | ' + '\\n'.join(s) + ' }'

        g.node(o_n, s)
        o_encounters.append(o)

    es = []
    for i in range(1, len(o_n_l)):
        es.append((o_n_l[i - 1], o_n_l[i]))

    g.edges(es)
    g.render(view=view)

    return filename
