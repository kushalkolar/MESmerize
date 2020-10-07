#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import pandas as pd
import pickle
import json
from copy import deepcopy
from uuid import uuid4, UUID
from typing import Tuple, List, Dict, Union, Optional
from itertools import chain
import os
import traceback
from warnings import warn
from configparser import RawConfigParser
from ..common.utils import HdfTools, draw_graph
from ..common import get_proj_config
from ..common.configuration import get_environment
from tqdm import tqdm
from functools import lru_cache


class _HistoryTraceExceptions(Exception):
    def __init__(self, msg):
        assert isinstance(msg, str)
        self.msg = msg

    def __str__(self):
        return str(self.__doc__) + '\n' + self.msg


class DataBlockNotFound(_HistoryTraceExceptions):
    """Requested data block not found"""


class DataBlockAlreadyExists(_HistoryTraceExceptions):
    """Data block already exists in HistoryTrace."""


class OperationNotFound(_HistoryTraceExceptions):
    """Requested operation not found in data block."""


class HistoryTrace:
    """
    Structure of a history trace:

    A dict with keys that are the block_ids. Each dict value is a list of operation_dicts.
    Each operation_dict has a single key which is the name of the operation and the value of that key is the operation parameters.

        {block_id_1: [\n
                        {operation_1:\n
                            {\n
                             param_1: a,\n
                             param_2: b,\n
                             param_n, z\n
                             }\n
                         },\n
\n
                        {operation_2:\n
                            {\n
                             param_1: a,\n
                             param_n, z\n
                             }\n
                         },\n
                         ...\n
                        {operation_n:\n
                            {\n
                             param_n: x\n
                             }\n
                         }\n
                     ]\n
         block_id_2: <list of operation dicts>,\n
         ...\n
         block_id_n: <list of operation dicts>\n
         }\n

    **The main dict illustrated above should never be worked with directly.**\n
    **You must use the helper methods of this class to query or add information**

    """
    def __init__(self, history: Dict[Union[UUID, str], List[Dict]] = None, data_blocks: List[Union[UUID, str]] = None):
        """
        :param history:     Dict containing a data block UUIDs as keys. The values are a list of dicts containing operation parameters.
        :param data_blocks: List of data block UUIDs

        :ivar _history:     The dict of the actual data, as illustrated above. Should not be accessed directly. Use the :py:attr:`~history` property or call `get_all_data_blocks_history()`.
        :ivar _data_blocks: List of all data blocks. Should not be accessed directly, use the :py:attr:`~data_blocks` property instead.
        """
        self._history = None
        self._data_blocks = None

        if None in [history, data_blocks]:
            self.data_blocks = []
            self.history = dict()
        else:
            for i in range(len(data_blocks)):
                data_blocks[i] = self._to_uuid(data_blocks[i])
            self.data_blocks = data_blocks
            for k in list(history.keys()):
                history[self._to_uuid(k)] = history.pop(k)
            self.history = history

    @property
    def data_blocks(self) -> list:
        """List of UUIDs that allow you to pin down the history of specific rows of the dataframe to their history
        as stored in the history trace data structure (self.history)"""
        return self._data_blocks

    @data_blocks.setter
    def data_blocks(self, dbl: list):
        self._data_blocks = dbl

    @property
    def history(self) -> dict:
        """The analysis log that is stored in the structure outlined in the doc string"""
        return self._history

    @history.setter
    def history(self, h):
        self._history = h

    def create_data_block(self, dataframe: pd.DataFrame) -> Tuple[pd.DataFrame, UUID]:
        """
        Creates a new UUID, assigns it to the input dataframe by setting the UUID in the _BLOCK_ column

        :param dataframe: Assigns a block ID to this entire DataFrame.
        """
        block_id = uuid4()
        self._add_data_block(block_id)
        dataframe['_BLOCK_'] = str(block_id)
        return dataframe, block_id

    def _add_data_block(self, data_block_id: UUID):
        """
        Adds new datablock UUID to the list of datablocks in this instance.
        Throws exception if UUID already exists.
        """
        assert isinstance(data_block_id, UUID)
        if data_block_id in self.data_blocks:
            raise DataBlockAlreadyExists(str(data_block_id))
        else:
            self.data_blocks.append(data_block_id)

        self.history.update({data_block_id: []})

    def add_operation(self, data_block_id: Union[UUID, str], operation: str, parameters: dict):
        """
        Add a single operation, that is usually performed by a node, to the history trace.
        Added to all or specific datablock(s), depending on which datablock(s) the node performed the operation on

        :param data_block_id: data_block_id to log the operation on to. either a UUID or 'all' to append the operation to all data blocks
        :param operation: name of the operation, usually the same as the name of the node in all lowercase
        :param parameters: operation parameters.
        """
        assert isinstance(operation, str)
        assert isinstance(parameters, dict)

        if isinstance(data_block_id, str):
            if data_block_id == 'all':
                _ids = self.data_blocks
            else:
                try:
                    _ids = [self._to_uuid(data_block_id)]
                except ValueError:
                    raise ValueError("data_block_id must be a UUID, str representation of a UUID, or 'all' ")

        else:
            _ids = [data_block_id]

        if not all(u in self.data_blocks for u in _ids):
            raise DataBlockNotFound()
        for _id in _ids:
            self.history[_id].append({operation: parameters})

    def get_data_block_history(self, data_block_id: Union[str, UUID], copy: bool = False) -> List[dict]:
        """
        Get the full history trace of a single data block.

        Use copy=False if you want to modify the history trace of the data block.

        :param data_block_id: data block ID
        :type data_block_id: Union[str, UUID]

        :param copy: If true, returns a deepcopy
        :type copy: bool

        :return: data block history
        :rtype: List[dict]
        """

        data_block_id = self._to_uuid(data_block_id)

        if data_block_id not in self.data_blocks:
            raise DataBlockNotFound(str(data_block_id))

        if copy:
            return deepcopy(self.history[data_block_id])

        else:
            return self.history[data_block_id]

    def get_all_data_blocks_history(self) -> dict:
        """Returns history trace of all datablocks"""
        h = {}

        for block_id in self.data_blocks:
            h.update({str(block_id): self.get_data_block_history(block_id)})

        return h.copy()

    def get_operations_list(self, data_block_id: Union[UUID, str]) -> list:
        """
        Returns just a simple list of operations in the order that they were performed on the given datablock.
        To get the operations along with their parameters call get_data_block_history()
        """
        data_block_id = self._to_uuid(data_block_id)

        l = [next(iter(d)) for d in self.get_data_block_history(data_block_id)]
        return l

    def get_operation_params(self, data_block_id: Union[UUID, str], operation: str) -> dict:
        """Get the parameters dict for a specific operation that was performed on a specific data block"""
        # if isinstance(data_block_id, str):
        #     data_block_id = UUID(data_block_id)
        data_block_id = self._to_uuid(data_block_id)

        try:
            l = self.get_data_block_history(data_block_id)
            params = next(d for ix, d in enumerate(reversed(l)) if operation in d)[operation]
        except StopIteration:
            raise OperationNotFound('Data block: ' + str(data_block_id) + ', Operation: ' + operation)

        return params.copy()

    def check_operation_exists(self, data_block_id: UUID, operation: str) -> bool:
        """Check if a specific operation was performed on a specific datablock"""
        data_block_id = self._to_uuid(data_block_id)
        try:
            self.get_operation_params(data_block_id, operation)
        except OperationNotFound:
            return False
        else:
            return True

    @staticmethod
    def _to_uuid(u: Union[str, UUID]) -> UUID:
        """
        If argument 'u' is type <str> that can be formatted as a UUID, return it as UUID type.
        If argument 'u' is a UUID, just return it.
        """
        if isinstance(u, UUID):
            return u
        elif isinstance(u, str):
            return UUID(u)
        else:
            raise TypeError('Must pass str or UUID')

    def to_dict(self) -> dict:
        """
        Package the HistoryTrace instance as a dict. Converts all UUIDs to <str> representation for JSON compatibility.
        """

        dbs_str = [str(db) for db in self.data_blocks]
        hist_str = self.get_all_data_blocks_history()

        return {'history': hist_str, 'data_blocks': dbs_str}

    @staticmethod
    def from_dict(d: dict) -> dict:
        """
        Format a dict stored using HistoryTrace.to_dict so that it can be used to create a HistoryTrace instance.
        Converts all the <str> representations of UUID back to :class:`<uuid.UUID>` types.

        :param d: dict containing appropriate 'history' and 'datablocks' keys. Must be packaged by HistoryTrace.to_dict()
        :return: dict formatted so that it can be used to instantiate a HistoryTrace instance recapitulating the HistoryTrace it was packaged from.
        """

        hist = {HistoryTrace._to_uuid(k): v for k, v in d['history'].items()}
        dbs = [HistoryTrace._to_uuid(u) for u in d['data_blocks']]

        return {'history': hist, 'data_blocks': dbs}

    def to_json(self, path: str):
        """
        Save HistoryTrace to a JSON file.

        :param path: file path, usually ends with .json
        """

        json.dump(self.to_dict(), open(path, 'w'))

    @classmethod
    def from_json(cls, path: str):
        """
        Instantiate HistoryTrace from JSON file (that was saved using HistoryTrace.to_json)

        :param path: file path, usually ends with .json
        """

        j = json.load(open(path, 'r'))
        j = HistoryTrace.from_dict(j)

        return cls(history=j['history'], data_blocks=['data_blocks'])

    def to_pickle(self, path: str):
        """
        Dump this instance to a pickle

        :param path: file path
        """
        pickle.dump(self.to_dict(), open(path, 'wb'))

    @classmethod
    def from_pickle(cls, path: str):
        """
        Load HistoryTrace that was pickled

        :param path: file path
        """
        p = pickle.load(open(path, 'r'))
        p = HistoryTrace.from_dict(p)
        return cls(history=p['history'], data_blocks=p['data_blocks'])

    @classmethod
    def merge(cls, history_traces: list):
        """
        Merge a list of HistoryTrace instances into one HistoryTrace instance.
        Useful when merging Transmission objects.

        :param history_traces: list of HistoryTrace instances
        """

        assert all(isinstance(h, HistoryTrace) for h in history_traces)
        data_blocks_l2_list = [h.data_blocks for h in history_traces]
        data_blocks = list(chain.from_iterable(data_blocks_l2_list))

        history = dict()
        for h in history_traces:
            d = h.history
            history.update(d)

        return cls(history=history, data_blocks=data_blocks)

    def draw_graph(self, data_block_id: Union[str, UUID], **kwargs) -> str:
        """
        Draw graph of a data block. kwargs are passed to `mesmerize.plotting.utils.draw_graph`

        :param data_block_id: data block ID from which to get history to draw in a graph
        :type data_block_id: Union[str, UUID]

        :return: file path to the graph pdf file
        :rtype: str
        """
        db_history = self.get_data_block_history(data_block_id, copy=True)

        cleaned = HistoryTrace.clean_history_trace(db_history)

        return draw_graph(cleaned, **kwargs)

    @staticmethod
    def clean_history_trace(db_history: list) -> list:
        """
        Cleans up excessive data such as frequencies linspaces and linkage matrices so the graph is viewable.

        :param db_history: data block history
        :return: data block history with excessive params removed
        """

        for op in db_history:
            o = list(op.keys())[0]
            params = op[o]
            op[o] = HistoryTrace._cleanup_params(o, params)

        return db_history

    @staticmethod
    def _cleanup_params(operation, params):
        log = params.copy()
        if operation == 'rfft':
            log.pop('frequencies')
        elif operation == 'fcluster':
            log.pop('linkage_matrix')

        return log


