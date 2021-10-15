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
import numpy as np
import os
from scipy.ndimage.filters import gaussian_filter
import sys

import caiman as cm
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
import shutil

# must be within this block, else windows gives issues
if __name__ == '__main__':
    from mesmerize.common.utils import HdfTools


if not sys.argv[0] == __file__:
    from ...core import ViewerUtils, ViewerWorkEnv


def run(work_dir: str, UUID: str, save_temp_files: str):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s")

    start_time = time()

    batch_dir = os.environ['CURR_BATCH_DIR']
    save_temp_files = bool(int(save_temp_files))

    output = {'status': 0, 'output_info': ''}
    n_processes = int(os.environ['_MESMERIZE_N_THREADS'])

    filepath = os.path.join(work_dir, UUID)

    imgpath = f'{filepath}_input.tiff'
    input_params = pickle.load(open(f'{filepath}.params', 'rb'))

    print('******** Creating process pool *********')
    c, dview, n_processes = setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )

    try:
        if input_params['use_memmap']:
            memmap_uuid = input_params['memmap_uuid']

            memmap_batchdir = glob(os.path.join(batch_dir, f'memmap-{memmap_uuid}*.mmap'))

            # Check batch dir
            if len(memmap_batchdir) > 0:
                memmap_path = memmap_batchdir[0]
                print(f'********** Found existing memmap in batch dir: {memmap_path} ********** ')

                # copy to work dir
                if not os.path.samefile(batch_dir, work_dir):
                    print('**** Copying memmap to work dir ****')
                    shutil.copy(memmap_path, work_dir)
                    memmap_path = glob(os.path.join(work_dir, f'memmap-{memmap_uuid}*.mmap'))[0]

            else:
                # remake the memmap with the same UUID so that future batch items can rely on it
                print('********** Memmap not found, re-making memmap with the same UUID **********')
                memmap_path = cm.save_memmap(
                    [imgpath], base_name=f'memmap-{memmap_uuid}', is_3D=True, order='C', dview=dview
                )

        else:
            print('********** Making memmap **********')
            memmap_path = cm.save_memmap(
                [imgpath], base_name=f'memmap-{UUID}', is_3D=True, order='C', dview=dview
            )

        print(f'Using memmap:\n{memmap_path}')

        print('********** Loading memmap **********')
        Yr, dims, T = cm.load_memmap(memmap_path)
        Y = np.reshape(Yr, dims + (T,), order='F')

        images = np.reshape(Yr.T, [T] + list(dims), order='F')

        Ain = None

        # seed components
        if 'use_seeds' in input_params.keys():
            if input_params['use_seeds']:
                try:
                    # see if it's an h5 file produced by the nuset_segment GUI
                    hdict = HdfTools.load_dict(
                        os.path.join(f'{filepath}.ain'),
                        'data'
                    )
                    Ain = hdict['sparse_mask']
                except:
                    try:
                        Ain = np.load(f'{UUID}.ain')
                    except Exception as e:
                        output['warnings'] = f'Could not seed components, make sure that ' \
                            f'the .ain file exists in the batch dir: {e}'

        if input_params['use_patches']:
            cnm = cnmf.CNMF(
                n_processes=n_processes,
                dview=dview,
                only_init_patch=True,
                Ain=Ain,
                **input_params['cnmf_kwargs']
            )

        else:
            cnm = cnmf.CNMF(
                n_processes,
                dview=dview,
                Ain=Ain,
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

        if input_params['refit']:
            cnm.params.set('temporal', {'p': input_params['cnmf_kwargs']['p']})
            cnm_ = cnm.refit(images)
        else:
            cnm_ = cnm

        out_filename = f'{UUID}_results.hdf5'
        cnm_.save(out_filename)

        output_files = [out_filename]

        # Save the memmap
        if save_temp_files:
            print("***** Keeping memmap file *****")

            # copy to batch dir if batch_dir != work_dir
            if not os.path.samefile(batch_dir, work_dir):
                print("***** Copying memmap file to batch dir *****")
                shutil.copy(memmap_path, batch_dir)

        # Delete the memmap from the work dir
        if not os.path.samefile(batch_dir, work_dir):
            print("***** Deleting memmap files from work dir *****")
            try:
                os.remove(memmap_path)
            except:
                pass

        output.update(
            {
                'output': UUID,
                'status': 1,
                'output_files': output_files,
                'saved_memmap': save_temp_files
            }
        )

    except Exception as e:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    cm.stop_server(dview=dview)

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

        roi_manager_gui = vi.viewer.parent().get_module('roi_manager')
        roi_manager_gui.start_backend('VolCNMF')

        roi_manager_gui.manager.add_all_components(
            cnmf_data,
            input_params_dict=input_params,
        )

        name = input_params['item_name']
        vi.viewer.ui.label_curr_img_seq_name.setText(f'CNMF 3D: {name}')
        vi.viewer.workEnv.history_trace.append({'cnmf_3d': input_params})
        vi.enable_ui(True)


#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(*sys.argv[1:])
