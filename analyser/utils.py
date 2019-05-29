#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import pandas as pd


def get_cluster_proportions(cluster_labels: iter, group_labels: iter) -> pd.DataFrame:
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