class BaseTransmission:
    def __init__(self, df: pd.DataFrame, history_trace: HistoryTrace, proj_path: str = None, last_output: str = None,
                 last_unit: str = None, ROI_DEFS: list = None, STIM_DEFS: list = None, CUSTOM_COLUMNS: list = None,
                 plot_state: dict = None):
        """
        Base class for common Transmission functions

        :param  df:             Transmission dataframe
        :param  history_trace:  HistoryTrace object, keeps track of the nodes & node parameters
                                the transmission has been processed through
        :param  proj_path:      Project path, necessary for the datapoint tracer
        :param  last_output:    Last data column that was appended via a node's operation
        :param  last_unit:      Current units of the data. Refers to the units of column in last_output
        :param plot_state:      State of a plot, such as data and label columns. Used when saving interactive plots.

        :type df:               pd.DataFrame
        :type history_trace:    HistoryTrace
        :type proj_path:        str
        :type last_output:      str
        :type last_unit:        str
        :type plot_state:       dict

        :ivar df:               DataFrame instance
        :ivar history_trace:    :class:`HistoryTrace instance <mesmerize.analysis.data_types.HistoryTrace>`
        :ivar last_output:      Name of the DataFrame column that contains data from the most recent node
        :ivar last_unit:        The data units for the data in the column of 'last_output'
        :ivar plot_state:       State of a plot, containing user entered plot parameters. Used for storing interactive plot states.
        """

        self.df = df

        if isinstance(history_trace, HistoryTrace):
            self.history_trace = history_trace
        elif isinstance(history_trace, dict):
            self.history_trace = HistoryTrace(**history_trace)

        self._proj_path = None
        if proj_path is not None:
            self.set_proj_path(proj_path)

        self.last_output = last_output
        self.last_unit = last_unit

        if ROI_DEFS is None:
            self.ROI_DEFS = []
        else:
            assert isinstance(ROI_DEFS, list)
            self.ROI_DEFS = ROI_DEFS

        if STIM_DEFS is None:
            self.STIM_DEFS = []
        else:
            assert isinstance(STIM_DEFS, list)
            self.STIM_DEFS = STIM_DEFS

        if CUSTOM_COLUMNS is None:
            self.CUSTOM_COLUMNS = []
        else:
            assert isinstance(CUSTOM_COLUMNS, list)
            self.CUSTOM_COLUMNS = CUSTOM_COLUMNS

        self.plot_state = plot_state  #: If used in a plot, dict containing information about the plot state

    def to_dict(self) -> dict:
        """
        Package Transmission as a dict, useful for saving to hdf5 or pickle
        """
        d = {'df':              self.df,
             'history_trace':   self.history_trace.to_dict(),
             'last_output':     self.last_output,
             'last_unit':       self.last_unit,
             'plot_state':      self.plot_state
             }

        return d

    def to_hdf5(self, path: str):
        """
        Save as an hdf5 file. Uses pytables to save the DataFrame, serielizes the HistoryTrace using JSON.
        See :class:`HdfTools <mesmerize.common.utils.HdfTools>`

        :param path: file path, usually ends in .trn
        """
        d = self.to_dict()
        df = d.pop('df')
        HdfTools.save_dataframe(path=path, dataframe=df, metadata=d, metadata_method='json')

    @classmethod
    def from_hdf5(cls, path: str):
        """
        Create Transmission from an hdf5 file. See :class:`HdfTools <mesmerize.common.utils.HdfTools>` for information on the file structure.

        :param path: file path, usually ends in .trn (.ptrn for plots)
        """
        df, meta = HdfTools.load_dataframe(path)
        return cls(df, **meta)

    @classmethod
    def from_pickle(cls, path):
        """
        Load Transmission from a pickle.

        :param path: file path, usually ends in .trn
        """
        p = pickle.load(open(path, 'rb'))
        return cls(**p)

    def to_pickle(self, path: str):
        """
        Save Transmission as a pickle.  Not recommended for sharing data, use :func:`~to_hdf5`

        :param path: file path, usually ends in .trn
        """
        pickle.dump(self.to_dict(), open(path, 'wb'), protocol=4)

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def empty_df(transmission, addCols: list = None) -> pd.DataFrame:
        """
        Just a helper method to return an empty DataFrame with the same columns

        :param transmission: Transmission object that forms the basis
        :param addCols: list of columns to add

        :return: The input transmission with an empty dataframe containing the same columns and any additional columns that were passed

        """
        if addCols is None:
            addCols = []

        c = list(transmission.df.columns) + addCols
        e_df = pd.DataFrame(columns=c)
        return e_df
        # return cls(e_df, transmission.history_trace, **transmission.kwargs)

    def get_proj_path(self) -> str:
        """
        Get the project root dir associated to this Transmission.

        :return: Root directory of the project
        """
        if self._proj_path is None:
            raise ValueError('No project path set')
        return self._proj_path

    def set_proj_path(self, path: str):
        """
        Set the project root dir for this transmission.

        Used for finding associated project files, for example the Datapoint Tracer uses it to find max and std projections of image sequences.

        :param path: Root directory of the project
        """

        path = os.path.abspath(path)

        if not os.path.isdir(path + '/images'):
            raise NotADirectoryError('images directory not found')
        if not os.path.isfile(path + '/config.cfg'):
            raise FileNotFoundError('Project config not found')

        self._proj_path = path

    def set_proj_config(self):
        """
        Sets some project config related attributes from the project's config file.
        """
        proj_path = self.get_proj_path()
        if proj_path is None:
            raise ValueError('Project path must be set before setting project configuration')

        config_path = proj_path + '/config.cfg'

        proj_config = RawConfigParser(allow_no_value=True)
        proj_config.optionxform = str
        proj_config.read(config_path)

        self.ROI_DEFS = proj_config.options('ROI_DEFS')
        self.STIM_DEFS = proj_config.options('STIM_DEFS')
        self.CUSTOM_COLUMNS = proj_config.options('CUSTOM_COLUMNS')


