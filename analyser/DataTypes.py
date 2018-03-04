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
from collections import OrderedDict


class Transmission:
    def __init__(self, df, src, data_column, dst=None, STIM_DEFS=None, ROI_DEFS=None, plot_this=None):
        """
        :param df: DataFrame
        :type df: pd.DataFrame
        :param src: History of the nodes & node parameters the transmission has been processed through
        :type src: dict
        :param data_column: Data column of interest by process methods of nodes.
        :type data_column: dict
        :param dst:
        :param STIM_DEFS: STIM_DEF columns, used by the AlignStims control node for example
        :type STIM_DEFS: list
        :param ROI_DEFS: ROI_DEF columns, used by the ROI selection control node for example
        :type ROI_DEFS: list
        :param plot_this: Data column which should be plotted by plot widgets
        :type plot_this: str
        """
        self.df = df.copy()
        assert isinstance(self.df, pd.DataFrame)
        # TODO: Make a graphical thing that display the source history of any node and can be accessed while looking at stastics too
        self.data_column = data_column
        
        if plot_this is None:
            self.plot_this = self.data_column
        else:
            self.plot_this = plot_this
            
        self.src = src
        
        self.STIM_DEFS = STIM_DEFS
        self.ROI_DEFS = ROI_DEFS
        
        self.dst = dst

    @classmethod
    def from_proj(cls, df):
        """
        :param df: Chosen Child DataFrame from the Mesmerize Project
        :return: Transmission class object
        """
        assert isinstance(df, pd.DataFrame)
        df[['curve', 'meta', 'stimMaps']] = df.apply(Transmission._load_files, axis=1)
        
        from MesmerizeCore import configuration
        stim_defs = configuration.cfg.options('STIM_DEFS')
        roi_defs = configuration.cfg.options('ROI_DEFS')

        return cls(df, src=[{'raw': ''}], data_column={'curve': 'curve'}, STIM_DEFS=stim_defs, ROI_DEFS=roi_defs)
    
    @staticmethod
    def _load_files(row):
        """Loads npz and pickle files of Curves & Img metadata according to the paths specified in each row of the
        chosen child DataFrame in the project"""

        path = row['CurvePath']
        npz = np.load(path)

        pikPath = row['ImgInfoPath']
        pik = pickle.load(open(pikPath, 'rb'))
        meta = pik['imdata']['meta']

        return pd.Series({'curve': npz.f.curve[1], 'meta': meta, 'stimMaps': npz.f.stimMaps})

    @classmethod
    def from_pickle(cls, path):
        """
        :param path: Path to the pickle file
        :return: Transmission class object
        """
        try:
            p = pickle.load(open(path, 'rb'))
            return True, cls(p['df'],
                             p['src'],
                             p['data_column'],
                             p['dst'],
                             p['STIM_DEFS'],
                             p['ROI_DEFS'],
                             p['plot_this'])

        except Exception as e:
            return False, e

    def _make_dict(self):
        d = {'df': self.df,
             'src': self.src,
             'data_column': self.data_column,
             'dst': self.dst,
             'STIM_DEFS': self.STIM_DEFS,
             'ROI_DEFS': self.ROI_DEFS,
             'plot_this': self.plot_this}

        return d

    def to_pickle(self, path):
        """
        :param path: Path of where to store pickle
        """
        try:
            pickle.dump(self._make_dict(), open(path, 'wb'), protocol=4)
            return True, None
        except Exception as e:
            return False, e

    def copy(self):
        return deepcopy(self)

        # @property
        # def src(self):
        #     return self._src
        #
        # @src.setter
        # def src(self, source):
        #     self._src = source + '_' + uuid4().hex

# if __name__ == '__main__':
#    from MesmerizeCore import configuration
#    configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
#    configuration.openConfig()
#    pick = pickle.load(open('../df_with_curves', 'rb'))
#    # data = list(pick['curve'][0])
#    t = Transmission.from_proj(pick)
#    df = t.df
