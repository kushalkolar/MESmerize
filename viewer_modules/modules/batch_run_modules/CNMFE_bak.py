#!/usr/bin/env python3
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
from ..common import ViewerInterface, BatchRunInterface
from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
from MesmerizeCore import configuration
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import json
import caiman as cm

from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from past.utils import old_div
try:
    get_ipython().magic(u'load_ext autoreload')
    get_ipython().magic(u'autoreload 2')
except:
    print('Not IPYTHON')

import numpy as np
import matplotlib.pyplot as plt
import caiman as cm
from caiman.source_extraction import cnmf
from caiman.utils.utils import download_demo
from caiman.utils.visualization import inspect_correlation_pnr
from caiman.components_evaluation import estimate_components_quality_auto
from caiman.motion_correction import motion_correct_oneP_rigid,motion_correct_oneP_nonrigid
import os
import pickle
import multiprocessing


class ThreadSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()


class Batch(QtCore.QRunnable):
    # self.finished = QtCore.pyqtSignal()

    def __init__(self):
        super(Batch, self).__init__()
        # multiprocessing.Process.__init__(self)
        # QtCore.QRunnable.__init__(self)
        # QtCore.QObject.__init__(self)
        # super(BatchRunInterface, self).__init__()
        # self.signals = BatchRunSignals()
        self.signals = ThreadSignals()
        self.output = {'status': 'fail', 'output_info': ''}

    def set_inputs(self, input_workEnv, input_params):
        self.input_workEnv = input_workEnv
        self.input_params = input_params
        print('************** Item inputs set **************')
    # itemFinished = QtCore.pyqtSignal()

    # def __init__(self):
    #     super(Batch, self).__init__()
        # BatchRunInterface.__init__(self)
        # QtCore.QObject.__init__()
    # @QtCore.pyqtSlot()

    def get_output(self):
        return self.output

    def run(self):
        input_workEnv = self.input_workEnv
        input_params = self.input_params
        # ThreadCNMFE(filename=input_workEnv, input_params=input_params)
        frate =         input_params['frate']
        gSig =          input_params['gSig']
        gSiz =          3*gSig+1
        min_corr =      input_params['min_corr']
        min_pnr =       input_params['min_pnr']
        min_SNR =       input_params['min_SNR']
        r_values_min =  input_params['r_values_min']
        decay_time =    input_params['decay_time']
        rf =            input_params['rf']
        stride =        input_params['stride']
        gnb =           input_params['gnb']
        nb_patch =      input_params['nb_patch']
        k =             input_params['k']

        filename = [input_workEnv]
        self.filename = input_workEnv
        # filename_reorder = fnames
        print('************ Starting CNMFE Pool ************')
        # dview = Pool(configuration.n_processes)
        c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                         n_processes=configuration.n_processes,
                                                         # number of process to use, if you go out of memory try to reduce this one
                                                         single_thread=False)
        # dview.terminate()
        # self.output.update({'baaaaaaaaaaah': 34534534})
        # self.signals.finished.emit()
        # print('****** sigFinished emitted ********')
        # dview = Pool(configuration.n_processes)
        # create memory mappable file in the right order on the hard drive (C order)
        bord_px = 10
        try:
            fname_new = cm.save_memmap_each(
                filename,
                base_name='memmap_',
                order='C',
                border_to_0=bord_px,
                dview=dview)
            fname_new = cm.save_memmap_join(fname_new, base_name='memmap_', dview=dview)
            print("**** REACHED LINE 84 ****")
            # load memory mappable file
            Yr, dims, T = cm.load_memmap(fname_new)
            Y = Yr.T.reshape((T,) + dims, order='F')
            print("**** REACHED LINE 88 ****")
            # compute some summary images (correlation and peak to noise)
            # change swap dim if output looks weird, it is a problem with tiffile
            cn_filter, pnr = cm.summary_images.correlation_pnr(
                Y, gSig=gSig, swap_dim=False)
            print("**** REACHED LINE 93 ****")
            # inspect the summary images and set the parameters
            #    inspect_correlation_pnr(cn_filter, pnr)
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
            print("**** REACHED LINE 131 ****")
            cnm.fit(Y)
            print("**** REACHED LINE 133 ****")

            #  DISCARD LOW QUALITY COMPONENTS
            idx_components, idx_components_bad, comp_SNR, r_values, pred_CNN = estimate_components_quality_auto(
                Y, cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, frate,
                decay_time, gSig, dims, dview=dview,
                min_SNR=min_SNR, r_values_min=r_values_min, use_cnn=False)

            print(' ******** REACHED LINE 141 ********* ')
            print((len(cnm.C)))
            print((len(idx_components)))
            # np.save(filename[:-5] + '_curves.npy', cnm.C)
            filename = self.filename
            pickle.dump(Yr, open(filename[:-5] + '_Yr.pikl', 'wb'), protocol=4)
            pickle.dump(cnm.A, open(filename[:-5] + '_cnm-A.pikl', 'wb'), protocol=4)
            pickle.dump(cnm.b, open(filename[:-5] + '_cnm-b.pikl', 'wb'), protocol=4)
            pickle.dump(cnm.C, open(filename[:-5] + '_cnm-C.pikl', 'wb'), protocol=4)
            pickle.dump(cnm.f, open(filename[:-5] + '_cnm-f.pikl', 'wb'), protocol=4)
            pickle.dump(idx_components, open(filename[:-5] + '_idx_components.pikl', 'wb'), protocol=4)
            pickle.dump(cnm.YrA, open(filename[:-5] + '_cnm-YrA.pikl', 'wb'), protocol=4)
            pickle.dump(cn_filter, open(filename[:-5] + '_cn_filter.pikl', 'wb'), protocol=4)
            pickle.dump(dims, open(filename[:-5] + '_dims.pikl', 'wb'), protocol=4)

            self.output.update({'output': self.filename[:-5], 'status': 'success'})
            print('****** dview terminated ********')
            dview.terminate()
            self.signals.finished.emit()
            print('****** sigFinished emitted ********')

        except Exception as e:
            self.output.update({'status': 'fail', 'error_msg': str(e)})
            dview.terminate()
            self.signals.finished.emit()

    @staticmethod
    def show_output(output):
        filename = output['output']
        Yr = pickle.load(open(filename + '_Yr.pikl', 'rb'))
        cnmA = pickle.load(open(filename + '_cnm-A.pikl', 'rb'))
        cnmb = pickle.load(open(filename + '_cnm-b.pikl', 'rb'))
        cnmC = pickle.load(open(filename + '_cnm-C.pikl', 'rb'))
        cnm_f = pickle.load(open(filename + '_cnm-f.pikl', 'rb'))
        idx_components = pickle.load(open(filename + '_idx_components.pikl', 'rb'))
        cnmYrA = pickle.load(open(filename + '_cnm-YrA.pikl', 'rb'))
        cn_filter = pickle.load(open(filename + '_cn_filter.pikl', 'rb'))
        dims = pickle.load(open(filename + '_dims.pikl', 'rb'))
        cm.utils.visualization.view_patches_bar(Yr, cnmA[:, idx_components], cnmC[idx_components], cnmb, cnm_f,
                                                dims[0], dims[1], YrA=cnmYrA[idx_components], img=cn_filter)