class Transmission(BaseTransmission):
    """The transmission object used throughout the flowchart"""
    @classmethod
    def from_proj(cls, proj_path: str, dataframe: pd.DataFrame, sub_dataframe_name: str = 'root',
                  dataframe_filter_history: dict = None):
        """
        :param proj_path: root directory of the project
        :param dataframe: Chosen Child DataFrame from the Mesmerize Project
        :param sub_dataframe_name: Name of the sub DataFrame to load
        :param dataframe_filter_history: Filter history of the child dataframe

        """
        df = dataframe.copy()
        print('Collecting image metadata')
        tqdm().pandas()
        df[['meta', 'stim_maps']] = df.progress_apply(lambda r: Transmission._load_files(proj_path, r), axis=1)

        Transmission._load_imginfo.cache_clear()

        try:
            print('Collecting curve data')
            df['_RAW_CURVE'] = df['ROI_State'].progress_apply(
                    lambda r: r['curve_data'][1]
                )
        except:
            raise IndexError("Curve data missing from one of your samples.\n"
                             "See the progress bar to get the row index of "
                             "the project dataframe where the curve data are missing")

        try:
            print('Collecting curve data')
            df['_SPIKES'] = df['ROI_State'].progress_apply(
                lambda r: r['spike_data'][1] if (r['spike_data'] is not None) else None
            )

        except KeyError:
            warn('spikes or data not found, probably is probably from Mesmerize version < 0.2')

        try:
            print('Collecting dfof data')
            df['_DFOF'] = df['ROI_State'].progress_apply(
                lambda r: r['dfof_data'][1] if (r['dfof_data'] is not None) else None
            )
        except KeyError:
            warn('dfof data not found, probably is probably from Mesmerize version < 0.2')

        df.sort_values(by=['SampleID'], inplace=True)
        df = df.reset_index(drop=True)

        h = HistoryTrace()
        df, block_id = h.create_data_block(df)

        params = {'sub_dataframe_name': sub_dataframe_name, 'dataframe_filter_history': dataframe_filter_history}
        h.add_operation(data_block_id=block_id, operation='spawn_transmission', parameters=params)

        proj_config = get_proj_config(proj_path)

        try:
            roi_type_defs = proj_config.options('ROI_DEFS')
            stim_type_defs = proj_config.options('STIM_DEFS')
            custom_columns = proj_config.options('CUSTOM_COLUMNS')
        except:
            raise ValueError('Could not read project configuration when creating Transmission'
                             '\n' + traceback.format_exc())

        return cls(df, proj_path=proj_path, history_trace=h, last_output=None, last_unit='time',
                   ROI_DEFS=roi_type_defs, STIM_DEFS=stim_type_defs, CUSTOM_COLUMNS=custom_columns)

    @staticmethod
    @lru_cache(maxsize=get_environment().LRU_CACHE_MAXSIZE)
    def _load_imginfo(path: str) -> dict:
        return pickle.load(open(path, 'rb'))

    @staticmethod
    def _load_files(proj_path: str, row: pd.Series) -> pd.Series:
        """Loads npz of curve data and pickle files containing metadata using the paths specified in each row of the
        chosen sub-dataframe of the project"""

        pik_path = os.path.join(proj_path, row['ImgInfoPath'])
        pik = Transmission._load_imginfo(pik_path)
        meta = pik['meta']
        stim_maps = pik['stim_maps']

        return pd.Series(
            {
                'meta': meta,
                'stim_maps': [[stim_maps]]
            }
        )

    def get_data_block_dataframe(self, data_block_id: Union[UUID, str]) -> pd.DataFrame:
        """
        Get the DataFrame rows corresponding to a single data block.

        :param data_block_id: data block uuid
        :return: DataFrame with rows from the specified data block
        """
        if isinstance(data_block_id, UUID):
            data_block_id = str(data_block_id)
        assert isinstance(data_block_id, str)

        if UUID(data_block_id) not in self.history_trace.data_blocks:
            raise DataBlockNotFound(data_block_id)

        return self.df[self.df._BLOCK_ == data_block_id]

    @classmethod
    def merge(cls, transmissions: list):
        """
        Merges a list of Transmissions into one transmission. A single DataFrame is created by simple concatenation.
        HistoryTrace objects are also merged using HistoryTrace.merge.

        :param transmissions: A list containing Transmission objects to merge
        :return: Merged transmission
        """
        proj_path_list = [os.path.abspath(t.get_proj_path()) for t in transmissions]
        if len(set(proj_path_list)) > 1:
            raise ValueError('You cannot merge transmissions from different projects. '
                             'You have tried to merge transmissions from the following projects: '
                             + '\n'.join(set(proj_path_list)))
        else:
            proj_path = proj_path_list[0]
            roi_defs = transmissions[0].ROI_DEFS
            stim_defs = transmissions[0].STIM_DEFS
            custom_columns = transmissions[0].CUSTOM_COLUMNS

        units = set([t.last_unit for t in transmissions])

        if len(units) > 1:
            raise ValueError('Cannot merge transmissions of differing data units. The inputs have the following '
                             'units in their last output data column: \n' + str(units))

        dfs = [t.df for t in transmissions]
        df = pd.concat(dfs, copy=True)

        h = [t.history_trace for t in transmissions]
        h = HistoryTrace.merge(h)

        return cls(df, proj_path=proj_path, history_trace=h,
                   ROI_DEFS=roi_defs, STIM_DEFS=stim_defs, CUSTOM_COLUMNS=custom_columns)
