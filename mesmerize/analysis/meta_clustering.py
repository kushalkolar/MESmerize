import abc
from typing import Dict, List, Tuple, Iterable, Generator, Any, Optional, Union
import numpy as np
import itertools
from collections import OrderedDict
from multiprocessing import Pool

from sklearn.cluster import AgglomerativeClustering
from .clustering_metrics import davies_bouldin_score, pairwise_distances
from scipy.stats import wasserstein_distance
from .math import modln, modlog10
from copy import deepcopy
from scipy.fftpack import rfft


def dict_product(d: OrderedDict[str, Iterable]) -> Generator[OrderedDict[str, object]]:
    for i in itertools.product(*d.values()):
        yield OrderedDict(zip(d.keys(), i))


class BaseMetaClustering(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        self._result = None

    @abc.abstractmethod
    def run_clustering(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def score_cluster(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def run_iter(self, params: dict) -> float:
        """
        Runs an single iteration of clustering and scoring the respective cluster and returns a single score.
        :param params:  dict of parameter combination for a single iteration
        :return:        score
        """
        pass

    @abc.abstractmethod
    def run(self, num_threads, *args, **kwargs) -> None:
        pass

    @abc.abstractmethod
    @property
    def param_iters(self) -> list:
        pass

    @abc.abstractmethod
    @property
    def result(self) -> list:
        pass


class MetaClustering(BaseMetaClustering):
    def __init__(self, data: np.ndarray, param_iters: OrderedDict[str, Iterable[Any]], metric: Union[str, callable],
                 score_metric: Union[str, callable], *args, clustering_func: Optional[callable] = None, **kwargs):
        """

        :param data:    Input data used for clustering
        :param metric:  metric for computing the distance matrices, passed to sklearn.metric.pairwise_distances
        :param score_metric: metric for scoring clusters. If passing a callable it must accept output from the subclass run_clustering() method.
        :param params:  Dict[clustering_kwarg: iterable_of_possible_values], Each possible value is passed to run_clustering().
        """
        super().__init__(*args, **kwargs)
        self.data = data
        self._metric = metric
        self._score_metric = score_metric

        self.product = dict_product(param_iters)
        self._param_iters = list(deepcopy(self.product))

        self.clustering_func = clustering_func

    @property
    def param_iters(self) -> list:
        return self._param_iters

    @property
    def result(self) -> list:
        if self._result is None:
            raise ValueError('No results are available')
        else:
            return self._result

    def run_clustering(self, data: np.ndarray, params: dict) -> Tuple[np.ndarray, Optional[tuple], Optional[dict]]:
        """
        :return: cluster labels, and any args or kwargs that are passed to score_cluster() method
        """
        if self.clustering_func is not None:
            return self.clustering_func(params)
        else:
            raise NotImplementedError('Must pass callable to "clustering_func" '
                                      'of constructor or subclass MetaClustering')

    def score_cluster(self, params: dict, cluster_labels: np.ndarray, *args, **kwargs):
        if self._score_metric == 'davies_bouldin':
            return davies_bouldin_score(data=self.data, metric=self._metric, cluster_labels=cluster_labels)
        elif callable(self._score_metric):
            return self._score_metric(data=self.data, metric=self._metric, cluster_labels=cluster_labels, *args,
                                      **kwargs)
        # raise NotImplementedError

    def run_iter(self, params: OrderedDict) -> float:
        cluster_labels, args, kwargs = self.run_clustering(data, params)
        scores = self.score_cluster(params, cluster_labels, *args, **kwargs)
        return np.mean(scores)

    def run(self, num_threads: int, *args, **kwargs):
        p = Pool(num_threads)
        self._result = p.map(self.run_iter, self.product)


class MetaAgglomerative(MetaClustering):
    def __init__(self, data: np.ndarray, param_iters: OrderedDict[str, Iterable[Any]], metric: Union[str, callable],
                 score_metric: Union[str, callable], *args, **kwargs):

        super().__init__(data, param_iters, metric, score_metric, *args, **kwargs)

        log_values = ['raw', 'ln_abs', 'log10_abs', 'modln', 'modlog10']
        if 'log_type' in params.keys():
            if not set(params['log_type']).issubset(log_values):
                raise ValueError(f'Allowed log_type param values are: {log_values}')

        linkage_values = ['complete', 'average', 'single']
        if 'linkage' in params.keys():
            if not set(params['linkage']).issubset(linkage_values):
                raise ValueError(f'Allowed linkage param values are: {linkage_values}')

    def _get_log(self, data, method: int) -> np.ndarray:
        if method == 'raw':
            return data
        elif method == 'ln_abs':
            return np.log(np.abs(data))
        elif method == 'log10_abs':
            return np.log10(np.abs(data))
        elif method == 'modln':
            return modln(data)
        elif method == 'modlog10':
            return modlog10(data)

    def _preprocess(self, params: dict) -> np.ndarray:
        data = rfft(self.data)

        if 'freq_cutoff' in params.keys():
            cutoff = params['freq_cutoff']
            data = data[:, :cutoff]

        if 'log_method' in params.keys():
            data = self._get_log(data, params['log_method'])

        return data

    def run_clustering(self, data: np.ndarray, params: dict) -> np.ndarray:
        kwargs = dict(n_clusters=params['n_clusters'], linkage=params['linkage'])
        dist_m = pairwise_distances(data, metric=self._metric)
        agg = AgglomerativeClustering(affinity='precomputed', **kwargs)
        agg.fit(dist_m)

        return agg.labels_

    def run_iter(self, params: dict) -> float:
        data = self._preprocess(params)
        cluster_labels = self.run_clustering(data, params)
        scores = self.score_cluster(params, cluster_labels)
        return np.mean(scores)


if __name__ == '__main__':
    data = np.random.random((100, 100))
    params = OrderedDict(n_clusters=    range(2, 20),
                         linkage=       ['complete', 'average', 'single'],
                         freq_cutoff=   range(100, 801, 50),
                         log_type=      ['raw', 'ln_abs', 'log10_abs', 'modln', 'modlog10'])

    meta_agg = MetaAgglomerative(data, params, metric=wasserstein_distance, score_metric='davies_bouldin')
