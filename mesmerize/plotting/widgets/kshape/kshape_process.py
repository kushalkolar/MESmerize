#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
import numpy as np
import pickle
import os
from mesmerize.common.configuration import HAS_TSLEARN, get_sys_config
if HAS_TSLEARN:
    from tslearn.clustering import KShape
from joblib import Parallel, delayed
from typing import *
from scipy import signal
from itertools import product
import json

def run(data_path: str, params_path: str):
    X = np.load(data_path)

    params = pickle.load(open(params_path, 'rb'))
    workdir = params['workdir']

    out = os.path.join(workdir, 'out')
    with open(out, 'w') as f:
        f.write('0')

    print(f'Using work dir: {workdir}')

    print('** Fitting training data **')
    n_train = int((params['kwargs'].pop('train_percent') / 100) * X.shape[0])
    train = X[np.random.choice(X.shape[0], size=n_train, replace=False)]

    if params['do_single']:
        run_single(X, train, params['kwargs'], workdir, out)
    else:
        run_grid(X, train, params['kwargs'], workdir, out)


def run_single(X, train, params, workdir, out):
    kwargs = params
    ks = KShape(**kwargs)

    ks.fit(train)

    print('**** Predicting ****')
    y_pred = ks.predict(X)

    ks_path = os.path.join(workdir, 'ks.pickle')
    pickle.dump(ks, open(ks_path, 'wb'))

    y_pred_path = os.path.join(workdir, 'y_pred.npy')
    np.save(y_pred_path, y_pred)

    train_path = os.path.join(workdir, 'train.npy')
    np.save(train_path, train)

    with open(out, 'w') as f:
        f.write('1')

    print('* Done! *')


# np.array_split(a, n_partitions, axis=0)

def sort_peak_widths(a: np.ndarray):
    widths = [signal.peak_widths(p, [np.argmax(p)])[0][0] for p in a]
    sort_ixs = np.argsort(widths)

    return a[sort_ixs]


def sort_amplitidue(a: np.ndarray):
    ampls = [s.argmax() for s in a]
    sort_ixs = np.argsort(ampls)

    return a[sort_ixs]


def kshape_grid_iter(X_partitioned: List[np.array], kshape_kwargs: dict) -> Tuple[KShape, int]:
    seed_ixs = [np.random.randint(0, X.shape[0] - 1) for X in X_partitioned]
    centroid_seeds = np.array([X_partitioned[i][seed] for i, seed in enumerate(seed_ixs)])
    init = np.swapaxes(np.array([centroid_seeds]).T, 0, 1)

    kshape = KShape(
        n_clusters=len(seed_ixs),
        init=init,
        verbose=True,
        random_state=None,
        **kshape_kwargs
    )

    X = np.vstack(X_partitioned)

    print('** Fitting ks model **')
    kshape.fit(X)

    print('** Predicting **')
    n_clusters_out = np.unique(kshape.predict(X)).size

    # until the tslearn hyper-param json issue is released in the latest pypi version
    kshape.init = kshape.init.tolist()

    return kshape, n_clusters_out


def run_grid(X, train, params, workdir, out):
    sortby = params.pop('sortby')
    if sortby == 'width':
        X_sorted = sort_peak_widths(X)
    elif sortby == 'amplitude':
        X_sorted = sort_amplitidue(X)

    p_range = params.pop('npartitions_range')
    ncombinations = params.pop('ncombinations')

    n_jobs = get_sys_config()['_MESMERIZE_N_THREADS']
    tmpdir = os.path.join(workdir, 'joblib_tmp')

    kg = Parallel(n_jobs=n_jobs, verbose=5, temp_folder=tmpdir)(
        delayed(kshape_grid_iter)(
            np.array_split(X_sorted, nparts, axis=0), params
            ) for nparts in range(*p_range) \
                for i in range(ncombinations)
    )

    kga = [k[0]._to_dict(output='json') for k in kg]

    n_clusters_out = np.array([k[1] for k in kg]).reshape(
        len(range(*p_range)),
        ncombinations
    )

    json.dump(kga, open(os.path.join(workdir, 'kga.json'), 'w'))
    np.save(os.path.join(workdir, 'n_clusters_out.npy'), n_clusters_out)

    with open(out, 'w') as f:
        f.write('1')

    print('* Done! *')


#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
