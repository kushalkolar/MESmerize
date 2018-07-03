#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import pandas as pd
from common.misc_functions import floating_point_equality


def create_stim_maps_dataframe(mes_meta: dict, voltage_stimulus_mapping: pd.DataFrame) -> pd.DataFrame:
    for voltage_channel in voltage_stimulus_mapping.keys():
        channel_dict = voltage_stimulus_mapping[voltage_channel]
        try:
            y = mes_meta[voltage_channel]['y']
            x = mes_meta[voltage_channel]['x'][1]

            firstFrameStartTime = mes_meta['FoldedFrameInfo']['firstFrameStartTime']
            frameTimeLength = mes_meta['FoldedFrameInfo']['frameTimeLength']

            current_map = []

            for i in range(0, y.shape[1] - 1):
                voltage = str(y[1][i])

                tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)

                if tstart_frame < 0:
                    tstart_frame = 0

                tend_frame = int(((y[0][i + 1] * x) - firstFrameStartTime) / frameTimeLength)

                current_map.append([channel_dict['values'][voltage], (tstart_frame, tend_frame)])

            self._stimMaps[channel_dict['channel_name']] = current_map

        except (KeyError, IndexError) as e:
            QtGui.QMessageBox.information(None, 'FYI: Missing channels in current image',
                                          'Voltage values not found for: "' + str(channel_dict['channel_name']) + \
                                          '" in <' + str(voltage_channel) + '>.\n' + str(e),
                                          QtGui.QMessageBox.Ok)

    return
