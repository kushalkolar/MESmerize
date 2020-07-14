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
from ....common.configuration import HAS_TSLEARN
if HAS_TSLEARN:
    from tslearn.clustering import KShape


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

    kwargs = params['kwargs']
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


#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
