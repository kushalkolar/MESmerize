# -*- coding: utf-8 -*-
"""
Created on April 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Adapted from @agiovann and @epnev
"""

from __future__ import division
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import json

import numpy as np
from matplotlib.widgets import Slider
from caiman.utils import visualization

import os
import pickle
from glob import glob
from functools import partial
import traceback
from time import time, sleep
import logging
import caiman as cm
from caiman.source_extraction import cnmf
from caiman.utils.utils import load_dict_from_hdf5
from caiman.source_extraction.cnmf.params import CNMFParams

import cv2
try:
    cv2.setNumThreads(0)
except:
    pass


if not sys.argv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core import ViewerUtils, ViewerWorkEnv
    from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget


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

    # If Ain is specified
    if input_params['do_cnmfe']:
        Ain = None
        item_uuid = input_params['cnmfe_kwargs'].pop('Ain')

        if item_uuid:
            print('>> Ain specified, looking for cnm-A file <<')
            parent_batch_dir = os.environ['CURR_BATCH_DIR']
            item_out_file = os.path.join(parent_batch_dir, f'{item_uuid}.out')
            t0 = time()
            timeout = 60
            while not os.path.isfile(item_out_file):
                print('>>> cnm-A not found, waiting for 15 seconds <<<')
                sleep(15)
                if time() - t0 > timeout:
                    output.update({'status': 0, 'output_info': 'Timeout exceeding in waiting for Ain input file'})
                    raise TimeoutError('Timeout exceeding in waiting for Ain input file')

            if os.path.isfile(item_out_file):
                if json.load(open(item_out_file, 'r'))['status']:
                    Ain_path = os.path.join(parent_batch_dir, item_uuid + '_results.hdf5')
                    Ain = load_dict_from_hdf5(Ain_path)['estimates']['A']
                    print('>>> Found Ain file <<<')
                else:
                    raise FileNotFoundError('>>> Could not find specified Ain file <<<')

    print('*********** Creating Process Pool ***********')

    c, dview, n_processes = cm.cluster.setup_cluster(
        backend='local',
        n_processes=n_processes,
        single_thread=False,
        ignore_preexisting=True
    )

    try:
        print('Creating memmap')

        memmap_path = cm.save_memmap(
            filename,
            base_name=f'memmap-{UUID}',
            order='C',
            dview=dview,
            border_to_0=input_params['border_pix'],
        )

        Yr, dims, T = cm.load_memmap(memmap_path)
        Y = Yr.T.reshape((T,) + dims, order='F')

        if input_params['do_cnmfe']:
            gSig = input_params['cnmfe_kwargs']['gSig'][0]
        else:
            gSig = input_params['corr_pnr_kwargs']['gSig']

        cn_filter, pnr = cm.summary_images.correlation_pnr(
            Y, swap_dim=False, gSig=gSig
        )

        if not input_params['do_cnmfe'] and input_params['do_corr_pnr']:
            pickle.dump(cn_filter, open(UUID + '_cn_filter.pikl', 'wb'), protocol=4)
            pickle.dump(pnr, open(UUID + '_pnr.pikl', 'wb'), protocol=4)

            output_file_list = \
                [
                    UUID + '_pnr.pikl',
                    UUID + '_cn_filter.pikl',
                ]

            output.update(
                {
                    'output': UUID,
                    'status': 1,
                    'output_info': 'inspect correlation & pnr',
                    'output_files': output_file_list
                }
            )

            dview.terminate()

            for mf in glob(batch_dir + '/memmap-*'):
                os.remove(mf)

            end_time = time()
            processing_time = (end_time - start_time) / 60
            output.update({'processing_time': processing_time})

            json.dump(output, open(file_path + '.out', 'w'))

            return

        cnmf_params_dict = \
            {
                "method_init": 'corr_pnr',
                "n_processes": n_processes,
                "only_init_patch": True,  # for 1p
                "center_psf": True,  # for 1p
                "normalize_init": False,  # for 1p
            }
        cnmf_params_dict.update(**input_params['cnmfe_kwargs'])

        cnm = cnmf.CNMF(
            n_processes=n_processes,
            dview=dview,
            Ain=Ain,
            params=CNMFParams(params_dict=cnmf_params_dict),
        )

        cnm.fit(Y)

        #  DISCARD LOW QUALITY COMPONENTS
        cnm.params.set(
            'quality',
            {
                'use_cnn': False,
                **input_params['eval_kwargs']
            }
        )

        cnm.estimates.evaluate_components(Y, cnm.params, dview=dview)

        out_filename = f'{UUID}_results.hdf5'
        cnm.save(out_filename)

        pickle.dump(pnr, open(UUID + '_pnr.pikl', 'wb'), protocol=4)
        pickle.dump(cn_filter, open(UUID + '_cn_filter.pikl', 'wb'), protocol=4)

        output.update(
            {
                'output': filename[:-5],
                'status': 1,
                'output_files': [
                    out_filename,
                    UUID + '_pnr.pikl',
                    UUID + '_cn_filter.pikl',
                ]

            }
        )

    except Exception as e:
        output.update({'status': 0, 'Y.shape': Y.shape, 'output_info': traceback.format_exc()})

    dview.terminate()

    for mf in glob(batch_dir + '/memmap-*'):
        try:
            os.remove(mf)
        except: # Windows doesn't like removing the memmaps
            pass

    end_time = time()
    processing_time = (end_time - start_time) / 60
    output.update({'processing_time': processing_time})

    json.dump(output, open(file_path + '.out', 'w'))


