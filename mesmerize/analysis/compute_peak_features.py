#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
from scipy.integrate import simps
from .data_types import Transmission
from ..common.configuration import IS_WINDOWS
from ..common import get_sys_config
from tqdm import tqdm
import pandas as pd
import uuid
from warnings import warn

if not IS_WINDOWS:
    from multiprocessing import Pool
else:
    from multiprocessing.pool import ThreadPool as Pool


feature_list = \
[
    '_pf_ampl_rel_b_ix_l',
    '_pf_ampl_rel_b_ix_r',
    '_pf_ampl_rel_b_mean',
    '_pf_ampl_rel_zero',
    '_pf_area_rel_zero',
    '_pf_area_rel_min',
    '_pf_rising_slope_avg',
    '_pf_falling_slope_avg',
    '_pf_duration_base',
    '_pf_peak_curve',
    '_pf_uuid',
    '_pf_p_ix',
    '_pf_b_ix_l',
    '_pf_b_ix_r'
]

nan_dict = {k: np.nan for k in feature_list}


class ComputePeakFeatures:
    def compute(self, transmission: Transmission, data_column: str):
        self.t = transmission
        self.t.df.reset_index(drop=True, inplace=True)
        self.data_column = data_column
        with Pool(get_sys_config()['_MESMERIZE_N_THREADS']) as pool:
            dfs = list(tqdm(pool.imap(self._per_curve, self.t.df.iterrows()), total=self.t.df.index.size))

        self.t.df = pd.concat([df for df in dfs if df is not None]).reset_index(drop=True)

        return self.t

    def _per_curve(self, row: pd.Series):
        row = row[1]
        pb_df = row['peaks_bases']

        curve = row[self.data_column]

        out_df = pb_df[pb_df.label == 'peak']

        if out_df.empty:
            return None

        pd.options.mode.chained_assignment = None

        out_df[
            [
                '_pf_ampl_rel_b_ix_l',
                '_pf_ampl_rel_b_ix_r',
                '_pf_ampl_rel_b_mean',
                '_pf_ampl_rel_zero',
                '_pf_area_rel_zero',
                '_pf_area_rel_min',
                '_pf_rising_slope_avg',
                '_pf_falling_slope_avg',
                '_pf_duration_base',
                '_pf_peak_curve',
                '_pf_uuid',
                '_pf_p_ix',
                '_pf_b_ix_l',
                '_pf_b_ix_r'
            ]

        ] \
            = out_df.apply(lambda r: self._per_peak(r, curve, pb_df), axis=1)

        row_dup = pd.DataFrame([row] * out_df.index.size)
        out_df = pd.concat([row_dup.reset_index(drop=True), out_df.reset_index(drop=True)], axis=1)
        return out_df

    def _per_peak(self, row, curve, pb_df):
        p_ix = row.event  #: Peak index relative to the whole curve
        ix = row.name

        if ix == (pb_df.index.size - 1) or ix == 0:
            warn(f"Peak at curve index: <{p_ix}> is not flanked by bases on both sides, ignoring")
            return pd.Series(nan_dict)

        try:
            if pb_df.iloc[ix - 1].label != 'base' and pb_df.iloc[ix + 1].label != 'base':
                warn(f"Peak at curve index: <{p_ix}> is not flanked by bases on both sides, ignoring")
                return pd.Series(nan_dict)

        except IndexError as e:
            warn(f"Index error with a peak, probably missing a flanking base:\n{e}\nignoring")
            return pd.Series(nan_dict)

        b_ix_l = pb_df.iloc[ix - 1].event  #: Left base index relative to the whole curve
        b_ix_r = pb_df.iloc[ix + 1].event  #: Right base index relative to the whole curve

        max_ix = len(curve) - 1

        if (b_ix_l > max_ix) or (b_ix_r > max_ix) or (p_ix > max_ix):
            warn(f'Base or peak index out of bounds for peak at curve index: <{p_ix}>, ignoring')
            return pd.Series(nan_dict)

        peak_curve = curve[b_ix_l:b_ix_r]

        out = {'_pf_ampl_rel_b_ix_l': curve[p_ix] - curve[b_ix_l],
               '_pf_ampl_rel_b_ix_r': curve[p_ix] - curve[b_ix_r],
               '_pf_ampl_rel_b_mean': curve[p_ix] - np.mean((curve[b_ix_l], curve[b_ix_r])),
               '_pf_ampl_rel_zero': curve[p_ix],
               '_pf_area_rel_zero': simps(peak_curve),
               '_pf_area_rel_min': simps(peak_curve - np.min(peak_curve)),
               '_pf_rising_slope_avg': abs(curve[b_ix_l] - curve[p_ix]) / abs(p_ix - b_ix_l),
               '_pf_falling_slope_avg': abs(curve[b_ix_r] - curve[p_ix]) / abs(p_ix - b_ix_r),
               '_pf_duration_base': peak_curve.size,
               '_pf_peak_curve': peak_curve,
               '_pf_uuid': str(uuid.uuid4()),
               '_pf_p_ix': p_ix,
               '_pf_b_ix_l': b_ix_l,
               '_pf_b_ix_r': b_ix_r
               }

        return pd.Series(out)
