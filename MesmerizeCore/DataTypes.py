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
import numpy as np


def fix_fp_errors(n):
    fix = np.round(n, decimals=1) + 0.0
    return fix

class ImgData():
    def __init__(self, seq, meta={}, SampleID=None, stimMaps=None, 
                 isSubArray=False, isMotCor=False, isDenoised=False):
        self.seq = seq
        self.meta = meta.copy()
        self.SampleID = SampleID
        self._stimMaps = stimMaps
        self.isSubArray = isSubArray
        self.isMotCor = isMotCor
        self.isDenoised = isDenoised
        #self.stimMap = mapDict()
    # Simple method to package the stimulus map into a list for each instance of a stimulus
    @property
    def stimMaps(self, map_name=None):
        if map_name is None:
            return self._stimMaps
        else:
            try:
                return self._stimMaps[map_name]
            except KeyError:
                print(str(KeyError))
        
    @stimMaps.setter
    def stimMaps(self, maps):
        dm, origin = maps

        if dm is None:
            self._stimMaps = None
            return

        if origin == 'mesfile':
            self._stimMaps = {}

            for machine_channel in dm.keys():
                ch_dict = dm[machine_channel]
                try:
                    y = self.meta[machine_channel]['y']
                    x = self.meta[machine_channel]['x'][1]

                    firstFrameStartTime = self.meta['FoldedFrameInfo']['firstFrameStartTime']
                    frameTimeLength = self.meta['FoldedFrameInfo']['frameTimeLength']

                    current_map = []

                    for i in range(0,y.shape[1]-1):
                        # To convert negative zero to positive zero, and correct for floating point errors
                        voltage = str(fix_fp_errors(y[1][i]))

                        tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)

                        if tstart_frame < 0:
                            tstart_frame = 0

                        tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)

                        current_map.append([ch_dict['values'][voltage], (tstart_frame, tend_frame)])

                    self._stimMaps[ch_dict['channel_name']] = current_map

                except (KeyError, IndexError):
                    print('Voltage values not found for: "' + str(ch_dict['channel_name']) + '" in <' + str(machine_channel) + '>')

            return
        
        elif origin == 'csv':
            pass
            return
        
        
#        y = self.meta['AUXo3']['y']
#        x = self.meta['AUXo3']['x'][1]
#        firstFrameStartTime = self.meta['FoldedFrameInfo']['firstFrameStartTime']
#        frameTimeLength = self.meta['FoldedFrameInfo']['frameTimeLength']
#        self.Map = []
#        for i in range(0,y.shape[1]-1):
#            voltage = str(y[1][i])
#            tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)
#            if tstart_frame < 0:
#                tstart_frame = 0
#            tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)
#            self.Map.append([dm[voltage], (tstart_frame, tend_frame)])
        
        ''' Stimulus Map list organization:
            [['StimName//SubstimName', <pyqtgraph color object>], (startFrame, endFrame)]
            
            list index 0: A list with all stimuli & substimuli. Color object is specified at index -1
            list index 1: Tuple that has the start and end frame of this stimulus
        '''