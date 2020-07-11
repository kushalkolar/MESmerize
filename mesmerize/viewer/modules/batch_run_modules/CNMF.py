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
from glob import glob
try:
    cv2.setNumThreads(1)
except:
    pass
import numpy as np
import os
from time import time
import caiman as cm
from caiman.source_extraction.cnmf import cnmf as cnmf
from caiman.utils.utils import load_dict_from_hdf5
import pickle
import traceback
import json
import logging


if not sys.argv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core import ViewerUtils, ViewerWorkEnv


def run(batch_dir: str, UUID: str):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s")
    start_time = time()

    output = {'status': 0, 'output_info': ''}
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)
    file_path = os.path.join(batch_dir, UUID)

    filename = [file_path + '_input.tiff']
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    print('*********** Creating Process Pool ***********')
    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )

    try:
        print('Creating memmap')

        memmap_fname = cm.save_memmap(
            filename,
            base_name='memmap-',
            order='C',
            border_to_0=input_params['border_pix'],
            dview=dview
        )

        Yr, dims, T = cm.load_memmap(memmap_fname)
        Y = np.reshape(Yr.T, [T] + list(dims), order='F')

        cnm = cnmf.CNMF(
            dview=dview,
            n_processes=n_processes,
            **input_params['cnmf_kwargs'],
        )

        cnm.fit(Y)

        if input_params['refit']:
            cnm = cnm.refit(Y, dview=dview)

        cnm.params.change_params(params_dict=input_params['eval_kwargs'])

        cnm.estimates.evaluate_components(
            Y,
            cnm.params,
            dview=dview
        )

        cnm.estimates.select_components(use_object=True)

        out_filename = f'{UUID}_results.hdf5'
        cnm.save(out_filename)

        output_files = [out_filename]

        output.update(
            {
                'output': UUID,
                'status': 1,
                'output_files': output_files
            }
        )

    except Exception as e:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    dview.terminate()

    for mf in glob(batch_dir + '/memmap-*'):
        try:
            os.remove(mf)
        except:
            pass

    end_time = time()
    proc_time = (end_time - start_time) / 60

    output.update({'processing_time': proc_time})

    json.dump(output, open(file_path + '.out', 'w'))


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

        roi_manager_gui = vi.viewer.parent().get_module('roi_manager')
        roi_manager_gui.start_backend('CNMFROI')

        roi_manager_gui.manager.add_all_components(
            cnmf_data,
            input_params_dict=input_params,
        )

        name = input_params['item_name']
        vi.viewer.ui.label_curr_img_seq_name.setText(f'CNMF: {name}')
        vi.viewer.workEnv.history_trace.append({'cnmf': input_params})
        vi.enable_ui(True)


#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
