#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
from tslearn.clustering import KShape
import numpy as np
import pickle


def run(data_path: str, params_path: str):
    X = np.load(data_path)

    params = pickle.load(open(params_path, 'rb'))

    out = params['workdir'] + '/out'
    with open(out, 'w') as f:
        f.write('0')

    print('** Fitting input data **')

    kwargs = params['kwargs']
    ks = KShape(**kwargs)
    ks.fit(X)

    ks_path = params['workdir'] + '/ks.pickle'
    pickle.dump(ks, open(ks_path, 'wb'))

    print('** Fitting predictions **')
    y_pred = ks.fit_predict(X)

    y_pred_path = params['workdir'] + '/y_pred.pickle'
    pickle.dump(y_pred, open(y_pred_path, 'wb'))

    with open(out, 'w') as f:
        f.write('1')

    print('* Done! *')


if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2])
