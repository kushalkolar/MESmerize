#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Adapted from @agiovann and @epnev
"""

from __future__ import division
import sys
import cv2
try:
    cv2.setNumThreads(1)
except:
    print('Open CV is naturally single threaded')
import caiman as cm
import numpy as np
import os
import pickle
import json
from caiman.motion_correction import MotionCorrect
import tifffile
import traceback
# import numba
from glob import glob
from time import time


if not sys.argv[0] == __file__:
    from ...core.common import ViewerUtils
    from ...core.viewer_work_environment import ViewerWorkEnv


def run(batch_dir: str, UUID: str):
    start_time = time()

    output = {'status': 0, 'output_info': ''}
    file_path = batch_dir + '/' + UUID
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)

    c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                     n_processes=n_processes,
                                                     # number of process to use, if you go out of memory try to reduce this one
                                                     single_thread=False)

    try:
        fname = [file_path + '.tiff']
        input_params = pickle.load(open(file_path + '.params', 'rb'))

        niter_rig = input_params['iters_rigid']
        max_shifts = (input_params['max_shifts_x'], input_params['max_shifts_y'])
        splits_rig = n_processes

        strides = (input_params['strides'], input_params['strides'])
        overlaps = (input_params['overlaps'], input_params['overlaps'])
        splits_els = n_processes
        upsample_factor_grid = input_params['upsample']
        max_deviation_rigid = input_params['max_dev']
        gSig_filt = input_params['gSig_filt']

        if os.environ['_MESMERIZE_USE_CUDA'] == 'True':
            USE_CUDA = True
        else:
            USE_CUDA = False

        min_mov = cm.load(fname[0], subindices=range(200)).min()

        mc = MotionCorrect(fname[0], min_mov,
                           dview=dview, max_shifts=max_shifts, niter_rig=niter_rig,
                           splits_rig=splits_rig,
                           strides=strides, overlaps=overlaps, splits_els=splits_els,
                           upsample_factor_grid=upsample_factor_grid,
                           max_deviation_rigid=max_deviation_rigid,
                           shifts_opencv=True, nonneg_movie=True, use_cuda=USE_CUDA, gSig_filt=gSig_filt)

        mc.motion_correct_pwrigid(save_movie=True)
        m_els = cm.load(mc.fname_tot_els)
        bord_px_els = np.ceil(np.maximum(np.max(np.abs(mc.x_shifts_els)),
                                         np.max(np.abs(mc.y_shifts_els)))).astype(np.int)

        # p = pickle.load(open(UUID + '_workEnv.pik', 'rb'))
        # if p['imdata']['meta']['origin'] == 'mes':
        #     if p['imdata']['meta']['orig_meta']['DataType'] == 'uint16':
        #         pass
        #         # lut = BitDepthConverter.create_lut([np.nanmin(m_els), np.nanmax(m_els)], source=16, out=8)

        #
        # else:
        m_els -= np.nanmin(m_els)

        if input_params['output_bit_depth'] == 'Do not convert':
            pass
        elif input_params['output_bit_depth'] == '8':
            m_els = m_els.astype(np.uint8, copy=False)
        elif input_params['output_bit_depth'] == '16':
            m_els = m_els.astype(np.uint16)

        tifffile.imsave(batch_dir + '/' + UUID + '_mc.tiff', m_els, bigtiff=True, imagej=True, compress=1)

        output.update({'status': 1, 'bord_px': int(bord_px_els)})

    except Exception:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    for mf in glob(batch_dir +'/' + UUID +'*.mmap'):
        os.remove(mf)

    dview.terminate()

    end_time = time()
    processing_time = (end_time - start_time) / 60

    output_files_list = [UUID + '_mc.tiff',
                         UUID + '.out'
                         ]

    output.update({'processing_time': processing_time,
                   'output_files': output_files_list})

    json.dump(output, open(file_path + '.out', 'w'))


class Output:
    def __init__(self, batch_path, UUID, viewer_ref):
        vi = ViewerUtils(viewer_ref)

        if not vi.discard_workEnv():
            return

        vi.viewer.status_bar_label.showMessage('Please wait, loading motion corrected image sequence...')
        pik_path = batch_path + '/' + str(UUID) + '_workEnv.pik'
        tiff_path = batch_path + '/' + str(UUID) + '_mc.tiff'
        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pik_path, tiff_path)
        #tiff_path = batch_path + '/' + str(UUID) + '_mc.tiff'
        #workEnv.imgdata.seq = tifffile.imread(tiff_path).T
        vi.update_workEnv()
        vi.viewer.status_bar_label.showMessage('Finished loading motion corrected image sequence!')

        input_params = pickle.load(open(batch_path + '/' + str(UUID) + '.params', 'rb'))

        name = input_params['name_elas']
        vi.viewer.ui.label_curr_img_seq_name.setText('MotCor :' + name)
        bpx = json.load(open(batch_path + '/' + str(UUID) + '.out', 'r'))['bord_px']
        input_params.update({'bord_px': bpx})
        vi.viewer.workEnv.history_trace.append({'caiman_motion_correction': input_params})
        vi.enable_ui(True)


class BitDepthConverter:
    """
    Downscale the bit depth of image to uint8, uint16, or uint32 using a Look up table.
    Usage example:

    First create a LUT (look up table) of the bit depth you desire. Pass the min and max levels as a tuple or list:

    lut_8_bit = create_lut(levels=[32, 2049], source=16, output=8)

    Now use this LUT to downscale an image:

    downscaled_img = apply_lut(img, lut_8_bit)
    """
    @staticmethod
    def create_lut(levels, source, out):
        """
        :param levels:      min and max levels with which to create the LUT
        :type levels:       tuple or list
        :param source:      bit depth of the source. 16, 32, or 64
        :type source:       int
        :param output:      desired output bit depth
        :type output:       int
        :return:            LUT (Look up table) to use for downscaling the bit depth
        :rtype:             np.ndarray
        """

        accepted_srcs = [16, 32, 64]
        if source not in accepted_srcs:
            raise TypeError('Can only convert from uint16, uint32, or uint64')

        accepted_outs = [8, 16, 32]
        if out not in accepted_outs:
            raise TypeError('Can only output uint8, uint16, or uint32')

        type_str = 'uint' + str(source)
        lut = np.arange(2**source, dtype=type_str)
        lut.clip(levels[0], levels[1], out=lut)
        lut -= levels[0]
        np.floor_divide(lut, (levels[1] - levels[0] + 1) / (2**out), out=lut, casting='unsafe')

        type_str = 'uint' + str(out)
        return lut.astype(type_str)

    @staticmethod
    def apply_lut(image, lut):
        """
        :param image:   The image upon which to apply the LUT (Look up table) and change its bit depth
        :type image:    np.ndarray
        :param lut:     The LUT to use for downscaling the bit depth. Generated by BitDepthConvert.create_LUT
        :type lut:      np.ndarray
        :return:        Downscaled image with the LUT (Look up table) applied to it
        :rtype:         np.ndarray
        """
        return np.take(lut, image).astype(lut.dtype)

if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2])
