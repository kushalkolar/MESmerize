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
from MesmerizeCore.misc_funcs import empty_df

class Transmission:
    def __init__(self, df, src, dst=None, STIM_DEFS=None, ROI_DEFS=None, weakref=False):
        """
        :param df: DataFrame
        :type df: pd.DataFrame
        :param src: History of the nodes & node parameters the transmission has been processed through
        :type src: dict
        :param dst:
        :param STIM_DEFS: STIM_DEF columns, used by the AlignStims control node for example
        :type STIM_DEFS: list
        :param ROI_DEFS: ROI_DEF columns, used by the ROI selection control node for example
        :type ROI_DEFS: list
        """
        self.df = df
        assert isinstance(self.df, pd.DataFrame)
        # TODO: Make a graphical thing that display the source history of any node and can be accessed while looking at stastics too

        self.src = src

        self.STIM_DEFS = STIM_DEFS
        self.ROI_DEFS = ROI_DEFS

        self.dst = dst

    @classmethod
    def from_proj(cls, dataframe, df_name='', weakref=False):
        """
        :param df: Chosen Child DataFrame from the Mesmerize Project
        :return: Transmission class object
        """
        df = dataframe.copy()
        assert isinstance(df, pd.DataFrame)
        df[['curve', 'meta', 'stimMaps']] = df.apply(Transmission._load_files, axis=1)

        from MesmerizeCore import configuration
        stim_defs = configuration.cfg.options('STIM_DEFS')
        roi_defs = configuration.cfg.options('ROI_DEFS')

        return cls(df, src=[{'raw': df_name}], STIM_DEFS=stim_defs, ROI_DEFS=roi_defs, weakref=weakref)

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
        p = pickle.load(open(path, 'rb'))
        return cls(p['df'],
                   p['src'],
                   p['dst'],
                   p['STIM_DEFS'],
                   p['ROI_DEFS'])

    def _make_dict(self):
        d = {'df': self.df,
             'src': self.src,
             'dst': self.dst,
             'STIM_DEFS': self.STIM_DEFS,
             'ROI_DEFS': self.ROI_DEFS
             }

        return d

    def to_pickle(self, path):
        """
        :param path: Path of where to store pickle
        """
        pickle.dump(self._make_dict(), open(path, 'wb'), protocol=4)


    def copy(self):
        return deepcopy(self)

    @classmethod
    def empty_df(cls, transmission, addCols=[]):
        """
        :rtype: pd.DataFrame
        """
        c = list(transmission.df.columns)
        e_df = empty_df(cols=c, addCols=addCols)
        return cls(e_df, src=transmission.src, dst=transmission.dst,
                   STIM_DEFS=transmission.STIM_DEFS, ROI_DEFS=transmission.ROI_DEFS)


class GroupTranmission:
    def __init__(self, df, src, groups_list):
        """
        :param df: DataFrame
        :type df: pd.DataFrame
        :param src: History of the nodes & node parameters the transmission has been processed through
        :type src: dict
        :type: groups_list: list
        """
        self.df = df
        assert isinstance(self.df, pd.DataFrame)
        self.src = src
        self.groups_list = groups_list

    @classmethod
    def from_ca_data(cls, transmission, groups_list):
        if not (
            any('Peak_Features' in d for d in transmission.src) or any('AlignStims' in d for d in transmission.src)):
            raise IndexError('No Peak Features or Stimulus Alignment data to group the data.')

        if any('Peak_Features' in d for d in transmission.src):
            df = GroupTranmission._organize_peak_features(transmission.df)

        else:
            df = transmission.df

        transmission.src.append({'Grouped': ', '.join(groups_list)})

        return cls(df, transmission.src, groups_list)

    @staticmethod
    def _organize_peak_features(df):
        g_df = df['peaks_bases'].apply(lambda x: GroupTranmission._remove_empty_features(x[0]))
        g_df = g_df.values.flatten()
        g_df = pd.concat(g_df)
        g_df = g_df.reset_index(drop=True)
        return g_df

    @staticmethod
    def _remove_empty_features(df):
        df = df[df['features'] != {}]
        df = df['features']
        return df

    @classmethod
    def from_behav_data(cls, transmission, groups_list):
        pass

    @classmethod
    def from_pickle(cls, path):
        p = pickle.load(open(path, 'rb'))
        return cls(p['df'],
                   p['src'],
                   p['groups_list'])

    def _make_dict(self):
        d = {'df': self.df,
             'src': self.src,
             'groups_list': self.groups_list
             }
        return d

    def to_pickle(self, path):
        pickle.dump(self._make_dict(), open(path, 'wb'), protocol=4)

    def copy(self):
        return deepcopy(self)

    @staticmethod
    def merge(group_trans_list):
        """
        :param group_trans_list list of GroupTransmission objects
        :type group_trans_list: list
        """
        all_groups = []
        for trans in group_trans_list:
            assert isinstance(trans, GroupTranmission)
            all_groups += trans.groups_list

        all_df = []

        for trans in group_trans_list:
            assert isinstance(trans, GroupTranmission)
            for group in all_groups:
                if group in trans.groups_list:
                    trans.df[group] = True
                else:
                    trans.df[group] = False

            all_df.append(trans.df)

        df = pd.concat(all_df)
        return df
