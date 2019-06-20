import abc
from typing import Dict, List, Tuple, Iterable, Any, Optional, Union
import numpy as np
import itertools
from collections import OrderedDict
from multiprocessing import Pool, sharedctypes
from sklearn.metrics import pairwise_distances, davies_bouldin_score
from sklearn.cluster import AgglomerativeClustering
from scipy.stats import wasserstein_distance
from .clustering_metrics import davies_bouldin_score


class MetaClustering(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run_clustering(self):
        pass

    @abc.abstractmethod
    def score_cluster(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class BaseMetaClustering(MetaClustering):
    def __init__(self, data: np.ndarray, params: Dict[str, Iterable[Any]], *args, **kwargs):
        """

        :param data:    Input data used for clustering
        :param params:  Dict[clustering_kwarg: iterable_of_possible_values], Each possible value is passed to run_clustering().
        """
        self.data = data

        self.params_map = OrderedDict()
        self.params = OrderedDict()

        for p in params.keys():
            self.params_map[p] = OrderedDict(enumerate(params[p]))
            self.params[p] = tuple(self.params_map[p].keys())

        self.output_shape = (len(self.params[p]) for p in self.params.keys())

        self.output_dims = dict(enumerate(self.params.keys()))
        print(self.output_dims)

        self.product = itertools.product(*(self.params[p] for p in self.params.keys()))

        global result
        global shared_array

        result = np.ctypeslib.as_ctypes(np.zeros(self.output_shape))
        shared_array = sharedctypes.RawArray(result._type_, result)

    def map_param(self, param: str, index: int) -> object:
        """
        Returns the actual value of the param from the index
        :param param: name of the param
        :param index: index
        :return: value of the param
        """
        return self.params_map[param][index]

    def run_clustering(self):
        raise NotImplementedError

    def score_cluster(self):
        raise NotImplementedError

    def _add_score(self, score: float, ixs: tuple):
        tmp = np.ctypeslib.as_array(shared_array)
        tmp[ixs] = score

    def run(self):
        pass


class MetaAgglomerative(BaseMetaClustering):
    def __init__(self, data: np.ndarray, params: Dict[str, Iterable[Any]], metric: Union[str, callable],
                 score_method: Optional[Union[str, callable]] = 'davies_bouldin'):

        BaseMetaClustering.__init__(data, params)
        self._metric = metric
        self._score_method = score_method

        self.modln = lambda x: np.sign(x) * np.log(np.abs(x))
        self.modlog10 = lambda x: np.sign(x) * np.log(np.abs(x))

        log_values = ['raw', 'ln_abs', 'log10_abs', 'modln', 'modlog10']
        if 'log_type' in params.keys():
            if not set(params['log_type']).issubset(log_values):
                raise ValueError(f'Allowed log_type param values are: {log_values}')

        linkage_values = ['complete', 'average', 'single']
        if 'linkage' in params.keys():
            if not set(params['linkage']).issubset(linkage_values):
                raise ValueError(f'Allowed linkage param values are: {linkage_values}')

    def _get_log(self, data, method: int) -> np.ndarray:
        method = self.map_param(self.params['log_method'][method])
        if method == 'raw':
            return data
        elif method == 'ln_abs':
            return np.log(np.abs(data))
        elif method == 'log10_abs':
            return np.log10(np.abs(data))
        elif method == 'modln':
            return self.modln(data)
        elif method == 'modlog10':
            return self.modlog10(data)

    def score_cluster(self, ):
        data = self.data
        params = self.params.copy()

        model = AgglomerativeClustering


if __name__ == '__main__':
    data = np.random.random((100, 100))
    params = {'n_clusters': range(2, 20),
              'linkage': ['complete', 'average', 'single'],
              'freq_cutoff': range(100, 801, 50),
              'log_type': ['raw', 'ln_abs', 'log10_abs', 'modln', 'modlog10']
              }

    mc = BaseMetaClustering(data, params)
