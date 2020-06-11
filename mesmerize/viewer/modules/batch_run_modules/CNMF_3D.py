# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Adapted from the demo notebook from @agiovann and @epnev
"""

from ipyparallel import Client
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import psutil
from scipy.ndimage.filters import gaussian_filter
import sys

import caiman as cm
from caiman.utils.visualization import nb_view_patches3d
import caiman.source_extraction.cnmf as cnmf
from caiman.components_evaluation import evaluate_components, estimate_components_quality_auto
from caiman.cluster import setup_cluster
from caiman.paths import caiman_datadir
from caiman.utils.utils import load_dict_from_hdf5

from time import time
import pickle
import traceback
from glob import glob
import json

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s")

if not sys.argv[0] == __file__:
    from ...core import ViewerUtils, ViewerWorkEnv


def run(batch_dir: str, UUID: str):
    start_time = time()

    output = {'status': 0, 'output_info': ''}
    n_processes = int(os.environ['_MESMERIZE_N_THREADS'])

    filepath = os.path.join(batch_dir, UUID)

    imgpath = f'{filepath}_input.tiff'
    input_params = pickle.load(open(f'{filepath}.params', 'rb'))

    print('******** Creating process pool *********')
    c, dview, n_processes = setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )

    try:
        print('********** Making memmap **********')
        memmap_path = cm.save_memmap([imgpath], base_name=f'memmap_{UUID}', is_3D=True, order='C', dview=dview)

        print('********** Loading memmap **********')
        Yr, dims, T = cm.load_memmap(memmap_path)
        Y = np.reshape(Yr, dims + (T,), order='F')

        images = np.reshape(Yr.T, [T] + list(dims), order='F')

        if input_params['use_patches']:
            cnm = cnmf.CNMF(
                n_processes=n_processes,
                dview=dview,
                only_init_patch=True,
                **input_params['cnmf_kwargs']
            )

        else:
            cnm = cnmf.CNMF(
                n_processes,
                dview=dview,
                **input_params['cnmf_kwargs']
            )

        cnm.fit(images)

        print('Number of components:' + str(cnm.estimates.A.shape[-1]))

        cnm.params.change_params(
            params_dict={
                **input_params['eval_kwargs'],
                'use_cnn': False
            }
        )

        cnm.estimates.evaluate_components(images, cnm.params, dview=dview)

        print('Keeping ' + str(len(cnm.estimates.idx_components)) +
              ' and discarding  ' + str(len(cnm.estimates.idx_components_bad)))

        if input_params['refit']:
            cnm.params.set('temporal', {'p': input_params['cnmf_kwargs']['p']})
            cnm_ = cnm.refit(images)
        else:
            cnm_ = cnm

        out_filename = f'{UUID}_results.hdf5'
        cnm_.save(out_filename)

        output.update(
            {
                'output': UUID,
                'status': 1,
                'output_files': [out_filename]
            }
        )

    except Exception as e:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    cm.stop_server(dview=dview)

    for mf in glob(batch_dir + '/memmap_*'):
        os.remove(mf)

    end_time = time()
    processing_time = (end_time - start_time) / 60
    output.update({'processing_time': processing_time})

    json.dump(output, open(filepath + '.out', 'w'))


class Output:
    def __init__(self, batch_path, UUID, viewer_ref):
        vi = ViewerUtils(viewer_ref)

        if not vi.discard_workEnv():
            return

        vi.viewer.status_bar_label.showMessage('Please wait, loading image data...')

        pik_path = os.path.join(batch_path, f'{UUID}_input.pik')
        tiff_path = os.path.join(batch_path, f'{UUID}_input.tiff')
        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pik_path, tiff_path)

        vi.update_workEnv()
        vi.viewer.status_bar_label.showMessage('Finished loading image data...')

        input_params_path = os.path.join(batch_path, f'{UUID}.params')
        input_params = pickle.load(open(input_params_path, 'rb'))

        cnmf_data = load_dict_from_hdf5(
            os.path.join(batch_path, f'{UUID}_results.hdf5')
        )

        cnmA = cnmf_data['estimates']['A']
        cnmb = cnmf_data['estimates']['b']
        cnm_f = cnmf_data['estimates']['f']
        cnmC = cnmf_data['estimates']['C']
        cnmYrA = cnmf_data['estimates']['YrA']
        idx_components = cnmf_data['estimates']['idx_components']
        dims = cnmf_data['dims']

        roi_manager_gui = vi.viewer.parent().get_module('roi_manager')
        roi_manager_gui.start_scatter_mode('VolCNMF')

        roi_manager_gui.manager.add_all_components(
            cnmA=cnmA,
            cnmb=cnmb,
            cnmC=cnmC,
            cnm_f=cnm_f,
            cnmYrA=cnmYrA,
            dims=dims,
            input_params_dict=input_params,
        )

        name = input_params['item_name']
        vi.viewer.ui.label_curr_img_seq_name.setText('cnmf_3D:' + name)
        vi.viewer.workEnv.history_trace.append({'cnmf_3d': input_params})
        vi.enable_ui(True)


if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2])
