#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import sys
# sys.path.append('..')
import pandas as pd
import numpy as np
import pickle
from copy import deepcopy
from MesmerizeCore import configuration
from collections import OrderedDict

class Transmission:
    def __init__(self, df, src, data_column, dst=None):
        """
        :type df: pd.DataFrame
        """
        self.df = df.copy()
        #TODO: Make a graphical thing that display the source history of any node and can be accessed while looking at stastics too
        self.src = src
        self.dst = dst
        self.data_column = data_column
        self.STIM_DEFS = configuration.cfg.options('STIM_DEFS')
        self.ROI_DEFS = configuration.cfg.options('ROI_DEFS')
        self.plot_this = 'curve'

    @classmethod
    def from_proj(cls, df):
        assert isinstance(df, pd.DataFrame)
        df[['curve', 'meta', 'stimMaps']] = df.apply(Transmission._load_files, axis=1)

        return cls(df, src=[{'raw': ''}], data_column='curve')

    @staticmethod
    def _load_files(row):
        path = row['CurvePath']
        npz = np.load(path)
        
        pikPath = row['ImgInfoPath']
        pik = pickle.load(open(pikPath, 'rb'))
        meta = pik['imdata']['meta']
        
        return pd.Series({'curve': npz.f.curve[1], 'meta': meta, 'stimMaps': npz.f.stimMaps})

    @classmethod
    def from_pickle(cls, path):
        p = pickle.load(open(path, 'rb'))
        return cls(p['df'], p['src'], p['data_column'])

    def to_pickle(self, path):
        d = {'df': self.df, 'src': self.src, 'data_column': self.data_column, 'dst': self.dst}
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

if __name__ == '__main__':
    configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
    configuration.openConfig()
    pick = pickle.load(open('../df_with_curves', 'rb'))
    # data = list(pick['curve'][0])
    t = Transmission.from_proj(pick)
    df = t.df
