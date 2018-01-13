#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 17:59:04 2017

@author: kushal

A simple class that does the back-end handilng to export image sequence data.

"""

import numpy as np
import cv2
import tifffile
from functools import partial

class ImgOut():
    def __init__(self, img_data, out_file, vmin=None, vmax=None):
        self.img_data = img_data
        self.out_file = out_file
        self.vmin = vmin
        self.vmax = vmax
        outFormat = self.out_file[-4:]
        #self.lookup(outFormat)
        formats = {'.tif': self.tiff,
                   'tiff': self.tiff,
                   '.npz': self.npz,
                   '.avi': partial(self.vidWrite, 'MJPG'),
                   '.mp4': partial(self.vidWrite, 'X264')
                }
        formats[outFormat]()
    def tiff(self):
        tifffile.imsave(self.out_file,self.img_data.seq.T)

    def npz(self):
        print('yay')
    
    def vidWrite(self, codec):
        fourcc = cv2.VideoWriter_fourcc(*codec)
        print('YAY CODEC IS ' + codec)
        out = cv2.VideoWriter(self.out_file, fourcc, int(self.img_data.fps), 
                        (self.img_data.seq.shape[0], 
                         self.img_data.seq.shape[1]))
        
        if (self.vmin and self.vmax) == None:
            self.vmin = self.img_data.vmin
            self.vmax = self.img_data.vmax
        self.min_substract = self.img_data.seq.astype(np.int32) - self.vmin
        self.scaled = ((self.img_data.seq.astype(np.int32) - self.vmin)
                        * (255/self.vmax)).clip(min=0, max=255).astype(np.uint8)
#        self.no_neg = self.min_substract.clip(min=0)
#        self.scaled = np.array((self.no_neg * (255/self.vmax)), dtype=np.uint8)
        for frame in range(0,self.scaled.shape[2]):
            #print('entered write loop, frame# ' + str(frame))
            
            #if frame == 1364:
                #print(self.img_data.seq[:,:,frame].shape)
                #print(colorFrame.shape)
            out.write(cv2.cvtColor(self.scaled[:,:,frame].T, cv2.COLOR_GRAY2BGR))
        out.release()

