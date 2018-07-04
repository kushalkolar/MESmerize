#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 13:58:20 2017

@author: kushal, adapted from Daniel Dondorp

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import scipy.io as spio
import numpy as np
# from .misc_funcs import fix_fp_errors
import traceback
# from common.misc_functions import floating_point_equality


class MES:
    """
    Handles of opening .mes files and organizing the images and meta data.
    The load_img() method returns a 3D array (2D + time) of the image sequence
    and meta data as a ImgData class object.

    Usage:
    Create a mesfile object by passing the path of your mes file, example:

    mesfile = MES('/path/to/mesfile/experiment_Feb_31.mes')

    To get images from the mesfile object:

        Pass a dictionary key (extracted by the class constructor) as a string
        which refers to the desired image to load.

        imdata = mesfile.load_img('IF0001_0001')
    """

    def __init__(self, filename: str):
        # Open the weird matlab type objects and organize the images & meta data
        """
        :param filename: full path of a single .mes file
        """
        self.main_dict = self._loadmat(filename)

        self.main_dict_keys = [x for x in self.main_dict.keys()]
        self.main_dict_keys.sort()
        self.images = [x for x in self.main_dict_keys if "I" in x]

        self.image_descriptions = {}

        self.voltages_lists_dict = {}
        self.errors = []

        for image in self.images:
            try:
                meta = self.main_dict["D" + image[1:6]].tolist()
                meta = self._todict(meta[int(image[-1]) - 1])
            except Exception:
                self.errors.append('Error opening an image, There as an error when opening the following image: ' + str(
                    "D" + image[1:6]) + '\n' + traceback.format_exc())

            # If auxiliary voltage information (which for example contains information
            # about stimulus timings & can be mapped to stimulus definitions).
            for prefix in ['AUXi', 'AUXo', 'Sh', 'Stim']:
                for n in range(0, 9):
                    channel = prefix + str(n)
                    if channel in meta.keys():
                        try:
                            if meta[channel]['y'].ndim == 2:
                                self.voltages_lists_dict[channel] = list(set(meta[channel]['y'][1]))
                        except (KeyError, IndexError) as e:
                            self.errors.append(str(e) + ': ' + meta['IMAGE'] + ' Does not have: ' + channel)

            for channel in ['PMT_EN', 'Trig', 'PMTenUG', 'PMTenUR', 'PMTenUB']:
                if channel in meta.keys():
                    try:
                        if meta[channel]['y'].ndim == 2:
                            self.voltages_lists_dict[channel] = list(set(meta[channel]['y'][1]))
                    except (KeyError, IndexError) as e:
                        self.errors.append(str(e) + ': ' + meta['IMAGE'] + ' Does not have: ' + channel)
            try:
                comment = meta["Comment"]

                if type(comment) != str:
                    comment = "No description"
                self.image_descriptions[image] = comment
            except KeyError as e:
                self.errors.append(str(e) + ': ' + '"error for: "' + image)

                # print('bah')

    def _loadmat(self, filename):
        data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
        return self._check_keys(data)

    def _check_keys(self, dict):
        for key in dict:
            if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
                dict[key] = self._todict(dict[key])
        return dict

    def _todict(self, matobj):
        dict = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                dict[strg] = self._todict(elem)
            else:
                dict[strg] = elem
        return dict

    # Returns image as ImgData class object.
    def load_img(self, img_reference: str) -> (np.ndarray, dict):
        """
        :param img_reference: The image reference, usually something like IFxxxx_xxxx or Ifxxxx_xxxx
        :return: numpy array of the image sequence, dict of metadata
        """
        meta = self.main_dict["D" + img_reference[1:6]].tolist()
        meta = self._todict(meta[0])
        #        except KeyError:
        #            return False, KeyError

        if len(meta["FoldedFrameInfo"]) > 0:
            start = meta["FoldedFrameInfo"]["firstFramePos"]
            stop = meta["TransversePixNum"]
            # print("Images starting at: ",start)
            # print("Frame width = ",stop)
            im = self.main_dict[img_reference]
            # Trim the 2D array to start at where img acquisition actually begins
            im = im[:, start:]
            # Figure out where the 2D array stops at end of acquisition
            im = im[:, :(im.shape[1] - (im.shape[1] % stop))]
            # Divide the single large 2D array into individual arrays which each
            # represent a single frame
            image_sequence = np.hsplit(im, im.shape[1] / stop)
            # Combine all the frames into one 3D array, 2D + time
            seq = np.dstack(image_sequence)

            return seq, meta
        else:
            raise KeyError("'" + str(img_reference) + "' does not have the required "
                                                        "'FoldedFrameInfo' meta-data which is "
                                                        "required for the construction of an image "
                                                        "sequence from mesfile data")


# For testing
if __name__ == '__main__':
    mesfile = MES('/home/kushal/Sars_stuff/Olfactory exps/NH4/Dec 3 a1.mes')
# y = imdata.meta['AUXo3']['y']
