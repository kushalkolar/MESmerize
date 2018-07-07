# -*- coding: utf-8 -*-
"""
Created on July 7 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Adapted from @agiovann and @epnev
"""

from __future__ import division
import sys
import cv2
import glob
try:
    cv2.setNumThreads(1)
except:
    print('Open CV is naturally single threaded')
try:
    if __IPYTHON__:
        print("Running under iPython")
        # this is used for debugging purposes only. allows to reload classes
        # when changed
        get_ipython().magic('load_ext autoreload')
        get_ipython().magic('autoreload 2')
except NameError:
    pass
import caiman as cm
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from caiman.utils.visualization import plot_contours, view_patches_bar
from caiman.source_extraction.cnmf import cnmf as cnmf
from caiman.source_extraction.cnmf.utilities import detrend_df_f
from caiman.components_evaluation import estimate_components_quality_auto
import tifffile
import pickle

if not sys.arv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core.common import ViewerInterface, ViewerWorkEnv


def run(batch_dir, UUID, n_processes):

    output = {'status': 0, 'output_info': ''}
    n_processes = int(n_processes)
    file_path = batch_dir + '/' + UUID

    images = tifffile.imread(file_path + '.tiff')
    dims = (images.shape[1], images.shape[2])
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    fr = input_params['fr']
    p = input_params['p']
    gnb = input_params['gnb']
    merge_thresh = input_params['merge_thresh']
    rf = input_params['rf']
    stride_cnmf = input_params['stride_cnmf']
    K = input_params['k']
    gSig = input_params['gSig']
    min_SNR = input_params['min_SNR']
    rval_thr = input_params['rval_thr']
    cnn_thr = input_params['cnn_thr']
    decay_time = input_params['decay_time']

    c, dview, np = cm.cluster.setup_cluster(backend='local', n_processes=n_processes, single_thread=False)

    cnm = cnmf.CNMF(n_processes=1, k=K, gSig=gSig, merge_thresh=merge_thresh,
                    p=0, dview=dview, rf=rf, stride=stride_cnmf, memory_fact=1,
                    method_init='greedy_roi', alpha_snmf=None,
                    only_init_patch=False, gnb=gnb, border_pix=7)
    cnm.fit(images)

    idx_components, idx_components_bad, SNR_comp, r_values, cnn_preds = \
        estimate_components_quality_auto(images, cnm.A, cnm.C, cnm.b, cnm.f,
                                         cnm.YrA, fr, decay_time, gSig, dims,
                                         dview=dview, min_SNR=min_SNR,
                                         r_values_min=rval_thr, use_cnn=False,
                                         thresh_cnn_lowest=cnn_thr)
    A_in, C_in, b_in, f_in = cnm.A[:,
                             idx_components], cnm.C[idx_components], cnm.b, cnm.f
    cnm2 = cnmf.CNMF(n_processes=1, k=A_in.shape[-1], gSig=gSig, p=p, dview=dview,
                     merge_thresh=merge_thresh, Ain=A_in, Cin=C_in, b_in=b_in,
                     f_in=f_in, rf=None, stride=None, gnb=gnb,
                     method_deconvolution='oasis', check_nan=True)

    cnm2 = cnm2.fit(images)

    F_dff = detrend_df_f(cnm2.A, cnm2.b, cnm2.C, cnm2.f, YrA=cnm2.YrA,
                         quantileMin=8, frames_window=250)