class Output(QtWidgets.QWidget):
    def __init__(self, batch_dir, UUID, viewer_ref):
        # super(Output, self).__init__(self)
        # QtWidgets.QWidget.__init__(self, parent=None)
        self.batch_dir = batch_dir
        self.UUID = UUID
        self.viewer_ref = viewer_ref
        self.cnmfe_results = {}

        visualization.mpl.use('TkAgg')

        filename = os.path.join(batch_dir, str(UUID))

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
            layout.addWidget(self.btnCP)

            self.btnImportIntoViewer = QtWidgets.QPushButton()
            self.btnImportIntoViewer.setText('Import CNMFE output into chosen Viewer')
            layout.addWidget(self.btnImportIntoViewer)

            self.checkbox_calc_raw_min_max = QtWidgets.QCheckBox()
            self.checkbox_calc_raw_min_max.setText('Calculate raw min and max of components')
            self.checkbox_calc_raw_min_max.setChecked(True)
            layout.addWidget(self.checkbox_calc_raw_min_max)

            self.setLayout(layout)

            self.btnCP.clicked.connect(self.output_corr_pnr)
            self.btnImportIntoViewer.clicked.connect(self.import_cnmfe_into_viewer)
            self.show()

    def output_corr_pnr(self):  # , batch_dir, UUID, viewer_ref):
        filename = os.path.join(self.batch_dir, str(self.UUID))

        cn_filter = pickle.load(open(filename + '_cn_filter.pikl', 'rb'))
        # try:
        pnr = pickle.load(open(filename + '_pnr.pikl', 'rb'))
        # except:
        #     try:
        #         pnr = pickle.load(open(filename + 'pnr.pikl', 'rb'))
            # except:
            #     return

        correlation_image_pnr = cn_filter
        pnr_image = pnr
        self.mw = MatplotlibWidget()
        # fig = mw.getFigure()
        self.mw.setWindowTitle(str(self.UUID))
        #Adapted from CaImAn library's visualization module
        # mw.plot = plt.figure(figsize=(10,4))
        # fig = pl.figure(figsize=(10, 4))
        self.cn_ax = self.mw.fig.add_axes([0.05, 0.2, 0.4, 0.7])
        self.cn_img = self.cn_ax.imshow(cn_filter, cmap='jet')
        # im_cn = plt.imshow(correlation_image_pnr, cmap='jet')
        # plt.title('correlation image')
        # self.cn_ax.colorbar()
        self.pn_ax = self.mw.fig.add_axes([0.5, 0.2, 0.4, 0.7])
        self.pn_img = self.pn_ax.imshow(pnr, cmap='jet')
        # im_pnr = plt.imshow(pnr_image, cmap='jet')
        # plt.title('PNR')
        # plt.colorbar()
        #
        s_cn_max_ax = self.mw.fig.add_axes([0.05, 0.01, 0.35, 0.03])
        s_cn_max = Slider(s_cn_max_ax, 'vmax',
                          correlation_image_pnr.min(), correlation_image_pnr.max(), valinit=correlation_image_pnr.max())

        s_cn_min_ax = self.mw.fig.add_axes([0.05, 0.07, 0.35, 0.03])
        s_cn_min = Slider(s_cn_min_ax, 'vmin',
                          correlation_image_pnr.min(), correlation_image_pnr.max(), valinit=correlation_image_pnr.min())

        s_pnr_max_ax = self.mw.fig.add_axes([0.5, 0.01, 0.35, 0.03])
        s_pnr_max = Slider(s_pnr_max_ax, 'vmax',
                           pnr_image.min(), pnr_image.max(), valinit=pnr_image.max())
        s_pnr_min_ax = self.mw.fig.add_axes([0.5, 0.07, 0.35, 0.03])
        s_pnr_min = Slider(s_pnr_min_ax, 'vmin',
                           pnr_image.min(), pnr_image.max(), valinit=pnr_image.min())
        #
        def update(val):
            self.cn_img.set_clim([s_cn_min.val, s_cn_max.val])
            self.pn_img.set_clim([s_pnr_min.val, s_pnr_max.val])
            self.mw.canvas.draw_idle()
        #
        s_cn_max.on_changed(update)
        s_cn_min.on_changed(update)
        s_pnr_max.on_changed(update)
        s_pnr_min.on_changed(update)
        # plt.ion()
        self.mw.show()
        # plt.show()

    def import_cnmfe_into_viewer(self):
        vi = ViewerUtils(self.viewer_ref)

        if not vi.discard_workEnv():
            return

        cnmf_data = load_dict_from_hdf5(
            os.path.join(self.batch_dir, f'{self.UUID}_results.hdf5')
        )

        vi.viewer.status_bar_label.showMessage('Loading CNMFE data, please wait...')
        pickle_file_path = os.path.join(self.batch_dir, f'{self.UUID}_input.pik')
        tiff_path = os.path.join(self.batch_dir, f'{self.UUID}_input.tiff')

        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path, tiff_path)
        vi.update_workEnv()

        input_params = pickle.load(
            open(
                os.path.join(self.batch_dir, f'{self.UUID}.params'),
                'rb'
            )
        )

        vi.viewer.workEnv.history_trace.append({'cnmfe': input_params})

        roi_manager_gui = vi.viewer.parent().get_module('roi_manager')
        roi_manager_gui.start_backend('CNMFROI')

        roi_manager_gui.manager.add_all_components(
            cnmf_data,
            input_params_dict=input_params,
            calc_raw_min_max=self.checkbox_calc_raw_min_max.isChecked()
        )

        vi.viewer.ui.label_curr_img_seq_name.setText('CNMFE of: ' + input_params['item_name'])
        self.close()


#if sys.argv[0] == __file__:
if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
