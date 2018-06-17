# -*- coding: utf-8 -*-
"""
Created on April 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from __future__ import division
from __future__ import print_function
import sys
# from ..common import ViewerInterface, BatchRunInterface
# from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
# from MesmerizeCore import configuration
# from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
# if not len(sys.argv) > 1:
#     from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
    # from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import json
import caiman as cm

from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from past.utils import old_div

import numpy as np
import matplotlib.pyplot as plt
from caiman.source_extraction import cnmf
from caiman.utils.utils import download_demo
from caiman.utils.visualization import inspect_correlation_pnr
from caiman.components_evaluation import estimate_components_quality_auto
from caiman.motion_correction import motion_correct_oneP_rigid,motion_correct_oneP_nonrigid
import os
import pickle
from glob import glob
# from multiprocessing import Pool
from functools import partial


def run(batch_dir, UUID, n_processes):
    output = {'status': 0, 'output_info': ''}
    n_processes = int(n_processes)
    file_path = batch_dir + '/' + UUID

    filename = file_path + '.tiff'
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    frate = input_params['frate']
    gSig = input_params['gSig']
    gSiz = 3 * gSig + 1
    min_corr = input_params['min_corr']
    min_pnr = input_params['min_pnr']
    min_SNR = input_params['min_SNR']
    r_values_min = input_params['r_values_min']
    decay_time = input_params['decay_time']
    rf = input_params['rf']
    stride = input_params['stride']
    gnb = input_params['gnb']
    nb_patch = input_params['nb_patch']
    k = input_params['k']

    filename = [filename]
    # filename_reorder = fnames
    print('***** Starting CNMFE Pool *****')
    print('***** No live output beyond this point =O *****')

    # dview = Pool(n_processes)
    c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                     n_processes=n_processes,
                                                     # number of process to use, if you go out of memory try to reduce this one
                                                     single_thread=False)
    print('Pool started')
    # dview.terminate()
    # self.output.update({'baaaaaaaaaaah': 34534534})
    # self.signals.finished.emit()
    # print('****** sigFinished emitted ********')
    # dview = Pool(configuration.n_processes)
    # create memory mappable file in the right order on the hard drive (C order)
    bord_px = 10
    try:
        print('Creating memmap')
        fname_new = cm.save_memmap_each(
            filename,
            base_name='memmap_' + UUID,
            order='C',
            border_to_0=bord_px,
            dview=dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_' + UUID, dview=dview)
        # load memory mappable file
        Yr, dims, T = cm.load_memmap(fname_new)
        Y = Yr.T.reshape((T,) + dims, order='F')
        # compute some summary images (correlation and peak to noise)
        # change swap dim if output looks weird, it is a problem with tiffile
        cn_filter, pnr = cm.summary_images.correlation_pnr(
            Y, gSig=gSig, swap_dim=False)
        if not input_params['do_cnmfe'] and input_params['do_corr_pnr']:
            pickle.dump(cn_filter, open(filename[0][:-5] + '_cn_filter.pikl', 'wb'), protocol=4)
            pickle.dump(pnr, open(filename[0][:-5] + 'pnr.pikl', 'wb'), protocol=4)
            output.update({'output': filename[0][:-5], 'status': 1, 'output_info': 'inspect correlation & pnr'})
            json.dump(output, open(file_path + '.out', 'w'))
            dview.terminate()

            for mf in glob(batch_dir + '/memmap_*'):
                os.remove(mf)

            return
        # inspect the summary images and set the parameters
        # inspect_correlation_pnr(cn_filter, pnr)
        #
        #
        # reduced from .8
        # min_corr = .89  # min correlation of peak (from correlation image)
        # min_pnr = 4  # min peak to noise ratio
        # min_SNR = 1  # adaptive way to set threshold on the transient size
        # threshold on space consistency (if you lower more components will be accepted, potentially with worst quality)
        # r_values_min = 0.7
        # decay_time = 10  # decay time of transients/indocator

        cnm = cnmf.CNMF(n_processes=n_processes,
                        method_init='corr_pnr',  # use this for 1 photon
                        k=k,  # neurons per patch
                        gSig=(gSig, gSig),  # half size of neuron
                        gSiz=(gSiz, gSiz),  # in general 3*gSig+1
                        merge_thresh=.3,  # threshold for merging
                        p=1,  # order of autoregressive process to fit
                        dview=dview,  # if None it will run on a single thread
                        # downsampling factor in time for initialization, increase if you have memory problems
                        tsub=2,
                        # downsampling factor in space for initialization, increase if you have memory problems
                        ssub=2,
                        # if you want to initialize with some preselcted components you can pass them here as boolean vectors
                        Ain=None,
                        # half size of the patch (final patch will be 100x100)
                        rf=(rf, rf),
                        # overlap among patches (keep it at least large as 4 times the neuron size)
                        stride=(stride, stride),
                        only_init_patch=True,  # just leave it as is
                        gnb=gnb,  # number of background components
                        nb_patch=nb_patch,  # number of background components per patch
                        method_deconvolution='oasis',  # could use 'cvxpy' alternatively
                        low_rank_background=True,  # leave as is
                        # sometimes setting to False improve the results
                        update_background_components=True,
                        min_corr=min_corr,  # min peak value from correlation image
                        min_pnr=min_pnr,  # min peak to noise ration from PNR image
                        normalize_init=False,  # just leave as is
                        center_psf=True,  # leave as is for 1 photon
                        del_duplicates=True,  # whether to remove duplicates from initialization
                        border_pix=bord_px)  # number of pixels to not consider in the borders
        cnm.fit(Y)

        #  DISCARD LOW QUALITY COMPONENTS
        idx_components, idx_components_bad, comp_SNR, r_values, pred_CNN = estimate_components_quality_auto(
            Y, cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, frate,
            decay_time, gSig, dims, dview=dview,
            min_SNR=min_SNR, r_values_min=r_values_min, use_cnn=False)

        print((len(cnm.C)))
        print((len(idx_components)))
        # np.save(filename[:-5] + '_curves.npy', cnm.C)
        filename = filename[0]
        pickle.dump(Yr, open(filename[:-5] + '_Yr.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.A, open(filename[:-5] + '_cnm-A.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.b, open(filename[:-5] + '_cnm-b.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.C, open(filename[:-5] + '_cnm-C.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.f, open(filename[:-5] + '_cnm-f.pikl', 'wb'), protocol=4)
        pickle.dump(idx_components, open(filename[:-5] + '_idx_components.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.YrA, open(filename[:-5] + '_cnm-YrA.pikl', 'wb'), protocol=4)
        pickle.dump(pnr, open(filename[0][:-5] + 'pnr.pikl', 'wb'), protocol=4)
        pickle.dump(cn_filter, open(filename[:-5] + '_cn_filter.pikl', 'wb'), protocol=4)
        pickle.dump(dims, open(filename[:-5] + '_dims.pikl', 'wb'), protocol=4)
        output.update({'output': filename[:-5], 'status': 1})

    except Exception as e:
        output.update({'status': 0, 'output_info': str(e)})

    dview.terminate()

    for mf in glob(batch_dir + '/memmap_*'):
        os.remove(mf)

    json.dump(output, open(file_path + '.out', 'w'))


class Output(QtWidgets.QWidget):
    def __init__(self, batch_dir, UUID, viewer_ref):
        # super(Output, self).__init__()
        self.batch_dir = batch_dir
        self.UUID = UUID
        self.viewer_ref = viewer_ref

        filename = batch_dir + '/' + str(UUID)
        if pickle.load(open(filename + '.params', 'rb'))['do_corr_pnr']:
            print('showing corr pnr')
            self.output_corr_pnr()
        else:
            QtWidgets.QWidget.__init__(self)
            print('opening question box')
            self.setWindowTitle('Show Correlation & PNR image or CNMFE')
            layout = QtWidgets.QVBoxLayout()

            label = QtWidgets.QLabel(self)
            label.setText('Would you like to look at the correlation & PNR image or view the CNMFE output?')
            layout.addWidget(label)

            self.btnCP = QtWidgets.QPushButton()
            self.btnCP.setText('Corr PNR Img')
            # self.btnCP.clicked.connect(self.deleteLater)
            layout.addWidget(self.btnCP)

            self.btnCNMFE = QtWidgets.QPushButton()
            self.btnCNMFE.setText('CNMFE')
            # self.btnCNMFE.clicked.connect(self.deleteLater)

            layout.addWidget(self.btnCNMFE)

            self.setLayout(layout)

            self.btnCP.clicked.connect(self.output_corr_pnr)
            self.btnCNMFE.clicked.connect(self.output_cnmfe)
            self.show()

    def output_corr_pnr(self): #, batch_dir, UUID, viewer_ref):
        filename = self.batch_dir + '/' + str(self.UUID)

        cn_filter = pickle.load(open(finomlename + '_cn_filter.pikl', 'rb'))
        pnr = pickle.load(open(filename + 'pnr.pikl', 'rb'))
        inspect_correlation_pnr(cn_filter, pnr)

    def output_cnmfe(self):# , batch_dir, UUID, viewer_ref):
        print('showing CNMFE')
        filename = self.batch_dir + '/' + str(self.UUID)

        Yr = pickle.load(open(filename + '_Yr.pikl', 'rb'))
        cnmA = pickle.load(open(filename + '_cnm-A.pikl', 'rb'))
        cnmb = pickle.load(open(filename + '_cnm-b.pikl', 'rb'))
        cnmC = pickle.load(open(filename + '_cnm-C.pikl', 'rb'))
        cnm_f = pickle.load(open(filename + '_cnm-f.pikl', 'rb'))
        idx_components = pickle.load(open(filename + '_idx_components.pikl', 'rb'))
        cnmYrA = pickle.load(open(filename + '_cnm-YrA.pikl', 'rb'))
        cn_filter = pickle.load(open(filename + '_cn_filter.pikl', 'rb'))
        dims = pickle.load(open(filename + '_dims.pikl', 'rb'))
        self.visualization = cm.utils.visualization.view_patches_bar(Yr, cnmA[:, idx_components], cnmC[idx_components], cnmb, cnm_f,
                                                dims[0], dims[1], YrA=cnmYrA[idx_components], img=cn_filter)


# class QuestionBox(QtWidgets.QWidget):
#     def __init__(self):
#         super(QuestionBox, self).__init__()


if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2], sys.argv[3])