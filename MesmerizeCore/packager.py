#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:08:09 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import sys

sys.path.append('..')
if __name__ == '__main__':
    from DataTypes import ImgData
    from FileInput import *
else:
    from .FileInput import *
    from .DataTypes import ImgData
import numpy as np
import pickle
import pandas as pd
import time
import tifffile
from PyQt5 import QtGui
from pyqtgraphCore import PolyLineROI
import os
from . import configuration


# class mesfile2workEnv():
#    def __init__(self,):
#        pass
#
# class tiff2workEnv():
#    def __init__(self,):
#        pass

class viewerWorkEnv():
    def __init__(self, imgdata=None, ROIList=[], CurvesList=[], roi_states=[]):
        """

        :type imgdata: ImgData
        """
        self.ROIList = ROIList
        self.CurvesList = CurvesList
        #        self.ROItags = []
        self.imgdata = imgdata
        self._saved = True
        self.roi_states = roi_states

    #    def __repr__(self):
    #        return 'viewerWorkEnv()\nROIlist: {}\nCurvesList: {}\nimgdata: +\
    #            {}\nmesfileMap: {}'.format(self.ROIlist, self.CurvesList, self.imgdata, self.mesfileMap)

    @classmethod
    def from_pickle(cls, pikPath, npzPath=None, tiffPath=None):
        pick = pickle.load(open(pikPath, 'rb'))
        if npzPath is not None:
            npz = np.load(npzPath)
            seq = npz['imgseq']
        elif tiffPath is not None:
            seq = tifffile.imread(tiffPath)
            seq = seq.T
        imdata = ImgData(seq,
                         pick['imdata']['meta'],
                         SampleID=pick['imdata']['SampleID'],
                         Genotype=pick['imdata']['Genotype'],
                         stimMaps=pick['imdata']['stimMaps'],
                         isSubArray=pick['imdata']['isSubArray'])
        roi_states = []
        if 'roi_states' in pick['imdata']:
            for roi_state in pick['imdata']['roi_states']:
                roi_states.append(roi_state)

        return cls(imdata, roi_states=roi_states)

    @property
    def saved(self):
        return bool(self._saved)

    @saved.setter
    def saved(self, state):
        self._saved = state

    @staticmethod
    def load_mesfile(path):
        return MES(path)

    @classmethod
    def from_mesfile(cls, mesfile, ref, mesfileMaps=None):
        rval, seq, meta = mesfile.load_img(ref)

        if rval:
            imdata = ImgData(seq, meta)
            imdata.stimMaps = (mesfileMaps, 'mesfile')

            return cls(imdata)

        else:
            return rval

    @classmethod
    def from_tiff(cls, path, csvMapPaths=None):
        seq = tifffile.imread(path)
        imdata = ImgData(seq.T)
        imdata.stimMaps = (csvMapPaths, 'csv')
        return cls(imdata)

    @classmethod
    def from_splits(cls):
        pass

    def _make_dict(self):

        d = {'SampleID': self.imgdata.SampleID, 'Genotype': self.imgdata.Genotype,
             'meta': self.imgdata.meta, 'stimMaps': self.imgdata.stimMaps,
             'isSubArray': self.imgdata.isSubArray, 'isMotCor': self.imgdata.isMotCor,
             'isDenoised': self.imgdata.isDenoised}

        for ix in range(0, len(self.ROIList)):
            for roi_def in self.ROIList[ix].tags.keys():
                if self.ROIList[ix].tags[roi_def] == '':
                    self.ROIList[ix].tags[roi_def] = 'untagged'

        roi_states = []
        for roi in self.ROIList:
            roi_states.append(roi.saveState())
        d['roi_states'] = roi_states

        #
        # if len(self.CurvesList) > 0:
        #     d['CurvesList'] = self.CurvesList

        return d

    def to_pickle(self, dirPath, mc_params=None):
        if mc_params is not None:
            rigid_params, elas_params = mc_params
        try:
            fileName = dirPath + '/' + self.imgdata.SampleID + '_' + str(time.time())

            imginfo = self._make_dict()

            if mc_params is not None:
                data = {'imdata': imginfo, 'rigid_params': rigid_params, 'elas_params': elas_params}
            else:
                data = {'imdata': imginfo}

            tifffile.imsave(fileName + '.tiff', self.imgdata.seq.T)
            pickle.dump(data, open(fileName + '.pik', 'wb'), protocol=4)

            self._saved = True

            return True, fileName

        except IOError:
            return False, None

    def to_pandas(self, projPath):
        imgdir = projPath + '/images'  # + self.imgdata.SampleID + '_' + str(time.time())
        rval, imgPath = self.to_pickle(imgdir)

        if rval == False:
            return False, None

        self._saved = False

        stimMapsSet = {}
        new_stims = []
        if self.imgdata.stimMaps is None:
            stimMapsSet = ['No_Stims']
        else:
            for stimMap in self.imgdata.stimMaps:
                stimList = []
                for stim in self.imgdata.stimMaps[stimMap]:
                    if stim is None:
                        stim = 'untagged'
                    stimList.append(stim[0][0])
                stimMapsSet[stimMap] = list(set(stimList))

                for key in configuration.cfg.options('STIM_DEFS'):
                    if key not in self.imgdata.stimMaps.keys():
                        stimMapsSet[key] = ['untagged']

                for stim in stimMapsSet[stimMap]:
                    if stim not in configuration.cfg['ALL_STIMS'].keys():
                        new_stims.append(stim)

        print(stimMapsSet)

        configuration.cfg['ALL_STIMS'] = {**configuration.cfg['ALL_STIMS'], **dict.fromkeys(new_stims)}
        configuration.saveConfig()

        if self.imgdata.meta is not None:
            try:
                date = str(self.imgdata.meta['MeasurementDate'])
            except KeyError:
                date = 'Unknown'

        curvesDir = projPath + '/curves/' + self.imgdata.SampleID

        if os.path.isdir(curvesDir) is False:
            os.mkdir(curvesDir)

        dicts = []
        for ix in range(0, len(self.CurvesList)):
            curvePath = curvesDir + '/CURVE_' + str(ix).zfill(3) + '.npz'

            np.savez(curvePath, curve=self.CurvesList[ix].getData(),
                     roi_state=self.ROIList[ix].saveState(), stimMaps=self.imgdata.stimMaps)

            d = {'SampleID': self.imgdata.SampleID,
                 'CurvePath': curvePath,
                 'ImgPath': imgPath + '.tiff',
                 'ImgInfoPath': imgPath + '.pik',
                 'Genotype': self.imgdata.Genotype}

            dicts.append({**d, **stimMapsSet, 'Date': date, **self.ROIList[ix].tags})

            # df = df.append({**d, **roitags})  # , ignore_index=True)

            # ------------------------------------------------------------------
            ### TODO: CANNOT ALLOW NaN's in the dataframe!! Huge pain in the ass.
        # ------------------------------------------------------------------
        print(dicts)
        self._saved = True
        return True, dicts


