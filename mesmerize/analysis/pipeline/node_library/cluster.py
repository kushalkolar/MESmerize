#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Kushal Kolar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from fcsugar import *
from ..containers import TransmissionContainer
import numpy as np
from tslearn.clustering import KShape
from typing import *


@node
def kshape(container: TransmissionContainer,
           data_column: str,
           n_clusters: int,
           max_iter: int = 300,
           tol: float = 1e-6,
           n_init: int = 1,
           verbose: bool = True,
           random_state: Union[int, None] = None,
           init: np.ndarray = 'random',
           centroid_seeds: np.ndarray = None):
    """

    :param container:
    :param data_column:
    :param n_clusters:
    :param max_iter:
    :param tol:
    :param n_init:
    :param verbose:
    :param random_state:
    :param init:
    :param centroid_seeds: arrays of shape [n_clusters, ts_size]
    :return:
    """
    if centroid_seeds is not None:
        init = np.swapaxes(np.array([centroid_seeds]).T, 0, 1)

    ks = KShape(n_clusters=n_clusters, max_iter=max_iter,
                tol=tol, n_init=n_init, verbose=verbose,
                random_state=random_state, init=init)

    X = np.vstack(container.df[data_column].values)

    y = ks.fit_predict(X)

    container.df['KSHAPE_CLUSTER'] = y

    return container
