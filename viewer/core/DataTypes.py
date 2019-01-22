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
#from PyQt5 import QtGui
#import pyqtgraphCore.functions as fn
#import csv
#from common import configuration
#from .misc_funcs import fix_fp_errors


class ImgData:
    def __init__(self, seq: np.ndarray, meta: dict = None):
        self.seq = seq
        if meta is None:
            meta = {'origin': 'unknown',
                    'fps': 0,
                    'date': 'unknown',
                    'orig_meta': None
                    }

        self.meta = meta.copy()
