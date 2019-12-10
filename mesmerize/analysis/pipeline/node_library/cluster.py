from fcsugar import *
from ..containers import TransmissionContainer
import numpy as np
from tslearn.clustering import  KShape
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
