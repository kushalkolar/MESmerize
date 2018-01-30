#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 19:01:21 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Just a clean simple & independent image data class which is the core of the work
envrionment in Mesmerize Viewer.

seq : 3D array (2D + time) of the image sequence
meta : meta data dictionary
Map : Stimulus map. Contains the definitions of the stimuli & the time that they
occured for the animal that was exposed to in this particular image sequence

"""

class ImgData():
    def __init__(self, seq, meta={}, SampleID=None, Map=None, 
                 isSubArray=False, isMotCor=False, isDenoised=False):
        self.seq = seq
        self.meta = meta.copy()
        self.SampleID = SampleID
        self.Map = Map
        self.isSubArray = isSubArray
        self.isMotCor = isMotCor
        self.isDenoised = isDenoised
        #self.stimMap = mapDict()
    # Simple method to package the stimulus map into a list for each instance of a stimulus
    def setMap(self, dm):
        y = self.meta['AUXo3']['y']
        x = self.meta['AUXo3']['x'][1]
        firstFrameStartTime = self.meta['FoldedFrameInfo']['firstFrameStartTime']
        frameTimeLength = self.meta['FoldedFrameInfo']['frameTimeLength']
        self.Map = []
        for i in range(0,y.shape[1]-1):
            voltage = str(y[1][i])
            tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)
            if tstart_frame < 0:
                tstart_frame = 0
            tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)
            self.Map.append([dm[voltage], (tstart_frame, tend_frame)])
        
        ''' Stimulus Map list organization:
            [['StimName//SubstimName', <pyqtgraph color object>], (startFrame, endFrame)]
            
            list index 0: A list with all stimuli & substimuli. Color object is specified at index -1
            list index 1: Tuple that has the start and end frame of this stimulus
        '''