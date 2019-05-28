#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
from tslearn.cycc import normalized_cc
from tslearn.preprocessing import TimeSeriesScalerMeanVariance, TimeSeriesScalerMinMax
# from sklearn.metrics import pairwise_distances


def ncc_c(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    cc = normalized_cc(x.reshape(-1, 1), y.reshape(-1, 1))
    return cc


def get_omega(x: np.ndarray, y: np.ndarray) -> int:
    cc = ncc_c(x, y)
    w = np.argmax(cc)
    return w


def get_lag(x: np.ndarray, y: np.ndarray) -> int:
    w = get_omega(x, y)
    s = w - x.shape[0]
    return s


def get_epsilon(x, y) -> float:
    cc = ncc_c(x, y)
    e = np.max(cc)
    return e


# if normalize == 'z':
#     data = TimeSeriesScalerMeanVariance().fit_transform(data)[:, :, 0]
# elif normalize == 'minmax':
#     data = TimeSeriesScalerMinMax().fit_transform(data)[:, :, 0]

def get_lag_matrix(data: np.ndarray) -> np.ndarray:
    m = data.shape[0]
    a = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            a[i, j] = get_lag(data[i], data[j])
    return a


def get_epsilon_matrix(data: np.ndarray) -> np.ndarray:
    m = data.shape[0]
    a = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            a[i, j] = get_epsilon(data[i], data[j])
    return a
