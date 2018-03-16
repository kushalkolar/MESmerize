#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 17:59:04 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

A simple class that does the back-end handilng to export image sequence data.

"""

import numpy as np
import cv2
import tifffile
from functools import partial
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import imageio
import cv2


# vmin & vmax only has to be supplied for video outputs since videos cannot contain
# the full range of 16 bit image depth (OpenCV & 16 bit grayscale is a nightmare to deal with)
class Exporter:
    def __init__(self, img_data, out_file, **kwargs):
        if out_file[-4:] != 'tiff' and 'levels' not in kwargs.keys():
            raise ValueError('levels must be specified for file formats other than tiff or npz')

        if 'fps' in kwargs.keys():
            self.fps = kwargs['fps']
        else:
            self.fps = img_data.meta['fps']

        self.img_data = img_data
        self.out_file = out_file
        if 'levels' in kwargs.keys():
            vmin = kwargs['levels'][0]
            vmax = kwargs['levels'][1]
            self.vmin = vmin
            self.vmax = vmax
        outFormat = self.out_file[-4:]

        formats = {'.tif': self.tiff,
                   'tiff': self.tiff,
                   '.npz': self.npz,
                   '.avi': partial(self.vidWrite, 'MJPG'),
                   '.mp4': partial(self.vidWrite, 'X264'),
                   '.gif': self.gif
                   }

        formats[outFormat]()

    def gif(self):
        scaled = self.scale_levels()
        print(scaled)
        with imageio.get_writer(self.out_file, mode='I') as writer:
            for frame in range(0, scaled.shape[2]):
                writer.append_data(scaled[:, :, frame].T)

    def tiff(self):
        tifffile.imsave(self.out_file,self.img_data.seq.T)

    def npz(self):
        print('yay')

    def scale_levels(self):

        scaled = ((self.img_data.seq - self.vmin) * (255/self.vmax)).clip(min=0, max=255).astype(np.uint8)
        # np.nan_to_num(scaled, copy=False)
        print(scaled)
        return scaled

    def vidWrite(self, codec):
        fourcc = cv2.VideoWriter_fourcc(*codec)
        print('YAY CODEC IS ' + codec)
        out = cv2.VideoWriter(self.out_file, fourcc, int(self.fps),
                        (self.img_data.seq.shape[0],
                         self.img_data.seq.shape[1]))
        scaled = self.scale_levels()
        # if (self.vmin and self.vmax) == None:
        #     self.vmin = self.img_data.vmin
        #     self.vmax = self.img_data.vmax
        # self.min_substract = self.img_data.seq.astype(np.int32) - self.vmin
        # self.scaled = ((self.img_data.seq.astype(np.int32) - self.vmin)
        #                 * (255/self.vmax)).clip(min=0, max=255).astype(np.uint8)
#        self.no_neg = self.min_substract.clip(min=0)
#        self.scaled = np.array((self.no_neg * (255/self.vmax)), dtype=np.uint8)
        for frame in range(0, scaled.shape[2]):
            #print('entered write loop, frame# ' + str(frame))
            out.write(cv2.cvtColor(scaled[:, :, frame].T, cv2.COLOR_GRAY2BGR))
        out.release()
