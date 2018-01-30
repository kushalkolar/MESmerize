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
from pyqtgraphCore.graphicsItems import ROI

#class mesfile2workEnv():
#    def __init__(self,):
#        pass
#
#class tiff2workEnv():
#    def __init__(self,):
#        pass

class viewerWorkEnv():
    def __init__(self, imgdata=None, ROIList=[], CurvesList=[], stimMap=None):
        self.ROIlist = ROIList
        self.CurvesList = CurvesList
#        self.ROItags = []
        self.imgdata = imgdata
        if stimMap is not None:
            self.setStimMap_from_mes(stimMap)
        
            
#    def __repr__(self):
#        return 'viewerWorkEnv()\nROIlist: {}\nCurvesList: {}\nimgdata: +\
#            {}\nmesfileMap: {}'.format(self.ROIlist, self.CurvesList, self.imgdata, self.mesfileMap)

    @classmethod
    def from_pickle(cls, pikPath, npzPath):
        pick = pickle.load(open(pikPath, 'rb'))
        npz = np.load(npzPath)
        imdata = ImgData(npz['imgseq'], 
                          pick['imdata']['meta'], 
                          SampleID=pick['imdata']['SampleID'],
                          Map=pick['imdata']['Map'], 
                          isSubArray=pick['imdata']['isSubArray'])
        return cls(imdata)
    
    @staticmethod
    def load_mesfile(path):
        return MES(path)
    
    @classmethod
    def from_mesObj(cls, mesfile, ref, mesfileMap=None):
        rval, imdata = mesfile.load_img(ref)
        if rval:
            return True, cls(imdata, mesfileMap)
        else:
            return False, None
    
    @classmethod
    def from_tiff(cls, path):
        seq = tifffile.imread(path)
        imdata = ImgData(seq)
        return cls(imdata)
    
    @classmethod
    def from_project(imgPath, infoPath, curvesPath):
        seq = tifffile.imread(imgPath)
        meta = infoPath
        
    @classmethod
    def from_split():
        pass
    
    ''' USE THIS TO SET THE STIM-MAP INSTEAD '''
    @property
    def stimMap(self,dm):
        pass
#        if dm is None:
#            dm = self.workEnv.mesfileMap
#        y = self.imgdata.meta['AUXo3']['y']
#        x = self.imgdata.meta['AUXo3']['x'][1]
#        firstFrameStartTime = self.imgdata.meta['FoldedFrameInfo']['firstFrameStartTime']
#        frameTimeLength = self.imgdata.meta['FoldedFrameInfo']['frameTimeLength']
#        self.imgdata.Map = []
#        for i in range(0,y.shape[1]-1):
#            voltage = str(y[1][i])
#            tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)
#            if tstart_frame < 0:
#                tstart_frame = 0
#            tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)
#            self.imgdata.Map.append([dm[voltage], (tstart_frame, tend_frame)])
    
    def setStimMap_from_standard():
        pass
    
    # Takes mesfile maps dicts returned from the StimMapWidget GUI
    def setStimMap_from_mes(self,dm):
        y = self.imgdata.meta['AUXo3']['y']
        x = self.imgdata.meta['AUXo3']['x'][1]
        firstFrameStartTime = self.imgdata.meta['FoldedFrameInfo']['firstFrameStartTime']
        frameTimeLength = self.imgdata.meta['FoldedFrameInfo']['frameTimeLength']
        self.imgdata.Map = []
        for i in range(0,y.shape[1]-1):
            voltage = str(y[1][i])
            tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)
            if tstart_frame < 0:
                tstart_frame = 0
            tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)
            self.imgdata.Map.append([dm[voltage], (tstart_frame, tend_frame)])
            
    def setStimMap_from_csv(self,csv):
        pass
    
    def to_pickle(self, dirPath, mc_params=None):
        rigid_params, elas_params = mc_params
        
        try:
            fileName = dirPath + '/' + SampleID + '_' + str(time.time())
            
            imginfo = {'SampleID': self.imgdata.SampleID, 'meta': self.imgdata.meta, 
                      'Map': self.imgdata.Map, 'isSubArray': self.imgdata.isSubArray, 
                      'isMotCor': self.imgdata.isMotCor,'isDenoised': self.imgdata.isDenoised}
            
            data = {'imdata': imginfo, 'rigid_params': rigid_params, 'elas_params': elas_params}
            
            tifffile.imsave(fileName+'.tiff', self.imgdata.seq.T)
            pickle.dump(data, open(fileName+'.pik', 'wb'))
            
            return True, fileName
        except IOError:
            return False, None
    
    def to_pandas():
        pass
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
'''
def pickle2workEnv(pikPath, npzPath):
        pick = pickle.load(open(pikPath, 'rb'))
        npz = np.load(npzPath)
        imgdata = ImgData(npz['imgseq'], 
                          pick['imdata']['meta'], 
                          SampleID=pick['imdata']['SampleID'],
                          Map=pick['imdata']['Map'], 
                          isSubArray=pick['imdata']['isSubArray'])
        return imgdata

# Empty pandas dataframe with columns that is used for the project index file
def empty_df():
    return pd.DataFrame(data=None, columns={'CurvePath', 'ImgPath', 'ImgInfoPath', 
                                            'SampleID', 'Date', 'ROIhandles', 
                                            'ROI_DEF:Location', 'ROI_DEF:SubcellLocation','ROI_DEF:NucLocation', 
                                            'StimSet'})

'''
Package the work environment into the organization of a pandas dataframe.
Used for example to add the current work environment (the image sequence, ROIs, and Calcium imaging
traces (curves)) to the project index which is a pandas dataframe
'''
def workEnv2pandas(df, projPath, imgdata, ROIlist, ROItags, Curveslist):
    if df is None:
        df = empty_df()
    
    # To save the image sequence array & metadata in the same folder as a the project
    path = projPath + '/' + imgdata.SampleID + '_' + str(time.time())
    
    # Save image sequence
    imgPath = path + '_IMG' + '.tiff'
    tifffile.imsave(imgPath, imgdata.seq.T)
    
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

    for ix in range(0,len(ROIlist)):
        curvePath = path + '_CURVE_' + str(ix).zfill(3) + '.npy'
        np.save(curvePath, Curveslist[ix].getData())
        
        roitags = {}
        
        for key in ROItags[ix]:
            if ROItags[ix][key] == '':
                ROItags[ix][key] = 'Untagged'
            roitags['ROI_DEF:'+key] = ROItags[ix][key]
            
#        ROItagsDf = pd.DataFrame(d, index=[0])
            
        d = {'CurvePath': curvePath,
               'ImgPath': imgPath,
               'ImgInfoPath': imgInfoPath,
               'SampleID': imgdata.SampleID,
               'Date': str(imgdata.meta['MeasurementDate']),
               'ROIhandles': 'N/A',
               'StimSet': setOfStimMap
               }
        
        df = df.append({**d, **roitags})#, ignore_index=True)

    #------------------------------------------------------------------
### TODO: CANNOT ALLOW NaN's in the dataframe!! Huge pain in the ass.
    #------------------------------------------------------------------        
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