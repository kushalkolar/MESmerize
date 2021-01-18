from sklearn.metrics import pairwise_distances
from typing import Tuple, Optional, Union
import numpy as np
from ..common import get_sys_config


def get_centerlike(cluster_members: np.ndarray, metric: Optional[Union[str, callable]] = None,
                   dist_matrix: Optional[np.ndarray] = None) -> Tuple[np.ndarray, int]:
    """
    Finds the 1D time-series within a cluster that is the most centerlike

    :param cluster_members: 2D numpy array in the form [n_samples, 1D time_series]
    :param metric:          Metric to use for pairwise distance calculation, simply passed to sklearn.metrics.pairwise_distances
    :param dist_matrix:     Distance matrix of the cluster members

    :return:                The cluster member which is most centerlike, and its index in the cluster_members array
    """
    if dist_matrix is None:
        dist_matrix = pairwise_distances(cluster_members, metric=metric,
                                         n_jobs=get_sys_config()['_MESMERIZE_N_THREADS'])

    c_ix = np.argmin(np.sum(dist_matrix, axis=0))
    c = cluster_members[c_ix, :]
    return c, c_ix


def get_cluster_radius(cluster_members: np.ndarray, metric: Optional[Union[str, callable]] = None,
                       dist_matrix: Optional[np.ndarray] = None, centerlike_index: Optional[int] = None) -> float:
    """
    Returns the cluster radius according to chosen distance metric

    :param cluster_members: 2D numpy array in the form [n_samples, 1D time_series]
    :param metric:          Metric to use for pairwise distance calculation, simply passed to sklearn.metrics.pairwise_distances
    :param dist_matrix:     Distance matrix of the cluster members
    :param centerlike_index: Index of the centerlike cluster member within the cluster_members array

    :return:                 The cluster radius, average between the most centerlike member and all other members
    """
    if dist_matrix is None:
        dist_matrix = pairwise_distances(cluster_members, metric=metric,
                                         n_jobs=get_sys_config()['_MESMERIZE_N_THREADS'])

    if centerlike_index is None:
        c, c_ix = get_centerlike(cluster_members, dist_matrix)
    else:
        c_ix = centerlike_index

    ra = np.sum(dist_matrix[c_ix, :]) / (cluster_members.shape[0] - 1)
    return ra


def davies_bouldin_score(
        data: np.ndarray, cluster_labels: np.ndarray, metric: Union[str, callable]
    ) -> Tuple[float, np.ndarray]:
    """
    Adopted from sklearn.metrics.davies_bouldin_score to use any distance metric

    :param data:            Data that was used for clustering, [n_samples, 1D time_series]
    :param metric:          Metric to use for pairwise distance calculation, simply passed to sklearn.metrics.pairwise_distances
    :param cluster_labels:  Cluster labels

    :return:                Davies Bouldin Score using EMD
    """
    radii = np.zeros(np.unique(cluster_labels).size)
    centroids = np.zeros((np.unique(cluster_labels).size, data.shape[1]))

    for i, c in enumerate(np.unique(cluster_labels)):
        members = np.take(data, np.where(cluster_labels == c)[0], axis=0)
        dist_m = pairwise_distances(members, metric=metric, n_jobs=get_sys_config()['_MESMERIZE_N_THREADS'])

        centroids[i, :], c_ix = get_centerlike(members, dist_matrix=dist_m)
        radii[i] = get_cluster_radius(members, dist_matrix=dist_m, centerlike_index=c_ix)

    centroid_distances = pairwise_distances(centroids, metric=metric, n_jobs=get_sys_config()['_MESMERIZE_N_THREADS'])

    if np.allclose(radii, 0) or np.allclose(centroid_distances, 0):
        return 0.0, None

    centroid_distances[centroid_distances == 0] = np.inf
    combined_intra_dists = radii[:, None] + radii
    combined_intra_dists = np.nan_to_num(combined_intra_dists, nan=0.0)  # for cases where a cluster has just 1 member

    scores = np.max(combined_intra_dists / centroid_distances, axis=1)

    return (np.nanmean(scores), scores)
