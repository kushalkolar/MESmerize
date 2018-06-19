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
    from mesfile import *
else:
    from .mesfile import *
    from .DataTypes import ImgData
import numpy as np
import pickle
import time
import tifffile
import os
from common import configuration
from uuid import uuid4
import json


class ViewerWorkEnv:
    def __init__(self, imgdata=None, sample_id='', ROIList=[], CurvesList=[], roi_states=[], comments='', origin_file='', custom_columns_dict={}):
        """
        A class that encapsulates the main work environment objects (img sequence, ROIs, and ROI associated curves) of
        the viewer. Allows for a work environment to be easily spawned from different types of sources and allows for
        a work environment to be easily saved in different ways regardless of the type of original data source.

        :param ROIList:     list of ROIs in current work environment
        :param CurvesList:  list of curves in current work environment
        :param roi_states:  list of ROI states, from pyqtgraphCore.ROI.saveState()

        :type imgdata:      ImgData
        :type ROIList:      list
        :type CurvesList:   list
        :type roi_states:   list

        """
        if imgdata is not None:
            self.isEmpty = False
        else:
            self.isEmpty = True

        self.sample_id = sample_id

        self.ROIList = ROIList
        self.CurvesList = CurvesList
        #        self.ROItags = []
        self.imgdata = imgdata
        self._saved = True
        self.roi_states = roi_states
        self.comments = comments
        self.origin_file = origin_file
        self.custom_columns_dict = custom_columns_dict
    #    def __repr__(self):
    #        return 'viewerWorkEnv()\nROIlist: {}\nCurvesList: {}\nimgdata: +\
    #            {}\nmesfileMap: {}'.format(self.ROIlist, self.CurvesList, self.imgdata, self.mesfileMap)

    def dump(self):
        self.isEmpty = True
        del self.imgdata.seq
        self.imgdata = None
        self.ROIList = []
        self.CurvesList = []
        self.roi_states = []
        self.comments = ''
        self.origin_file = ''
        self._saved = True
        print('Work environment dumped!')

    @classmethod
    def from_pickle(cls, pikPath, npzPath=None, tiffPath=None):
        """
        Get pickled image data from a pickle file & image sequence from a npz or tiff. Used after motion correction
        & to view a sample from a project DataFrame. Create ImgData class object (See MesmerizeCore.DataTypes) and
        return instance of the work environment.

        :param: pikPath:    full path to the pickle containing image metadata, stim maps, and roi_states
        :type   pikPath:    str

        :param: npzPath:    full path to a npz containing the image sequence numpy array
        :type:  npzPath:    str

        :param: tiffPath:   str of the full path to a tiff file containing the image sequence
        :type:  tiffPath:   str
        """

        # if (npzPath is None) and (tifffile is None):
        #     raise ValueError('You must pass a path to either a npz or tiff image sequence.')
        if npzPath is not None:
            npz = np.load(npzPath)
            seq = npz['imgseq']
        elif tiffPath is not None:
            seq = tifffile.imread(tiffPath)
            seq = seq.T
        else:
            seq = None

        p = pickle.load(open(pikPath, 'rb'))

        sample_id = p['imdata']['sample_id']

        imdata = ImgData(seq,
                         p['imdata']['meta'],
                         stimMaps=p['imdata']['stimMaps'],
                         )

        comments = p['imdata']['comments']

        roi_states = []
        if 'roi_states' in p['imdata']:
            for ID in range(0, len(p['imdata']['roi_states'])):
                roi_states.append(p['imdata']['roi_states'][ID])

        return cls(imdata, roi_states=roi_states, comments=comments, sample_id=sample_id)

    @property
    def saved(self):
        return bool(self._saved)

    @saved.setter
    def saved(self, state):
        self._saved = state

    @staticmethod
    def load_mesfile(path):
        """
        Just passes the path of a .mes file to the constructor of class MES in MesmerizeCore.FileInput.
        Loads .mes file & constructs MES obj from which individual images & their respective metadata can be loaded
        to construct viewer work environments using the classmethod viewerWorkEnv.from_mesfile.

        :param path: full path to a single .mes file.
        :type path:  str

        :return:     MesmerizeCore.FileInput.MES type object
        :rtype:      MES
        """
        return MES(path)

    @staticmethod
    def _organize_meta(meta, origin):
        if origin == 'mes':
            fps = float(1000/meta['FoldedFrameInfo']['frameTimeLength'])

            date_meta = meta['MeasurementDate'].split('.')
            ymd = date_meta[0] + date_meta[1] + date_meta[2]
            hms_ = date_meta[3].split(':')
            hms = hms_[0].split(' ')[1] + hms_[1] + hms_[2][:2]
            date = ymd + '_' + hms

            vmin = meta['LUTstruct']['lower']
            vmax = meta['LUTstruct']['upper']

            meta_d = {'origin':    origin,
                      'fps':       fps,
                      'date':      date,
                      'vmin':      vmin,
                      'vmax':      vmax,
                      'orig_meta': meta}

            return meta_d

        elif origin == 'AwesomeImager' or origin == 'DeepEyes':
            meta_d = {'origin':     origin,
                      'version':    meta['version'],
                      'fps':        meta['framerate'],
                      'date':       meta['date'] + '_' + meta['time'],
                      'vmin':       meta['level_min'],
                      'vmax':       meta['level_max'],
                      'orig_meta':  meta}
            return meta_d

        else:
            raise ValueError('Unrecognized meta data source.')

    @classmethod
    def from_mesfile(cls, mesfile, ref, mesfileMaps=None):
        """
        Return instance of work environment with MesmerizeCore.ImgData class object using seq returned from
        MES.load_img from MesmerizeCore.FileInput module and any stimulus map that the user may have specified.

        :param      mesfile:        MesmerizeCore.FileInput.MES object
        :type       mesfile:        MES
        :param      ref:            reference of the image to load
        :type       ref:            str
        :param      mesfileMaps:    if there's a stimulus map that has been set by the user to load upon creation of the
                                    work environment.
        :type       mesfileMaps:    dict
        """
        assert isinstance(mesfile, MES)
        imgseq, raw_meta = mesfile.load_img(ref)

        meta_data = ViewerWorkEnv._organize_meta(raw_meta, 'mes')
        imdata = ImgData(imgseq, meta_data)
        imdata.stimMaps = (mesfileMaps, 'mesfile')

        return cls(imdata)

    @classmethod
    def from_tiff(cls, path, method, meta_path='', csvMapPaths=None):
        """
        Return instance of work environment with MesmerizeCore.ImgData class object using seq returned from
        tifffile.imread and any csv stimulus map that the user may want to apply.

        :param path:        full path to a single tiff file
        :type path:         str
        :param csvMapPaths: full paths to csv files to load with the ImgData object into the work environment
        :type csvMapPaths:  list
        """

        if method == 'imread':
            seq = tifffile.imread(path)
        elif method == 'asarray':
            tif = tifffile.TiffFile(path, is_nih=True)
            seq = tif.asarray(key=range(0, len(tif.series)),
                              maxworkers=int(configuration.sys_cfg['HARDWARE']['n_processes']))
        else:
            raise ValueError("Must specify 'imread' or 'asarray' in method argument")

        if meta_path.endswith('.json'):
            jmd = json.load(open(meta_path, 'r'))
            if 'source' not in jmd.keys():
                raise KeyError('Invalid meta data file. Json meta data file must have a "source" entry.')
            else:
                meta = ViewerWorkEnv._organize_meta(meta=jmd, origin=jmd['source'])
        else:
            meta = None

        imdata = ImgData(seq.T, meta)
        imdata.stimMaps = (csvMapPaths, 'csv')
        return cls(imdata)

    @classmethod
    def from_splits(cls):
        pass

    def _make_dict(self):
        # Dict that's later used for pickling
        d = {'sample_id':    self.sample_id,
             'meta':        self.imgdata.meta,
             'stimMaps':    self.imgdata.stimMaps,
             'comments':    self.comments
             }

        for ix in range(0, len(self.ROIList)):
            for roi_def in self.ROIList[ix].tags.keys():
                if self.ROIList[ix].tags[roi_def] == '':
                    self.ROIList[ix].tags[roi_def] = 'untagged'

            for roi_def in configuration.proj_cfg.options('ROI_DEFS'):
                if roi_def not in self.ROIList[ix].tags.keys():
                    self.ROIList[ix].tags[roi_def] = 'untagged'

        roi_states = []
        for ID in range(0, len(self.ROIList)):
            roi_states.append(self.ROIList[ID].saveState())
        d['roi_states'] = roi_states

        return d

    def to_pickle(self, dirPath, filename=None, save_img_seq=True):
        """
        Package the current work Env ImgData class object (See MesmerizeCore.DataTypes) and any paramteres such as
        for motion correction and package them into a pickle & image seq array. Used for batch motion correction and
        for saving current sample to the project. Image sequence is saved as a tiff and other information about the
        image is saved in a pickle.

        :param      dirPath: directory in which to save tiff and pik file
        :type       dirPath: str

        :param      mc_params: motion correction parameters if any
        :type       mc_params: dict

        :return:    str of filename
        :rtype:     str
        """
        if self.isEmpty:
            print('Work environment is empty!')
            return

        if filename is None:
            fileName = dirPath + '/' + self.sample_id + '_' + str(time.time())
        else:
            fileName = dirPath + '/' + filename

        imginfo = self._make_dict()

        data = {'imdata': imginfo}
        if save_img_seq:
            tifffile.imsave(fileName + '.tiff', self.imgdata.seq.T, bigtiff=True)
        pickle.dump(data, open(fileName + '.pik', 'wb'), protocol=4)

        self.saved = True

        return fileName

    def to_pandas(self, proj_path):
        """
        :param      proj_path: Root path of the current project
        :type       proj_path: str
        :return:    list of dicts that each correspond to a single curve that can be appended
                    as rows to the project dataframe
        :rtype:     list
        """
        if self.isEmpty:
            print('Work environment is empty!')
            return

        # Path where image (as tiff file) and image metadata, roi_states, and stimulus maps (in a pickle) are stored
        imgdir = proj_path + '/images'  # + self.imgdata.SampleID + '_' + str(time.time())

        imgPath = self.to_pickle(imgdir)

        # Since viewerWorkEnv.to_pickle sets the saved property to True, and we're not done saving the dict yet.
        self._saved = False

        # Create a dict that contains all stim definitions as keys that refer to a list of all the stims for that sample
        stimMapsSet = {}
        # This list is just used for gathering all new stims to add to the config file. This is just used for
        # populating the comboBoxes in the stimMapWidget GUI so that the widget doesn't need to access the DataFrame
        # for this simple task.
        new_stims = []
        if self.imgdata.stimMaps is None:
            for stim_def in configuration.proj_cfg.options('STIM_DEFS'):
                stimMapsSet[stim_def] = ['untagged']
        else:
            for stimMap in self.imgdata.stimMaps:
                stimList = []
                for stim in self.imgdata.stimMaps[stimMap]:
                    if stim is None:
                        stim = 'untagged'
                    stimList.append(stim[0][0])
                stimMapsSet[stimMap] = list(set(stimList))

                for key in configuration.proj_cfg.options('STIM_DEFS'):
                    if key not in self.imgdata.stimMaps.keys():
                        stimMapsSet[key] = ['untagged']

                for stim in stimMapsSet[stimMap]:
                    if stim not in configuration.proj_cfg['ALL_STIMS'].keys():
                        new_stims.append(stim)

        # print(stimMapsSet)

        configuration.proj_cfg['ALL_STIMS'] = {**configuration.proj_cfg['ALL_STIMS'], **dict.fromkeys(new_stims)}
        configuration.save_proj_config()

        if self.imgdata.meta is not None:
            try:
                date = str(self.imgdata.meta['date'])
            except KeyError:
                date = 'Unknown'
        else:
            date = 'Unknown'

        if self.comments is None or self.comments == '':
            comments = 'untagged'
        else:
            comments = self.comments

        curvesDir = proj_path + '/curves/' + self.sample_id

        if os.path.isdir(curvesDir) is False:
            os.mkdir(curvesDir)

        dicts = []
        for ix in range(0, len(self.CurvesList)):
            curvePath = curvesDir + '/CURVE_' + str(ix).zfill(3) + '.npz'

            if isinstance(self.CurvesList[ix], np.ndarray):
                curve = self.CurvesList[ix]
            else:
                curve = self.CurvesList[ix].getData()

            np.savez(curvePath, curve=curve,
                     roi_state=self.ROIList[ix].saveState(), stimMaps=self.imgdata.stimMaps)

            d = {'SampleID':    self.sample_id,
                 'CurvePath':   curvePath.split(proj_path)[1],
                 'ImgPath':     imgPath.split(proj_path)[1] + '.tiff',
                 'ImgInfoPath': imgPath.split(proj_path)[1] + '.pik',
                 }

            # Final list of dicts that are each appended as rows to the project DataFrame
            dicts.append({**d,
                          **self.custom_columns_dict,
                          **stimMapsSet,
                          **self.ROIList[ix].tags,
                          'Date':       date,
                          'uuid_curve': uuid4(),
                          'comments':   comments
                          })

        self.saved = True
        return dicts
