#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

# Functions for organizing your meta data into a format
# that for Mesmerize to use.
#
# You may define your own function to organize your meta data.
# It MUST return a dict which has at least the following keys:
# `origin`, `fps` and `date`.
#
# The `origin` is a string describing the software or microscope
# the recording comes from. This is for your own record.
# The `fps` is the sampling rate of the recording.
# The `date` is the date & time represented by a string in the
# following format: "YYYYMMDD_HHMMSS"
#
# In addition to these 3 keys, you may include any additional
# information as you wish.
#
# Example:
#
# d = \
# {
#     'origin': "microscope or software origin",
#     'fps':     10.0,
#     'date':    "20201123_172345"
# }
#
# Example function:
#
# def MyMetaOrganizer(path: str) -> dict:
#     """.ext""" # define the file ext in the docstring for it to be automatically recognized in the tiff file GUI
#     raw_meta = function_to_load_my_file(path)
#
#     # do stuff to organize the raw_meta
#
#     meta = ... # stuff to organize raw meta
#
#     # return the organized meta data dict
#     # that mesmerize can use
#
#     return meta
#

import json
import tifffile
from datetime import datetime
import numpy as np
from PyQt5 import QtWidgets
from warnings import warn
from mesmerize.common import is_app

try:
    import xmltodict
except ImportError:
    HAS_XMLTODICT = False
else:
    HAS_XMLTODICT = True


def AwesomeImager(path: str) -> dict:
    """.json"""
    meta = json.load(open(path, 'r'))

    meta_d = \
        {
            'origin': 'AwesomeImager',
            'version': meta['version'],
            'fps': meta['framerate'],
            'date': meta['date'] + '_' + meta['time'],
            'vmin': meta['level_min'],
            'vmax': meta['level_max'],
            'orig_meta': meta  # just the entire original meta data dict
        }
    return meta_d


def json_minimal(path: str) -> dict:
    """.json"""
    meta = json.load(open(path, 'r'))

    required = ['fps', 'date']

    if not all(k in meta.keys() for k in required):
        raise KeyError(f'Meta data dict must contain all mandatory fields: {required}')

    meta_d = \
        {
            'origin': meta['origin'],
            'fps': meta['fps'],
            'date': meta['date'],
            'orig_meta': meta
        }

    return meta_d


def ome_tiff(path: str) -> dict:
    """.tiff"""

    if not HAS_XMLTODICT:
        raise ImportError("`xmltodict` must be installed to use ome_tiff meta data")

    tif = tifffile.TiffFile(path)

    if tif.ome_metadata is None:
        raise ValueError("OME XML meta data is not present in the given tiff file")

    # convert it from the garbled OME XML to a dict for normal humans
    ome_meta = xmltodict.parse(tif.ome_metadata)

    # get date in YYYYMMDD_HHMMSS format
    date = datetime.strptime(
        ome_meta['OME']['OME:Image']['OME:AcquisitionDate'],
        "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%Y%m%d_%H%M%S")

    # list pertaining to image meta data
    ome_img_meta = ome_meta['OME']['OME:Image']['OME:Pixels']['OME:Plane']

    # number of zplanes and number of timepoints
    # if n_zplanes > 1, then n_timepoints is the number of acquired volumes
    n_zplanes = int(ome_meta['OME']['OME:Image']['OME:Pixels']['@SizeZ'])
    n_timepoints = int(ome_meta['OME']['OME:Image']['OME:Pixels']['@SizeT'])

    # an array that will contain all the time deltas
    # use it to get the mean `sampling_rate`, as well as the standard deviation
    # and max deviation from the mean frame rate
    a = np.zeros(shape=(n_zplanes, n_timepoints), dtype=np.float64)

    for n_zplane in range(n_zplanes):
        a[n_zplane, :] = [float(f['@DeltaT']) for f in ome_img_meta if int(f['@TheZ']) == n_zplane]

    sampling_rates = (1 / np.diff(a))

    mean_sampling_rate = sampling_rates.mean()  # mean sampling rate
    std_sampling_rate = sampling_rates.std()  # standard deviation
    max_dev_sampling_rate = sampling_rates.ptp()  # max deviation from mean sampling rate

    if (max_dev_sampling_rate > 0.1) or (std_sampling_rate > 0.01):
        warning_msg = \
            f'This is a warning that the standard deviation or max deviation from the mean sampling rate might be ' \
            f'unusually high' \
            f'\n\n' \
            f'mean sampling rate: {mean_sampling_rate:.5f} Hz\n' \
            f'standard deviation of sampling rate: {std_sampling_rate:.5f} Hz\n' \
            f'maximum deviation from mean sampling rate: {max_dev_sampling_rate:.5f} Hz\n\n' \
            f'This message is shown when the max deviation is > 0.1 Hz or the standard deviation is > 0.01 Hz' \

        if QtWidgets.QApplication.instance() is not None:
            QtWidgets.QMessageBox.warning(
                None,
                'Sampling Rate Warning',
                warning_msg
            )
        else:
            warn(
                warning_msg
            )

    meta_d = \
        {
            'origin': 'ome_tiff',
            'fps': mean_sampling_rate,
            'fps_std': std_sampling_rate,
            'fps_max_dev': max_dev_sampling_rate,
            'date': date,
            'orig_meta': ome_meta
        }

    return meta_d


def ome_tif(path: str) -> dict:
    """.tif"""
    return ome_tiff(path)
