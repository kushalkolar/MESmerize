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
