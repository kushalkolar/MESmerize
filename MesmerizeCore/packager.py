#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun Jan 21 17:12:37 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

For packaging the work environment for export, and importing saved work environments. For now
it is used after motion correction (see the method pickle2workEnv) to get the motion corrected image sequence and open that
on the Mesmerize Viewer so that ROIs can be drawn and the data saved (see the method workEnv2pandas).
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
                                            'Location', 'SubcellLocation','NucLocation', 
                                            'StimSet'})

'''
Package the work environment into the organization of a pandas dataframe.
Used for example to add the current work environment (the image sequence, ROIs, and Calcium imaging
traces (curves)) to the project index which is a pandas dataframe
'''
def workEnv2pandas(df, projPath, imgdata, ROIlist, Curveslist):
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
    setOfStimMap = set(stimList)    
    
    # Add rows to pandas dataframe

    for ix in range(0,len(ROIlist)):
        curvePath = path + '_CURVE_' + str(ix).zfill(3) + '.npy'
        np.save(curvePath, Curveslist[ix].getData())
    #------------------------------------------------------------------
### TODO: CANNOT ALLOW NaN's in the dataframe!! Huge pain in the ass.
    #------------------------------------------------------------------
        df = df.append({'CurvePath': curvePath,
                        'ImgPath': imgPath,
                        'ImgInfoPath': imgInfoPath,
                        'SampleID': imgdata.SampleID,
                        'Date': imgdata.meta['MeasurementDate'],
                        'ROIhandles': 'N/A',
                        'Location': 'N/A',
                        'SubcellLocation': 'N/A',
                        'NucLocation': 'N/A',
                        'StimSet': setOfStimMap
                        }, ignore_index=True)
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