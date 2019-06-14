#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ....analysis.math.cross_correlation import *
import numpy as np


class CC_Data:
    def __init__(self, ccs: np.ndarray = None,
                 lag_matrix: np.ndarray = None,
                 epsilon_matrix: np.ndarray = None):
        self.ccs = ccs
        self.lag_matrix = lag_matrix
        self.epsilon_matrix = epsilon_matrix

    def get_threshold_matrix(self, matrix_type: str, lag_thr: float, max_thr: float, lag_thr_abs: bool = True) -> np.ndarray:
        # Get lag and maxima matrices
        l = self.lag_matrix
        m = self.epsilon_matrix

        if (l is None) or (m is None):
            raise ValueError('No lag or maxima data available')

        # The type of matrix to return
        if matrix_type == 'lag':
            a = np.copy(l)
        elif matrix_type == 'maxima':
            a = np.copy(m)
        else:
            raise ValueError('Argument "matrix_type" must be "lag" or "maxima"')

        # Set all values below both thresholds to nan
        if lag_thr_abs:
            a[np.abs(l) > lag_thr] = np.nan
        else:
            a[l > lag_thr] = np.nan

        a[m < max_thr] = np.nan

        return a


def compute_cc_data(curves: np.ndarray) -> CC_Data:
    n_curves = curves.shape[0]
    m = curves.shape[1]
    ccs = np.zeros(shape=(n_curves, n_curves, (2 * m) - 1))
    ccs = compute_ccs(curves, ccs)
    
    l = get_lag_matrix(ccs=ccs)
    e = get_epsilon_matrix(ccs=ccs)
    
    return CC_Data(ccs, l, e)


def compute_ccs(a: np.ndarray, out: np.ndarray):
    n = a.shape[0]
    for i in range(n):
        for j in range(n):
            out[i, j, :] = ncc_c(a[i], a[j])
    return out


if __name__ == '__main__':
    from analysis import Transmission
    t = Transmission.from_hickle('/home/kushal/Sars_stuff/mesmerize_toy_datasets/cesa_hnk1_raw_data.trn')
    df = t.df
    df['spliced'] = df._RAW_CURVE.apply(lambda x: x[:2990])
    data = data = np.vstack(df[df.SampleID == 'a2-_-t1']['spliced'])
    