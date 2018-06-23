#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import pandas as pd
from spyder.widgets.variableexplorer.dataframeeditor import


class StimulusMap:
    def __init__(self):
        self.data =

    @staticmethod
    def get_empty_dataframe():
        return pd.DataFrame(columns=['name', 'start', 'stop', 'color'])

    def from_mes_data(self):
        self._stimMaps = {}

        if origin == 'mesfile':
            # Organize stimulus maps from mesfile objects
            try:
                mes_meta = self.meta['orig_meta']
            except (KeyError, IndexError) as e:
                raise KeyError('Stimulus Data not found! Could not find the stimulus data in the meta-data for this image.')
                self.data = None
                return
            for machine_channel in dm.keys():
                ch_dict = dm[machine_channel]
                try:
                    y = mes_meta[machine_channel]['y']
                    x = mes_meta[machine_channel]['x'][1]

                    firstFrameStartTime = mes_meta['FoldedFrameInfo']['firstFrameStartTime']
                    frameTimeLength = mes_meta['FoldedFrameInfo']['frameTimeLength']

                    current_map = []

                    for i in range(0, y.shape[1] - 1):
                        # To convert negative zero to positive zero, and correct for floating point errors
                        voltage = str(fix_fp_errors(y[1][i]))

                        tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)

                        if tstart_frame < 0:
                            tstart_frame = 0

                        tend_frame = int(((y[0][i + 1] * x) - firstFrameStartTime) / frameTimeLength)

                        current_map.append([ch_dict['values'][voltage], (tstart_frame, tend_frame)])

                    self._stimMaps[ch_dict['channel_name']] = current_map

                except (KeyError, IndexError) as e:
                    QtGui.QMessageBox.information(None, 'FYI: Missing channels in current image',
                                                  'Voltage values not found for: "' + str(ch_dict['channel_name']) + \
                                                  '" in <' + str(machine_channel) + '>.\n' + str(e),
                                                  QtGui.QMessageBox.Ok)

            return

    def from_csv(self):
        pass

    def from_manual_entry(self):
        pass