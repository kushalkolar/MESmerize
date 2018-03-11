#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 13:58:20 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import scipy.io as spio
import numpy as np
from .misc_funcs import fix_fp_errors
from PyQt5 import QtGui

# Loads the entire .mes file as an instance. 
# The load_img() method can be used to return an ImgData class object for any particular image
# of interest from the created MES instance.
class MES():
    """
    Does the back-end handling of opening .mes files and organizing the images and
	meta data. The load_img() method returns a 3D array (2D + time) of the image
	sequence and meta data as a ImgData class object.

	Usage:
        Create a mesfile object by passing the path of your mes file

        Example:
            mesfile = MES.('/home/kushal/olfactory/experiment_Dec_25.mes')

            To get images from the mesfile object:

                Pass a dictionary key (extracted by the __init__ method) as a string
                which refers to the desired image to load.

                imdata = mesfile.load_img('IF0001_0001')
    """
    def __init__(self, filename):
        # Open the weird matlab type objects and organize the images & meta data
        """

        :param filename: full path of a single .mes file
        :type filename: str
        """
        try:
            self.main_dict = self._loadmat(filename)

        except IOError:
            QtGui.QMessageBox.warning(None, 'IOError', 'Unable to open the file you have selected', QtGui.QMessageBox.Ok)

        self.main_dict_keys = [x for x in self.main_dict.keys()]
        self.main_dict_keys.sort()     
        self.images = [x for x in self.main_dict_keys if "I" in x]
        
        self.image_descriptions = {}
        
#        self.ao2VoltList = []
#        self.ao3VoltList = []
        self.voltDict = {}
        for image in self.images:
            try:
                meta = self.main_dict["D"+image[1:6]].tolist()
                meta = self._todict(meta[int(image[-1])-1])
            except Exception as e:
                QtGui.QMessageBox.warning(None, 'Error opening an image',
                                          'There as an error when opening the following image: ' + str("D"+image[1:6]) + \
                                          '\n' + str(e))

            # If auxiliary voltage information (which for example contains information
            # about stimulus timings & can be mapped to stimulus definitions).
            for prefix in ['AUXi', 'AUXo', 'Sh', 'Stim']:
                for n in range(0,9):
                    channel = prefix+str(n)
                    if channel in meta.keys():
                        try:
                            if meta[channel]['y'].ndim == 2:
                                self.voltDict[channel] = list(set(fix_fp_errors(meta[channel]['y'][1])))
        # self.ao3VoltList = self.ao3VoltList + list((np.round(np.unique(meta['AUXo3']['y'][1]), decimals=1)))
                        except (KeyError, IndexError):
                            print(meta['IMAGE'] + ' Does not have: ' + channel)
                            
            for channel in ['PMT_EN', 'Trig', 'PMTenUG', 'PMTenUR', 'PMTenUB']:
                if channel in meta.keys():
                    try:
                        if meta[channel]['y'].ndim == 2:
                            self.voltDict[channel] = list(set(fix_fp_errors(meta[channel]['y'][1])))
                    except (KeyError, IndexError):
                        print(meta['IMAGE'] + ' Does not have: ' + channel)
            try:
                comment = meta["Comment"]
                
                if type(comment) != str:
                    comment = "No description"
                self.image_descriptions[image] = comment
            except KeyError:
                print("error for", image)
                
        #print('bah')
    
    def _loadmat(self, filename):
        '''
        this function should be called instead of direct spio.loadmat
        as it cures the problem of not properly recovering python dictionaries
        from mat files. It calls the function check keys to cure all entries
        which are still mat-objects

        from: `StackOverflow <http://stackoverflow.com/questions/7008608/scipy-io-loadmat-nested-structures-i-e-dictionaries>`_
        '''
        data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
        return self._check_keys(data)

    def _check_keys(self, dict):
        '''
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        '''
        for key in dict:
            if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
                dict[key] = self._todict(dict[key])
        return dict        
    
    def _todict(self, matobj):
        '''
        A recursive function which constructs from matobjects nested dictionaries
        '''
        dict = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                dict[strg] = self._todict(elem)
            else:
                dict[strg] = elem
        return dict
    
    # Returns image as ImgData class object.
    def load_img(self,d):
        """
        :param d: The image reference, usually something like IFxxxx_xxxx or Ifxxxx_xxxx
        :type d: dict
        :return: Boolean, numpy array of the image sequence, dict of metadata
        :rtype: (bool, np.array, dict)

        """
        try:
            meta = self.main_dict["D"+d[1:6]].tolist()
            meta = self._todict(meta[0])
            #        except KeyError:
            #            return False, KeyError

            if len(meta["FoldedFrameInfo"]) > 0:
                start = meta["FoldedFrameInfo"]["firstFramePos"]
                stop = meta["TransversePixNum"]
                #print("Images starting at: ",start)
                #print("Frame width = ",stop)
                im = self.main_dict[d]
                # Trim the 2D array to start at where img acquisition actually begins
                im = im[:,start:]
                # Figure out where the 2D array stops at end of acquisition
                im = im[:,:(im.shape[1] - (im.shape[1]%stop))]
                # Divide the single large 2D array into individual arrays which each
                # represent a single frame
                image_sequence = np.hsplit(im, im.shape[1]/stop)
                # Combine all the frames into one 3D array, 2D + time
                seq = np.dstack(image_sequence)

                return True, seq, meta
        except KeyError:
            return False, None, None

# For testing
if __name__ == '__main__':
    mesfile = MES('/home/kushal/Sars_stuff/github-repos/all_aux_mesfile_sample.mes')
    rval, seq, meta = mesfile.load_img('If0001_0002')
#    y = imdata.meta['AUXo3']['y']
