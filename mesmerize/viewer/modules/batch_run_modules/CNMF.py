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
from caiman.source_extraction.cnmf.params import CNMFParams
import pickle
import traceback
import json
import logging
import tifffile

# must be within this block, else windows gives issues
if __name__ == '__main__':
    from mesmerize.common.utils import HdfTools

if not sys.argv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core import ViewerUtils, ViewerWorkEnv


def run(batch_dir: str, UUID: str):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                        format="%(relativeCreated)12d [%(filename)s:%(funcName)20s():%(lineno)s] [%(process)d] %(message)s")
    start_time = time()

    output = {'status': 0, 'output_info': ''}

    file_path = os.path.join(batch_dir, UUID)
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    try:
        if 'is_3d' in input_params.keys():
            if input_params['is_3d']:
                run_multi(batch_dir, UUID, output)
            else:
                run_single(batch_dir, UUID, output)
        else:
            run_single(batch_dir, UUID, output)

    except Exception as e:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    for mf in glob(os.path.join(batch_dir, f'memmap-{UUID}*')):
        try:
            os.remove(mf)
        except:
            pass

    end_time = time()
    proc_time = (end_time - start_time) / 60

    output.update({'processing_time': proc_time})

    json.dump(output, open(file_path + '.out', 'w'))


def run_single(batch_dir, UUID, output):
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)
    file_path = os.path.join(batch_dir, UUID)

    filename = [file_path + '_input.tiff']
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    print('*********** Creating Process Pool ***********')
    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )

    memmap_fname = cm.save_memmap(
        filename,
        base_name=f'memmap-{UUID}',
        order='C',
        border_to_0=input_params['border_pix'],
        dview=dview
    )

    Yr, dims, T = cm.load_memmap(memmap_fname)
    Y = np.reshape(Yr.T, [T] + list(dims), order='F')

    Ain = None

    # seed components
    if 'use_seeds' in input_params.keys():
        if input_params['use_seeds']:
            try:
                # see if it's an h5 file produced by the nuset_segment GUI
                hdict = HdfTools.load_dict(
                    os.path.join(f'{file_path}.ain'),
                    'data'
                )
                Ain = hdict['sparse_mask']
            except:
                try:
                    Ain = np.load(f'{file_path}.ain')
                except Exception as e:
                    output['warnings'] = f'Could not seed components, make sure that ' \
                        f'the .ain file exists in the batch dir: {e}'

    # seeded
    if Ain is not None:
        input_params['cnmf_kwargs'].update(
            {
                'only_init': False,
                'rf': None
            }
        )

    cnmf_params = CNMFParams(params_dict=input_params['cnmf_kwargs'])

    cnm = cnmf.CNMF(
        dview=dview,
        n_processes=n_processes,
        Ain=Ain,
        params=cnmf_params,
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

    dview.terminate()

    return output


def run_multi(batch_dir, UUID, output):
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)
    file_path = os.path.join(batch_dir, UUID)

    filename = [file_path + '_input.tiff']
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    seq = tifffile.TiffFile(filename[0]).asarray()
    seq_shape = seq.shape

    # assume default tzxy
    for z in range(seq.shape[1]):
        tifffile.imsave(f'{file_path}_z{z}.tiff', seq[:, z, :, :])

    del seq

    print('*********** Creating Process Pool ***********')
    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local', n_processes=n_processes, single_thread=False, ignore_preexisting=True
    )
    num_components = 0
    output_files = []
    for z in range(seq_shape[1]):
        print(f"Plane {z} / {seq_shape[1]}")
        filename = [f'{file_path}_z{z}.tiff']
        print('Creating memmap')

        memmap_fname = cm.save_memmap(
            filename,
            base_name=f'memmap-{UUID}',
            order='C',
            border_to_0=input_params['border_pix'],
            dview=dview
        )

        Yr, dims, T = cm.load_memmap(memmap_fname)
        Y = np.reshape(Yr.T, [T] + list(dims), order='F')

        Ain = None

        # seed components
        # see if it's an h5 file produced by the nuset_segment GUI
        try:
            hdict = HdfTools.load_dict(os.path.join(f'{file_path}.ain'), 'data')
            Ain = hdict[f'sparse_mask'][str(z)]
        except Exception as e:
            output['warnings'] = f'Could not seed components, make sure that ' \
                f'the .ain file exists in the batch dir: {e}'

        #print(Ain)
        #raise Exception

        # seeded
        if Ain is not None:
            input_params['cnmf_kwargs'].update(
                {
                    'only_init': False,
                    'rf': None
                }
            )

        cnmf_params = CNMFParams(params_dict=input_params['cnmf_kwargs'])

        cnm = cnmf.CNMF(
            dview=dview,
            n_processes=n_processes,
            Ain=Ain,
            params=cnmf_params,
        )

        cnm.fit(Y)

        if input_params['refit']:
            cnm = cnm.refit(Y, dview=dview)

        cnm.params.set('quality', input_params['eval_kwargs'])

        cnm.estimates.evaluate_components(
            Y,
            cnm.params,
            dview=dview
        )

        cnm.estimates.select_components(use_object=True)

        num_components += len(cnm.estimates.C)

        out_filename = f'{UUID}_results_z{z}.hdf5'
        cnm.save(out_filename)

        output_files.append(out_filename)

        os.remove(filename[0])

    output.update(
        {
            'output': UUID,
            'status': 1,
            'output_files': output_files,
            'num_components': num_components
        }
    )

    dview.terminate()

    return output


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

        if input_params['is_3d']:
            roi_manager_gui = vi.viewer.parent().get_module('roi_manager')
            manager = roi_manager_gui.start_backend('VolMultiCNMFROI')

            cnmf_data_dicts = \
                [
                    load_dict_from_hdf5(
                        os.path.join(batch_path, f'{UUID}_results_z{z}.hdf5')
                    )
                    # for z in range(5)
                    for z in range(vi.viewer.workEnv.imgdata.z_max + 1)
                ]

            manager.add_all_components(
                cnmf_data_dicts,
                input_params
            )
        else:
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
