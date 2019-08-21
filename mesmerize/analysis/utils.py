#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import numpy as np
import pandas as pd
from typing import *
from . import Transmission


def get_proportions(xs: Union[pd.Series, np.ndarray, list], ys: Union[pd.Series, np.ndarray, pd.Series],
                    xs_name: str = 'xs', ys_name: str = 'ys', swap = False, percentages: bool = True) -> pd.DataFrame:
    """
    Get the proportions of xs vs ys
    :param xs: data plotted on the x axis
    :param ys: proportions of unique elements in ys are calculated per xs
    :param invert: swap x and y
    :return:   DataFrame that can be plotted in a proportions bar graph
    """

    if len(xs) != len(ys):
        raise ValueError('Length of xs and ys must match exactly')

    if isinstance(xs, np.ndarray):
        if xs.ndim > 1:
            raise ValueError('Can only accept 1D numpy array')

    if isinstance(ys, np.ndarray):
        if ys.ndim > 1:
            raise ValueError('Can only accept 1D numpy array')

    if swap:
        xs, ys = ys, xs
        xs_name, ys_name = ys_name, xs_name

    df = pd.DataFrame({xs_name: xs, ys_name: ys})
    if percentages:
        return df.groupby([xs_name, ys_name]).agg({ys_name: 'count'}).groupby(by=xs_name).apply(lambda x: (x / x.sum()) * 100).unstack()
    else:
        return df.groupby([xs_name, ys_name]).agg({ys_name: 'count'}).unstack()


# def get_cluster_proportions(cluster_labels: Union[pd.Series, list, set],
#                             group_labels: Union[pd.Series, list, set]) -> pd.DataFrame:
#     if isinstance(cluster_labels, pd.Series):
#         clusters = cluster_labels.unique().tolist()
#     else:
#         clusters = list(set(cluster_labels))
#
#     if isinstance(group_labels, pd.Series):
#         groups = group_labels.unique().tolist()
#     else:
#         groups = list(set(group_labels))
#
#     cluster_dict = dict.fromkeys(clusters)
#
#     for k in cluster_dict.keys():
#         cluster_dict[k] = []
#
#     for ix, cluster in enumerate(cluster_labels):
#         cluster_dict[cluster].append(group_labels[ix])
#
#     group_proportions = dict.fromkeys(groups)
#
#     groups_order = []
#
#     for g in group_proportions.keys():
#         groups_order.append(g)
#         group_proportions[g] = []
#         for cl in clusters:
#             count = cluster_dict[cl].count(g)
#             percentage = count / len(cluster_dict[cl])
#             group_proportions[g].append(percentage)
#
#     return pd.DataFrame(group_proportions)


def get_sampling_rate(transmission: Transmission, tolerance: Optional[float] = 0.1) -> float:
    """
    Returns the mean sampling rate of all data in a Transmission if it is within the specified tolerance. Otherwise throws an exception.

    :param transmission:    Transmission object of the data from which sampling rate is obtained.
    :type transmission:     Transmission

    :param tolerance:       Maximum tolerance (in Hertz) of sampling rate variation between different samples
    :type tolerance:        float

    :return:                The mean sampling rate of all data in the Transmission
    :rtype:                 float
    """
    sampling_rates = []
    for db in transmission.history_trace.data_blocks:
        if transmission.history_trace.check_operation_exists(db, 'resample'):
            sampling_rates.append(transmission.history_trace.get_operation_params(db, 'resample')['output_rate'])
        else:
            r = pd.DataFrame(transmission.get_data_block_dataframe(db).meta.to_list())['fps'].unique()
            # if rates.size > 1:
            #     raise ValueError("Sampling rates for the data do not match")
            # else:
            sampling_rates.append(r)

    rates = np.hstack([sampling_rates])

    if np.ptp(rates) > tolerance:
        raise ValueError("Sampling rates of the data differ by "
                         "greater than the set tolerance of " + str(tolerance) + " Hz")

    framerate = float(np.mean(sampling_rates))

    return framerate


def get_array_size(transmission: Transmission, data_column: str) -> int:
    """Returns the size of the 1D arrays in the specified data column. Throws an exception if they do not match

    :param transmission:    Desired Transmission
    :param data_column:     Data column of the Transmission from which to retrieve the size

    :type transmission:     Transmission
    :type data_column:      str

    :return:                Size of the 1D arrays of the specified data column
    :rtype:                 int
    """
    if data_column not in transmission.df.columns:
        raise KeyError("Requested data column: " + data_column + " not found in transmission DataFrame")
    array_size = transmission.df[data_column].apply(lambda a: a.size).unique()

    if array_size.size > 1:
        raise ValueError("Size of all arrays in data column must match exactly.")

    return array_size[0]


def organize_dataframe_columns(columns: Iterable[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Organizes DataFrame columns into data column, categorical label columns, and uuid columns.

    :param columns: All DataFrame columns
    :return:        (data_columns, categorical_columns, uuid_columns)
    """
    columns = list(columns)
    if '_BLOCK_' in columns:
        columns.remove('_BLOCK_')

    dcols = [c for c in columns if c.startswith('_')]

    ucols = [c for c in columns if ('uuid' in c) or ('UUID' in c)]

    ccols = [c for c in columns if (not c.startswith('_')) and
             (c not in ['CurvePath', 'ImgPath', 'ImgUUID', 'ROI_State', 'meta', 'ImgInfoPath', 'misc']) and
             (c not in ucols)]

    dcols.sort();ccols.sort();ucols.sort()

    return dcols, ccols, ucols


def pad_arrays(self, a: np.ndarray, method: str = 'random', output_size: int = None, mode: str = 'minimum',
               constant: Any = None) -> np.ndarray:
    """
    Pad all the input arrays so that are of the same length. The length is determined by the largest input array.
    The padding value for each input array is the minimum value in that array.

    Padding for each input array is either done after the array's last index to fill up to the length of the
    largest input array (method 'fill-size') or the padding is randomly flanked to the input array (method 'random')
    for easier visualization.

    :param a: 1D array of input arrays where each element is a sample array
    :param method: one of 'fill-size' or 'random', see docstring for details
    :return: Arrays padded according to the method.
    """
    l = 0  # size of largest time series

    # Get size of largest time series
    for c in a:
        s = c.size
        if s > l:
            l = s

    if (output_size is not None) and (output_size < l):
        raise ValueError('Output size must be equal to larger than the size of the largest input array')
    else:
        l = output_size

    # pre-allocate output array
    p = np.zeros(shape=(a.size, l), dtype=a[0].dtype)

    # pad each 1D time series
    for i in range(p.shape[0]):
        s = a[i].size

        if s == l:
            p[i, :] = a[i]
            continue

        max_pad_en_ix = l - s

        if method == 'random':
            pre = np.random.randint(0, max_pad_en_ix)
        elif method == 'fill-size':
            pre = 0
        else:
            raise ValueError('Must specific method as either "random" or "fill-size"')

        post = l - (pre + s)
        p[i, :] = np.pad(a[i], (pre, post), 'minimum')

    return p
