#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 15 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from __future__ import division
from __future__ import print_function
from builtins import range
import sys
# sys.path.append('/home/kushal/Sars_stuff/github-repos/CaImAn/caiman')
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

if not len(sys.argv) > 1:
    from ..common import ViewerInterface
    from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv


def run(batch_dir, UUID, n_processes):
    output = {'status': 0, 'output_info': ''}
    file_path = batch_dir + '/' + UUID
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

        min_mov = cm.load(fname[0], subindices=range(200)).min()

        mc = MotionCorrect(fname[0], min_mov,
                           dview=dview, max_shifts=max_shifts, niter_rig=niter_rig,
                           splits_rig=splits_rig,
                           strides=strides, overlaps=overlaps, splits_els=splits_els,
                           upsample_factor_grid=upsample_factor_grid,
                           max_deviation_rigid=max_deviation_rigid,
                           shifts_opencv=True, nonneg_movie=True)

        mc.motion_correct_pwrigid(save_movie=True)
        m_els = cm.load(mc.fname_tot_els)
        bord_px_els = np.ceil(np.maximum(np.max(np.abs(mc.x_shifts_els)),
                                         np.max(np.abs(mc.y_shifts_els)))).astype(np.int)

        m_els -= np.nanmin(m_els)
        m_els = m_els.astype(np.uint8, copy=False)

        tifffile.imsave(batch_dir + '/' + UUID + '_mc.tiff', m_els)
        output.update({'status': 1, 'bord_px': int(bord_px_els)})

    except Exception:
        output.update({'status': 0, 'error_msg': traceback.format_exc()})

    dview.terminate()
    json.dump(output, open(file_path + '.out', 'w'))


def output(batch_path, UUID, viewer_ref):
    vi = ViewerInterface(viewer_ref)

    if not vi.VIEWER_discard_workEnv():
        return

    pik_path = batch_path + '/' + str(UUID) + '_workEnv.pik'
    workEnv = ViewerWorkEnv.from_pickle(pik_path)
    tiff_path = batch_path + '/' + str(UUID) + '_mc.tiff'
    workEnv.imgdata.seq = tifffile.imread(tiff_path).T
    viewer_ref.workEnv = workEnv

    vi.VIEWER_update_workEnv()
    vi.VIEWER_enable_ui(True)

if len(sys.argv) > 1:
    run(sys.argv[1], sys.argv[2], sys.argv[3])