#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 13:58:20 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

class MES:
	Does the back-end handling of opening .mes files and organizing the images and 
	meta data. The load_img() method returns a 3D array (2D + time) of the image 
	sequence and meta data as a ImgData class object.

	Usage:
        Create a mesfile object by passing the path of your mes file
		    
        Example:
            mesfile = MES.('/home/kushal/olfactory/experiment_Dec_25.mes')
		    
            Pass a dictionary key (extracted by the __init__ method) as a string 
            which refers to the desired image to load. 
            
            Returns ImgData class object. (See MesmerizeCore.DataTypes)
		    
            imdata = mesfile.load_img('IF0001_0001')


class tiff:
	Extracts any available meta data from the list of tiff files selected. The 
	load_img() method returns a 3D array (2D + time) of the image sequence and meta 
	data as a ImgData class object.
"""

if __name__ == '__main__':
    import matlab
    import numpy as np
    from DataTypes import ImgData
#else:
#    import matlab
#    from . import matlab
#    import numpy as np
#    from .DataTypes import ImgData # Just a clean simple & independent image data object
    
# Loads the entire .mes file as an instance. 
# The load_img() method can be used to return an ImgData class object for any particular image
# of interest from the created MES instance.
class MES():
    def __init__(self, filename):
        # Open the weird matlab type objects and organize the images & meta data
        self.main_dict = matlab.loadmat(filename)
        self.main_dict_keys = [x for x in self.main_dict.keys()]
        self.main_dict_keys.sort()     
        self.images = [x for x in self.main_dict_keys if "I" in x]
        
        self.image_descriptions = {}
        
        self.ao2VoltList = []
        self.ao3VoltList = []
        
        for image in self.images:
            meta = self.main_dict["D"+image[1:6]].tolist()
            meta = matlab._todict(meta[int(image[-1])-1])
            
            # If auxiliary voltage information (which for example contains information
            # about stimulus timings & can be mapped to stimulus definitions).
            if 'AUXo3' in meta.keys():
                try:
                    self.ao3VoltList = self.ao3VoltList + list((np.round(np.unique(meta['AUXo3']['y'][1]), decimals=1)))
                except:
                    print(meta['IMAGE'] + ' Does not have auxo3')
    
            try:
                comment = meta["Comment"]
                
                if type(comment) != str:
                    comment = "No description"
                self.image_descriptions[image] = comment
            except:
                print("error for", image)
                
        self.ao3VoltList = list(set(self.ao3VoltList))
        #print('bah')
    
    # Returns image as ImgData class object.
    def load_img(self,d):
        try:
            meta = self.main_dict["D"+d[1:6]].tolist()
            meta = matlab._todict(meta[0])
        except KeyError:
            return False, None
        
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
            
            return True, ImgData(seq, meta)
#        else: 
#            return self.main_dict[d]


class tiff():
    def __init__(self, files):
        # Organize meta data
        print('Not implemented yet')
    def load_img(self):
        # return ImgData class object
        #return ImgData()
        pass
    
# For testing
if __name__ == '__main__':
    mesfile = MES('/home/kushal/Sars_stuff/Olfactory exps/NH4/Dec 3 a1.mes')
    imdata = mesfile.load_img('If0001_0001')
#    y = imdata.meta['AUXo3']['y']
