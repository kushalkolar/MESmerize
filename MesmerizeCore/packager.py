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
import os
from . import configuration


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
        '''
        Get pickled image data from a pickle file & image sequence from a npz or tiff. Used after motion correction
        & to view a sample from a project DataFrame. Create ImgData class object (See MesmerizeCore.DataTypes) and
        return instance of the work environment.

        :param: pikPath:    str of the full path to the pickle containing image metadata, stim maps, and roi_states

        :param: npzPath:    str of the full path to a npz containing the image sequence numpy array

        :param: tiffPath:   str of the full path to a tiff file containing the image sequence
        '''

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
            for ID in range(0, len(pick['imdata']['roi_states'])):
                roi_states.append(pick['imdata']['roi_states'][ID])

        return cls(imdata, roi_states=roi_states)

    @property
    def saved(self):
        return bool(self._saved)

    @saved.setter
    def saved(self, state):
        self._saved = state

    @staticmethod
    def load_mesfile(path):
        '''
        Just passes the path of a .mes file to the constructor of class MES in MesmerizeCore.FileInput.
        Loads .mes file & constructs MES obj from which individual images & their respective metadata can be loaded
        to construct viewer work environments using the classmethod viewerWorkEnv.from_mesfile.

        :param path: str of the full path to the .mes file.

        :return: MES object
        '''
        return MES(path)

    @classmethod
    def from_mesfile(cls, mesfile, ref, mesfileMaps=None):
        '''
        Return instance of work environment with MesmerizeCore.ImgData class object using seq returned from
        MES.load_img from MesmerizeCore.FileInput module and any stimulus map that the user may have specified.

        :param      mesfile:        MES obj, from MesmerizeCore.FileInput.

        :param      ref:            str of the reference of the image to load

        :param      mesfileMaps:    if there's a stimulus map that has been set by the user to load upon creation of the
                                    work environment.
        '''
        rval, seq, meta = mesfile.load_img(ref)

        if rval:
            imdata = ImgData(seq, meta)
            imdata.stimMaps = (mesfileMaps, 'mesfile')

            return cls(imdata)

        else:
            return rval

    @classmethod
    def from_tiff(cls, path, csvMapPaths=None):
        '''
        Return instance of work environment with MesmerizeCore.ImgData class object using seq returned from
        tifffile.imread and any csv stimulus map that the user may want to apply.

        :param path:        str of the full path to the tiff file

        :param csvMapPaths: list of full paths to csv files to load with the ImgData object into the work environment
        '''

        seq = tifffile.imread(path)
        imdata = ImgData(seq.T)
        imdata.stimMaps = (csvMapPaths, 'csv')
        return cls(imdata)

    @classmethod
    def from_splits(cls):
        pass

    def _make_dict(self):
        # Dict that's later used for pickling
        d = {'SampleID': self.imgdata.SampleID, 'Genotype': self.imgdata.Genotype,
             'meta': self.imgdata.meta, 'stimMaps': self.imgdata.stimMaps,
             'isSubArray': self.imgdata.isSubArray, 'isMotCor': self.imgdata.isMotCor,
             'isDenoised': self.imgdata.isDenoised}

        for ix in range(0, len(self.ROIList)):
            for roi_def in self.ROIList[ix].tags.keys():
                if self.ROIList[ix].tags[roi_def] == '':
                    self.ROIList[ix].tags[roi_def] = 'untagged'

            for roi_def in configuration.cfg.options('ROI_DEFS'):
                if roi_def not in self.ROIList[ix].tags.keys():
                    self.ROIList[ix].tags[roi_def] = 'untagged'

        roi_states = []
        for ID in range(0, len(self.ROIList)):
            roi_states.append(self.ROIList[ID].saveState())
        d['roi_states'] = roi_states

        return d

    def to_pickle(self, dirPath, mc_params=None, filename=None):
        '''
        Package the current work Env ImgData class object (See MesmerizeCore.DataTypes) and any paramteres such as
        for motion correction and package them into a pickle & image seq array. Use for batch motion correction and
        for saving current sample to the project. Image sequence is saved as a tiff and other information about the
        image is saved in a pickle.

        :rtype:     bool, str
        :param      dirPath: str
        :param      mc_params: dict
        :return:    bool if no exceptions, str of filename
        '''
        if mc_params is not None:
            rigid_params, elas_params = mc_params
        try:
            if filename is None:
                fileName = dirPath + '/' + self.imgdata.SampleID + '_' + str(time.time())
            else:
                fileName = dirPath + '/' + filename

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
        '''
        :param      projPath: Root path of the current project

        :return:    True if no exceptions, list of dicts that each correspond to a single curve that can be appended
                    as a row to the project dataframe
        '''
        # Path where image (as tiff file) and image metadata, roi_states, and stimulus maps (in a pickle) are stored
        imgdir = projPath + '/images'  # + self.imgdata.SampleID + '_' + str(time.time())
        rval, imgPath = self.to_pickle(imgdir)

        # Check if the img saving and pickling worked
        if rval == False:
            return False, None

        # Since viewerWorkEnv.to_pickle sets the saved property to True, and we're not done saving the dict yet.
        self._saved = False

        # Create a dict that contains all stim definitions as keys that refer to a list of all the stims for that sample
        stimMapsSet = {}
        # This list is just used for gathering all new stims to add to the config file. This is just used for
        # populating the comboBoxes in the stimMapWidget GUI so that the widget doesn't need to access the DataFrame
        # for this simple task.
        new_stims = []
        if self.imgdata.stimMaps is None:
            for stim_def in configuration.cfg.options('STIM_DEFS'):
                stimMapsSet[stim_def] = ['untagged']
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

            # Final list of dicts that are each appended as rows to the project DataFrame
            dicts.append({**d, **stimMapsSet, 'Date': date, **self.ROIList[ix].tags})

            # df = df.append({**d, **roitags})  # , ignore_index=True)

            # ------------------------------------------------------------------
            ### TODO: CANNOT ALLOW NaN's in the dataframe!! Huge pain in the ass.
        # ------------------------------------------------------------------
        print(dicts)
        self._saved = True
        return True, dicts

def empty_df(cols):
    """
    Just returns an empty DataFrame based on columns in the project's config.cfg file. Only really used when a new
    project is started.

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
