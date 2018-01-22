#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 17:12:37 2018

@author: kushal
"""

if __name__ == '__main__':
    from DataTypes import ImgData
else:
    from .DataTypes import ImgData
import numpy as np
import pickle
import pandas as pd
import time
import tifffile

#class mesfile2workEnv():
#    def __init__(self,):
#        pass
#
#class tiff2workEnv():
#    def __init__(self,):
#        pass

def workEnv2pickle():
    pass
    
def pickle2workEnv(pikPath, npzPath):
        pick = pickle.load(open(pikPath, 'rb'))
        npz = np.load(npzPath)
        imgdata = ImgData(npz['imgseq'], 
                          pick['imdata']['meta'], 
                          AnimalID=pick['imdata']['AnimalID'],
                          TrialID=pick['imdata']['TrialID'],
                          Map=pick['imdata']['Map'], 
                          isSubArray=pick['imdata']['isSubArray'])
        return imgdata

def empty_df():
    return pd.DataFrame(data=None, columns={'CurvePath', 'ImgPath', 'ImgInfoPath', 
                                            'AnimalID', 'TrialID', 'Date', 'ROIhandles', 
                                            'Location', 'SubcellLocation','NucLocation', 
                                            'StimSet'})

def workEnv2pandas(df, projPath, imgdata, ROIlist, Curveslist):
    if df is None:
        df = empty_df()
    else:
        df = df
    path = projPath + '/' + imgdata.AnimalID + '_' + imgdata.TrialID + '_' + str(time.time())
    imgPath = path + '_IMG' + '.tiff'
    tifffile.imsave(imgPath, imgdata.seq.T)
    
    imgInfoPath = path + '_IMGINFO.pik'
    imgInfo = {'AnimalID': imgdata.AnimalID, 'TrialID': imgdata.TrialID, 'meta': imgdata.meta, 
              'Map': imgdata.Map, 'isSubArray': imgdata.isSubArray, 'isMotCor': imgdata.isMotCor,
              'isDenoised': imgdata.isDenoised}
    
    pickle.dump(imgInfo, open(imgInfoPath, 'wb'))
    stimList = []
    for stim in imgdata.Map:
        stimList.append(stim[0][0])
    setOfStimMap = set(stimList)    
    
    for ix in range(0,len(ROIlist)):
        curvePath = path + '_CURVE_' + str(ix).zfill(3) + '.npy'
        np.save(curvePath, Curveslist[ix].getData())
        df = df.append({'CurvePath': curvePath,
                        'ImgPath': imgPath,
                        'ImgInfoPath': imgInfoPath,
                        'AnimalID': imgdata.AnimalID,
                        'TrialID': imgdata.TrialID,
                        'Date': imgdata.meta['MeasurementDate'],
                        'ROIhandles': None,
                        'Location': None,
                        'SubcellLocation': None,
                        'NucLocation': None,
                        'StimSet': setOfStimMap
                        }, ignore_index=True)
    return df

def pandas2workEnv():
    pass

if __name__ == '__main__':
#    imD = pickle2workEnv('/home/kushal/Sars_stuff/github-repos/MESmerize/bahproj/.batches/1516565957.0505505/1516565957.050627.pik',
#                         '/home/kushal/Sars_stuff/github-repos/MESmerize/bahproj/.batches/1516565957.0505505/1516565957.050627_mc.npz')
    pass