def run(UUID, input_workEnv, input_params):
    output = {'status': 'fail', 'output_info': ''}
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

    filename = [input_workEnv]
    # filename_reorder = fnames
    print('************ Starting CNMFE Pool ************')
    # dview = Pool(configuration.n_processes)
    c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                     n_processes=configuration.n_processes,
                                                     # number of process to use, if you go out of memory try to reduce this one
                                                     single_thread=False)
    # dview.terminate()
    # self.output.update({'baaaaaaaaaaah': 34534534})
    # self.signals.finished.emit()
    # print('****** sigFinished emitted ********')
    # dview = Pool(configuration.n_processes)
    # create memory mappable file in the right order on the hard drive (C order)
    bord_px = 10
    try:
        fname_new = cm.save_memmap_each(
            filename,
            base_name='memmap_',
            order='C',
            border_to_0=bord_px,
            dview=dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_', dview=dview)
        print("**** REACHED LINE 84 ****")
        # load memory mappable file
        Yr, dims, T = cm.load_memmap(fname_new)
        Y = Yr.T.reshape((T,) + dims, order='F')
        print("**** REACHED LINE 88 ****")
        # compute some summary images (correlation and peak to noise)
        # change swap dim if output looks weird, it is a problem with tiffile
        cn_filter, pnr = cm.summary_images.correlation_pnr(
            Y, gSig=gSig, swap_dim=False)
        print("**** REACHED LINE 93 ****")
        # inspect the summary images and set the parameters
        #    inspect_correlation_pnr(cn_filter, pnr)
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
        print("**** REACHED LINE 131 ****")
        cnm.fit(Y)
        print("**** REACHED LINE 133 ****")

        #  DISCARD LOW QUALITY COMPONENTS
        idx_components, idx_components_bad, comp_SNR, r_values, pred_CNN = estimate_components_quality_auto(
            Y, cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, frate,
            decay_time, gSig, dims, dview=dview,
            min_SNR=min_SNR, r_values_min=r_values_min, use_cnn=False)

        print(' ******** REACHED LINE 141 ********* ')
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
        pickle.dump(cn_filter, open(filename[:-5] + '_cn_filter.pikl', 'wb'), protocol=4)
        pickle.dump(dims, open(filename[:-5] + '_dims.pikl', 'wb'), protocol=4)
        output.update({'output': filename[:-5], 'status': 'success'})
    except Exception as e:
        output.update({'status': 'fail', 'error_msg': str(e)})
        dview.terminate()
        json.dump(output, open(str(UUID) + '.out'))



class ThreadCNMFE(QtCore.QThread):
    def __init__(self, batch_manager_ref, filename, input_params):
        QtCore.QThread.__init__(self)
        self.filename = filename
        self.input_params = input_params

    def __del__(self):
        self.wait()

    def run(self):
        input_params = self.input_params
        filename = self.filename
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
        c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                         n_processes=configuration.n_processes,
                                                         # number of process to use, if you go out of memory try to reduce this one
                                                         single_thread=False)
        # dview = Pool(configuration.n_processes)
        # create memory mappable file in the right order on the hard drive (C order)
        bord_px = 10
        fname_new = cm.save_memmap_each(
            filename,
            base_name='memmap_',
            order='C',
            border_to_0=bord_px,
            dview=dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_', dview=dview)
        print("**** REACHED LINE 84 ****")
        # load memory mappable file
        Yr, dims, T = cm.load_memmap(fname_new)
        Y = Yr.T.reshape((T,) + dims, order='F')
        print("**** REACHED LINE 88 ****")
        # compute some summary images (correlation and peak to noise)
        # change swap dim if output looks weird, it is a problem with tiffile
        cn_filter, pnr = cm.summary_images.correlation_pnr(
            Y, gSig=gSig, swap_dim=False)
        print("**** REACHED LINE 93 ****")
        # inspect the summary images and set the parameters
        #    inspect_correlation_pnr(cn_filter, pnr)
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
        print("**** REACHED LINE 131 ****")
        cnm.fit(Y)
        print("**** REACHED LINE 133 ****")

        #  DISCARD LOW QUALITY COMPONENTS
        idx_components, idx_components_bad, comp_SNR, r_values, pred_CNN = estimate_components_quality_auto(
            Y, cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, frate,
            decay_time, gSig, dims, dview=dview,
            min_SNR=min_SNR, r_values_min=r_values_min, use_cnn=False)

        print(' ******** REACHED LINE 141 ********* ')
        print((len(cnm.C)))
        print((len(idx_components)))
        # np.save(filename[:-5] + '_curves.npy', cnm.C)
        pickle.dump(Yr, open(filename[:-5] + '_Yr.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.A, open(filename[:-5] + '_cnm-A.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.b, open(filename[:-5] + '_cnm-b.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.C, open(filename[:-5] + '_cnm-C.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.f, open(filename[:-5] + '_cnm-f.pikl', 'wb'), protocol=4)
        pickle.dump(idx_components, open(filename[:-5] + '_idx_components.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.YrA, open(filename[:-5] + '_cnm-YrA.pikl', 'wb'), protocol=4)
        pickle.dump(cn_filter, open(filename[:-5] + '_cn_filter.pikl', 'wb'), protocol=4)
        pickle.dump(dims, open(filename[:-5] + '_dims.pikl', 'wb'), protocol=4)

        dview.terminate()


class VisualizeComponents(ViewerInterface, QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QWidget.__init__(self, parent)


class VisualizeCorrelationPNR(ViewerInterface, QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self,  viewer_ref)

        QtWidgets.QWidget.__init__(self, parent)
