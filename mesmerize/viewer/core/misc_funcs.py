#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import pandas as pd
import numpy as np
from ...common import configuration


def empty_df(cols=None, addCols=[]):
    """
    Just returns an empty DataFrame based on columns in the project's config.cfg file. Only really used when a new
    project is started.

    :param cols: column names
    :type cols:  list
    :return:     empty pandas DataFrame with names from list passed in
    :rtype:      pd.DataFrame
    """
    if cols is None:
        include = configuration.proj_cfg.options('INCLUDE')
        exclude = configuration.proj_cfg.options('EXCLUDE')

        cols = include + exclude

    cols = cols + addCols

    if type(cols) is list:
        cols = set(cols)

    return pd.DataFrame(data=None, columns=cols)


def fix_fp_errors(n):
    fix = np.round(n, decimals=1) + 0.0
    return fix
