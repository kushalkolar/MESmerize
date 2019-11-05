#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @author: kushal

# Chatzigeorgiou Group
# Sars International Centre for Marine Molecular Biology

# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007


import numpy as np
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from .data_types import Transmission
from ..common import get_sys_config
from uuid import uuid4
from typing import *


class StimulusExtraction:
    def __init__(self,
                 transmission: Transmission,
                 data_column: str,
                 stimulus_type: str,
                 start_offset: int,
                 end_offset: int,
                 zero_pos: str):

        self.t = transmission
        self.t.df.reset_index(drop=True, inplace=True)

        self.data_column = data_column
        self.stimulus_type = stimulus_type

        self.start_offset = start_offset
        self.end_offset = end_offset

        accepted = ['start_offset', 'stim_end', 'stim_center']
        if zero_pos not in accepted:
            raise ValueError(f'Invalid "zero_pos" argument. Must pass one of:\n{accepted}')

        self.zero_pos = zero_pos

    def extract(self) -> Transmission:

        samples = self.t.df.SampleID.unique()

        n_threads = get_sys_config()['_MESMERIZE_N_THREADS']

        with Pool(n_threads) as p:
            dfs = list(
                tqdm(
                    p.imap(self._per_sample, samples),
                    total=len(samples),
                    position=0,
                    desc='samples'
                )
            )

        self.t.df = pd.concat([df for df in dfs if df is not None]).reset_index(drop=True)

        # self.t.df = self.t.df.explode('_st_stim_curve')

        return self.t

    def _per_sample(self, sample_id: str) -> pd.DataFrame:

        sub_df = self.t.df[self.t.df.SampleID == sample_id].copy()
        sub_df.reset_index(drop=True, inplace=True)

        stim_df = sub_df.stim_maps.iloc[0][0][0][self.stimulus_type]

        stim_df['start'] = stim_df['start'].astype(np.int64)
        stim_df['end'] = stim_df['end'].astype(np.int64)

        stim_df = stim_df.sort_values(by='start').reset_index(drop=True)

        out_dfs = []

        for ix, r in tqdm(stim_df.iterrows(), total=stim_df.index.size, position=1, desc='stimulus period'):
            sp_df = self._per_stimulus_period(sub_df, r['name'], r['start'], r['end'])
            out_dfs.append(sp_df)

        return pd.concat(out_dfs).reset_index(drop=True)

    # TODO: This can be done MUCH faster with DataFrame.explode but need to figure out how to keep all curve specific data
    def _per_stimulus_period(self, sub_df: pd.DataFrame, st_name: str, st_start: int, st_end: int) -> pd.DataFrame:
        """
        Extract a single stimulus period from all curves

        :param curves:
        :param st_name:
        :param st_start:
        :param st_end:
        :return:
        """

        curve_uuids = sub_df['uuid_curve'].values

        cols = sub_df.columns.to_list() + ['ST_NAME', 'ST_TYPE', '_ST_START_IX', '_ST_END_IX', '_ST_CURVE', 'ST_uuid']
        out_df = pd.DataFrame(columns=cols)

        for u in curve_uuids:
            # Do each separately to accommodate for varying curve lengths
            s = sub_df[sub_df['uuid_curve'] == u].iloc[0].copy()

            curve = s[self.data_column]

            start_ix, end_ix = self._apply_offsets(st_start, st_end, curve.size - 1)

            s['ST_NAME'] = st_name
            s['ST_TYPE'] = self.stimulus_type
            s['_ST_START_IX'] = start_ix
            s['_ST_END_IX'] = end_ix
            s['_ST_CURVE'] = curve[start_ix:end_ix]
            s['ST_uuid'] = str(uuid4())

            out_df = out_df.append(s, ignore_index=True)

        return out_df

    def _apply_offsets(self, start_ix, end_ix, max_ix) -> Tuple[int, int]:
        if self.zero_pos == 'start_offset':
            tstart = max(start_ix + self.start_offset, 0)
            tend = min(end_ix + self.end_offset, max_ix)

        elif self.zero_pos == 'stim_end':
            tstart = end_ix
            tend = min(end_ix + self.end_offset, max_ix)

        elif self.zero_pos == 'stim_center':
            tstart = int(((start_ix + end_ix) / 2)) + self.start_offset
            tend = min(end_ix + self.end_offset, max_ix)

        return tstart, tend
