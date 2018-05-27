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
from PyQt5 import QtGui
import pyqtgraphCore.functions as fn
import csv
from . import configuration
from . misc_funcs import fix_fp_errors


class ImgData():
    def __init__(self, seq, meta={}, SampleID=None, Genotype='untagged', stimMaps=None,
                 isSubArray=False, isMotCor=False, isDenoised=False):
        self.seq = seq
        self.meta = meta.copy()
        self.SampleID = SampleID
        self.Genotype = Genotype
        self._stimMaps = stimMaps
        self.isSubArray = isSubArray
        self.isMotCor = isMotCor
        self.isDenoised = isDenoised

    @property
    def stimMaps(self, map_name=None):
        ''' stimMaps property organization:
            Each items of the dict is a list of lists.

            Each list is organized in this way:

            [['StimName//SubstimName', <pyqtgraph color object>], (startFrame, endFrame)]

            list index 0: A list with all stimuli & substimuli. Color object is specified at index -1
            list index 1: Tuple that has the start and end frame of this stimulus
        '''
        if map_name is None:
            return self._stimMaps
        else:
            try:
                return self._stimMaps[map_name]
            except KeyError:
                print(str(KeyError))

    # Simple method to package the stimulus map into a list for each instance of a stimulus
    @stimMaps.setter
    def stimMaps(self, maps):
        """

        :param maps: tuple in the format: (<dict of stimulus maps>, <str, originating source of the map>)
        :return: None
        """
        dm, origin = maps

        if dm is None:
            return

        self._stimMaps = {}

        if origin == 'mesfile':
            # Organize stimulus maps from mesfile objects
            try:
                mes_meta = self.meta['orig_meta']
            except (KeyError, IndexError) as e:
                QtGui.QMessageBox.warning(None, 'Stimulus Data not found!', 'Could not find the stimulus data in the '
                                                                           'meta-data for this image.')
                self._stimMaps = {}
                return
            for machine_channel in dm.keys():
                ch_dict = dm[machine_channel]
                try:
                    y = mes_meta[machine_channel]['y']
                    x = mes_meta[machine_channel]['x'][1]

                    firstFrameStartTime = mes_meta['FoldedFrameInfo']['firstFrameStartTime']
                    frameTimeLength = mes_meta['FoldedFrameInfo']['frameTimeLength']

                    current_map = []

                    for i in range(0, y.shape[1]-1):
                        # To convert negative zero to positive zero, and correct for floating point errors
                        voltage = str(fix_fp_errors(y[1][i]))

                        tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)

                        if tstart_frame < 0:
                            tstart_frame = 0

                        tend_frame = int(((y[0][i+1] * x) - firstFrameStartTime) / frameTimeLength)

                        current_map.append([ch_dict['values'][voltage], (tstart_frame, tend_frame)])

                    self._stimMaps[ch_dict['channel_name']] = current_map

                except (KeyError, IndexError) as e:
                    QtGui.QMessageBox.information(None, 'FYI: Missing channels in current image',
                          'Voltage values not found for: "' + str(ch_dict['channel_name']) +\
                          '" in <' + str(machine_channel) + '>.\n' + str(e), QtGui.QMessageBox.Ok)

            return
        
        elif origin == 'csv':
            # Oraganize stimulus maps from CSV files
            files = dm

            for file in files:
                currentMap = []
                current_map = []

                try:
                    with open(file, newline='') as csvfile:
                        f = csv.reader(csvfile, delimiter=',')

                        for row in f:
                            currentMap.append(row)
                except IOError as e:
                    QtGui.QMessageBox.warning(None, 'Invalid Map file!',
                          'IOError while reading the file.\n' + str(e))
                    return

                try:
                    rmap = currentMap[1:]
                except IndexError as e:
                    QtGui.QMessageBox.warning(None, 'Invalid Map file!',
                          'This does not appear to be a stimulus map file! ' +\
                          'It is not formatted correctly..\n' + str(e))
                    return

                colors = {}
                i = 0
                try:
                    while rmap[i][1] != 'tstart':
                        colors[rmap[i][0]] = fn.mkColor(rmap[i][1])
                        i += 1
                except (IndexError, UnboundLocalError) as e:
                    QtGui.QMessageBox.warning(None, 'Invalid Map file!',
                          'This does not appear to be a stimulus map file! ' +\
                          'It is not formatted correctly.\n' + str(e))
                    return

                try:
                    for r in range(i, len(rmap)):

                        if rmap[r][1] == 'tstart':
                            rmap[r][2] = int(0)
                            continue

                        if int(rmap[r][1]) == int(rmap[r-1][2]):
                            rmap[r][1] = int(rmap[r][1]) + 1

                        current_map.append([ [rmap[r][0], colors[rmap[r][0]] ],
                                             (int(rmap[r][1]) * 24, int(rmap[r][2]) * 24)])
                except (IndexError, ValueError) as e:
                    QtGui.QMessageBox.warning(None, 'Invalid Map file!',
                          'This does not appear to be a stimulus map file! ' + \
                          'It is not formatted correctly..\n' + str(e))

                self._stimMaps[file.split('/')[-1].split('.csv')[0]] = current_map

            return