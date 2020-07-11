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
import logging

if not sys.argv[0] == __file__:
    from ...core.common import ViewerUtils
    from ...core.viewer_work_environment import ViewerWorkEnv


def run(batch_dir: str, UUID: str):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s")
    start_time = time()

    output = {'status': 0, 'output_info': ''}
    file_path = os.path.join(batch_dir, UUID)
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)

    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )

    try:
        fname = [file_path + '_input.tiff']
        input_params = pickle.load(open(file_path + '.params', 'rb'))
        # TODO: Should just unpack the input params as kwargs
        mc_kwargs = input_params['mc_kwargs']

        splits_rig = n_processes

        splits_els = n_processes

        if os.environ['_MESMERIZE_USE_CUDA'] == 'True':
            USE_CUDA = True
        else:
            USE_CUDA = False

        min_mov = cm.load(fname[0], subindices=range(200)).min()

        mc = MotionCorrect(
            fname[0], min_mov,
            dview=dview,
            splits_rig=splits_rig,
            splits_els=splits_els,
            shifts_opencv=True,
            nonneg_movie=True,
            use_cuda=USE_CUDA,
            **mc_kwargs
        )

        mc.motion_correct_pwrigid(save_movie=True)
        m_els = cm.load(mc.fname_tot_els)
        bord_px_els = np.ceil(np.maximum(np.max(np.abs(mc.x_shifts_els)),
                                         np.max(np.abs(mc.y_shifts_els)))).astype(np.int)

        m_els -= np.nanmin(m_els)

        if input_params['output_bit_depth'] == 'Do not convert':
            pass
        elif input_params['output_bit_depth'] == '8':
            m_els = m_els.astype(np.uint8, copy=False)
        elif input_params['output_bit_depth'] == '16':
            m_els = m_els.astype(np.uint16)

        img_out_path = os.path.join(batch_dir, f'{UUID}_mc.tiff')
        tifffile.imsave(img_out_path, m_els, bigtiff=True, imagej=True, compress=1)

        output.update({'status': 1, 'bord_px': int(bord_px_els)})

    except Exception:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    for mf in glob(os.path.join(batch_dir, UUID + '*.mmap')):
        try:
            os.remove(mf)
        except:
            pass

    dview.terminate()

    end_time = time()
    processing_time = (end_time - start_time) / 60

    output_files_list = [UUID + '_mc.tiff']

    output.update({'processing_time': processing_time,
                   'output_files': output_files_list})

    json.dump(output, open(file_path + '.out', 'w'))


class Output:
    def __init__(self, batch_path, UUID, viewer_ref):
        vi = ViewerUtils(viewer_ref)

        if not vi.discard_workEnv():
            return

        vi.viewer.status_bar_label.showMessage('Please wait, loading motion corrected image sequence...')

        pik_path = os.path.join(batch_path, f'{UUID}_input.pik')
        tiff_path = os.path.join(batch_path, f'{UUID}_mc.tiff')

        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pik_path, tiff_path)
        #tiff_path = batch_path + '/' + str(UUID) + '_mc.tiff'
        #workEnv.imgdata.seq = tifffile.imread(tiff_path).T
        vi.update_workEnv()
        vi.viewer.status_bar_label.showMessage('Finished loading motion corrected image sequence!')

        input_params = pickle.load(
            open(
                os.path.join(batch_path, f'{UUID}.params'),
                'rb'
            )
        )

        name = input_params['item_name']
        vi.viewer.ui.label_curr_img_seq_name.setText('MotCor :' + name)

        out_file = json.load(
            open(os.path.join(batch_path, f'{UUID}.out'), 'r')
        )

        bpx = out_file['bord_px']
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

#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