'''
This will be to take information from the Mesmerize Viewer work environment, such as
the current ImgData class object (See MesmerizeCore.DataTypes) and any paramteres such as
for motion correction and package them into a pickle & image seq array. Not yet implemented
in this module, it is currently done within the Mesmerize Viewer (modified pyqtgraph ImageView class)
but that class is getting clunky
'''


def workEnv2pickle():
    pass


'''
Get pickled image data from a pickle file (such as after motion correction) and
the corresponding npz array representing the image. Organize this info into an
ImgData class object (See MesmerizeCore.DataTypes)
#'''


# def pickle2workEnv(pikPath, npzPath):
#        pick = pickle.load(open(pikPath, 'rb'))
#        npz = np.load(npzPath)
#        imgdata = ImgData(npz['imgseq'], 
#                          pick['imdata']['meta'], 
#                          SampleID=pick['imdata']['SampleID'],
#                          Map=pick['imdata']['Map'], 
#                          isSubArray=pick['imdata']['isSubArray'])
#        return imgdata

# Empty pandas dataframe with columns that is used for the project index file

def empty_df(cols):
    """
    :rtype: pd.DataFrame
    """
    if type(cols) is list:
        cols = set(cols)
    return pd.DataFrame(data=None, columns=cols)  # type: pd.DataFrame


'''
Package the work environment into the organization of a pandas dataframe.
Used for example to add the current work environment (the image sequence, ROIs, and Calcium imaging
traces (curves)) to the project index which is a pandas dataframe
'''


def workEnv2pandas(df, projPath):
    if df is None:
        df = empty_df()

    # To save the image sequence array & metadata in the same folder as the project
    imgpath = projPath + '/images' + imgdata.SampleID + '_' + str(time.time())

    # Save image sequence
    imgPath = path + '_IMG' + '.tiff'
    tifffile.imsave(imgPath, self.imgdata.seq.T)

    # Organize metadata of the image & save as a pickle
    imgInfoPath = path + '_IMGINFO.pik'
    imgInfo = {'SampleID': imgdata.SampleID, 'meta': imgdata.meta,
               'Map': imgdata.Map, 'isSubArray': imgdata.isSubArray, 'isMotCor': imgdata.isMotCor,
               'isDenoised': imgdata.isDenoised}
    pickle.dump(imgInfo, open(imgInfoPath, 'wb'))

    # Get a set of all stimuli in this particular experiment
    stimList = []
    for stim in imgdata.Map:
        stimList.append(stim[0][0])
    setOfStimMap = list(set(stimList))

    # Add rows to pandas dataframe

    for ix in range(0, len(ROIList)):
        curvePath = path + '_CURVE_' + str(ix).zfill(3) + '.npy'
        np.save(curvePath, Curveslist[ix].getData())

        roitags = {}

        for key in ROItags[ix]:
            if ROItags[ix][key] == '':
                ROItags[ix][key] = 'Untagged'
            roitags['ROI_DEF:' + key] = ROItags[ix][key]

        #        ROItagsDf = pd.DataFrame(d, index=[0])

        d = {'CurvePath': curvePath,
             'ImgPath': imgPath,
             'ImgInfoPath': imgInfoPath,
             'SampleID': imgdata.SampleID,
             'Date': str(imgdata.meta['MeasurementDate']),
             'ROIhandles': 'N/A',
             'StimSet': setOfStimMap
             }

        df = df.append({**d, **roitags})  # , ignore_index=True)

        # ------------------------------------------------------------------
    ### TODO: CANNOT ALLOW NaN's in the dataframe!! Huge pain in the ass.
    # ------------------------------------------------------------------
    return df


'''
Does the reverse of workEnv2pandas
'''


def pandas2workEnv():
    pass


if __name__ == '__main__':
    #    imD = pickle2workEnv('/home/kushal/Sars_stuff/github-repos/MESmerize/bahproj/.batches/1516565957.0505505/1516565957.050627.pik',
    #                         '/home/kushal/Sars_stuff/github-repos/MESmerize/bahproj/.batches/1516565957.0505505/1516565957.050627_mc.npz')
    pass
