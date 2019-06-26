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


def get_cluster_proportions(cluster_labels: Union[pd.Series, list, set],
                            group_labels: Union[pd.Series, list, set]) -> pd.DataFrame:
    if isinstance(cluster_labels, pd.Series):
        clusters = cluster_labels.unique().tolist()
    else:
        clusters = list(set(cluster_labels))

    if isinstance(group_labels, pd.Series):
        groups = group_labels.unique().tolist()
    else:
        groups = list(set(group_labels))

    cluster_dict = dict.fromkeys(clusters)

    for k in cluster_dict.keys():
        cluster_dict[k] = []

    for ix, cluster in enumerate(cluster_labels):
        cluster_dict[cluster].append(group_labels[ix])

    group_proportions = dict.fromkeys(groups)

    groups_order = []

    for g in group_proportions.keys():
        groups_order.append(g)
        group_proportions[g] = []
        for cl in clusters:
            count = cluster_dict[cl].count(g)
            percentage = count / len(cluster_dict[cl])
            group_proportions[g].append(percentage)

    return pd.DataFrame(group_proportions)


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
    :param columns: DataFrame columns
    :return:        (data_columns, categorical_columns, uuid_columns)
    """
    columns = list(columns)
    columns.remove('_BLOCK_')
    dcols = [c for c in columns if c.startswith('_')]

    ucols = [c for c in columns if ('uuid' in c) or ('UUID' in c)]

    ccols = [c for c in columns if (not c.startswith('_')) and
             (c not in ['CurvePath', 'ImgPath', 'ImgUUID', 'ROI_State', 'meta', 'ImgInfoPath', 'misc']) and
             (c not in ucols)]

    dcols.sort();ccols.sort();ucols.sort()

    return dcols, ccols, ucols
