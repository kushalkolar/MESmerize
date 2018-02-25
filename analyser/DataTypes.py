#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import pandas as pd
import numpy as np
import pickle
from copy import deepcopy
from MesmerizeCore import configuration

class Transmission:
    def __init__(self, df, src, dst=None):
        """
        :type df: pd.DataFrame
        """
        self.df = df.copy()
        self.src = src
        self.dst = dst
        self.STIM_DEFS = configuration.cfg.options('STIM_DEFS')
        if src == 'raw' or 'deriv':
            self.plot_this = 'curve'

    @classmethod
    def from_proj(cls, df):
        assert isinstance(df, pd.DataFrame)
        df[['raw', 'stimMaps']] = df.apply(Transmission._loadnpz, axis=1)

        return cls(df, src='raw')

    @staticmethod
    def _loadnpz(row):
        path = row['CurvePath']
        npz = np.load(path)
        return pd.Series({'curve': npz.f.curve[1], 'stimMaps': npz.f.stimMaps})

    @classmethod
    def from_pickle(cls, path):
        p = pickle.load(open(path, 'rb'))
        return cls(p['df'], p['src'])

    def to_pickle(self, path):
        d = {'df': self.df, 'src': self.src, 'dst': self.dst}
        pickle.dump(d, path, protocol=4)

    def copy(self):
        return deepcopy(self)

    # @property
    # def src(self):
    #     return self._src
    #
    # @src.setter
    # def src(self, source):
    #     self._src = source + '_' + uuid4().hex

