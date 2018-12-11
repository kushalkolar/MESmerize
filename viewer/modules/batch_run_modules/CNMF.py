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
    print('Open CV is naturally single threaded')
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
import traceback
import json
from PyQt5 import QtCore, QtGui, QtWidgets

if not sys.argv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core.common import ViewerInterface, ViewerWorkEnv


def run(batch_dir, UUID, n_processes):

    output = {'status': 0, 'output_info': ''}
    n_processes = int(n_processes)
    file_path = batch_dir + '/' + UUID

    filename = [file_path + '.tiff']
    input_params = pickle.load(open(file_path + '.params', 'rb'))

    fr = input_params['fr']
    p = input_params['p']
    gnb = input_params['gnb']
    merge_thresh = input_params['merge_thresh']
    rf = input_params['rf']
    stride_cnmf = input_params['stride_cnmf']
    K = input_params['k']
    gSig = input_params['gSig']
    gSig = [gSig, gSig]
    min_SNR = input_params['min_SNR']
    rval_thr = input_params['rval_thr']
    cnn_thr = input_params['cnn_thr']
    decay_time = input_params['decay_time']
    frames_window = input_params['frames_window']
    quantileMin = input_params['quantileMin']

    print('*********** Creating Process Pool ***********')
    c, dview, np = cm.cluster.setup_cluster(backend='local', n_processes=n_processes, single_thread=False)

    try:

        print('Creating memmap')
        fname_new = cm.save_memmap_each(
            filename,
            base_name='memmap_' + UUID,
            order='C',
            border_to_0=7,
            dview=dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_' + UUID, dview=dview)

        Yr, dims, T = cm.load_memmap(fname_new)
        Y = Yr.T.reshape((T,) + dims, order='F')

        cnm = cnmf.CNMF(n_processes=n_processes, k=K, gSig=gSig, merge_thresh=merge_thresh,
                        p=0, dview=dview, rf=rf, stride=stride_cnmf, memory_fact=1,
                        method_init='greedy_roi', alpha_snmf=None,
                        only_init_patch=False, gnb=gnb, border_pix=7)
        cnm.fit(Y)

        idx_components, idx_components_bad, SNR_comp, r_values, cnn_preds = \
            estimate_components_quality_auto(Y, cnm.A, cnm.C, cnm.b, cnm.f,
                                             cnm.YrA, fr, decay_time, gSig, dims,
                                             dview=dview, min_SNR=min_SNR,
                                             r_values_min=rval_thr, use_cnn=False,
                                             thresh_cnn_lowest=cnn_thr)
        A_in, C_in, b_in, f_in = cnm.A[:,
                                 idx_components], cnm.C[idx_components], cnm.b, cnm.f
        cnm2 = cnmf.CNMF(n_processes=n_processes, k=A_in.shape[-1], gSig=gSig, p=p, dview=dview,
                         merge_thresh=merge_thresh, Ain=A_in, Cin=C_in, b_in=b_in,
                         f_in=f_in, rf=None, stride=None, gnb=gnb,
                         method_deconvolution='oasis', check_nan=True)

        cnm2 = cnm2.fit(Y)

        F_dff = detrend_df_f(cnm2.A, cnm2.b, cnm2.C, cnm2.f, YrA=cnm2.YrA,
                             quantileMin=quantileMin, frames_window=frames_window)


        pickle.dump(Yr, open(UUID + '_Yr.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.A, open(UUID + '_cnm-A.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.b, open(UUID + '_cnm-b.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.C, open(UUID + '_cnm-C.pikl', 'wb'), protocol=4)
        pickle.dump(F_dff, open(UUID + '_F_dff.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.f, open(UUID + '_cnm-f.pikl', 'wb'), protocol=4)
        pickle.dump(idx_components, open(UUID + '_idx_components.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.YrA, open(UUID  + '_cnm-YrA.pikl', 'wb'), protocol=4)
        pickle.dump(dims, open(UUID  + '_dims.pikl', 'wb'), protocol=4)
        output.update({'output': UUID, 'status': 1})
    except Exception:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    dview.terminate()

    for mf in glob(batch_dir + '/memmap_*'):
        os.remove(mf)

    json.dump(output, open(file_path + '.out', 'w'))


class Output(QtWidgets.QWidget):
    def __init__(self, batch_dir, UUID, viewer_ref):
        # super(Output, self).__init__()
        self.batch_dir = batch_dir
        self.UUID = UUID
        self.viewer_ref = viewer_ref
        self.cnmfe_results = {}

        filename = batch_dir + '/' + str(UUID)
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('CNMF visualization or Import?')
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel(self)
        label.setText('Would you like to use the CaImAn visualization or import components into the viewer?')
        layout.addWidget(label)

        self.btnCNMF = QtWidgets.QPushButton()
        self.btnCNMF.setText('CaImAn CNMF visualization')
        layout.addWidget(self.btnCNMF)

        self.btnImportIntoViewer = QtWidgets.QPushButton()
        self.btnImportIntoViewer.setText('Import CNMF output into chosen Viewer')
        layout.addWidget(self.btnImportIntoViewer)

        self.setLayout(layout)

        self.btnCNMF.clicked.connect(self.output_cnmf)
        self.btnImportIntoViewer.clicked.connect(self.import_cnmf_into_viewer)
        self.show()

    def get_cnmf_results(self):
        filename = self.batch_dir + '/' + str(self.UUID)

        self.cnmA = pickle.load(open(filename + '_cnm-A.pikl', 'rb'))
        self.cnmC = pickle.load(open(filename + '_cnm-C.pikl', 'rb'))
        self.F_dff = pickle.load(open(filename + '_F_dff.pikl', 'rb'))
        self.idx_components = pickle.load(open(filename + '_idx_components.pikl', 'rb'))
        self.dims = pickle.load(open(filename + '_dims.pikl', 'rb'))

    def output_cnmf(self):  # , batch_dir, UUID, viewer_ref):
        pass
        filename = self.batch_dir + '/' + str(self.UUID)

        self.get_cnmf_results()

        Yr = pickle.load(open(filename + '_Yr.pikl', 'rb'))

        cnmb = pickle.load(open(filename + '_cnm-b.pikl', 'rb'))
        cnm_f = pickle.load(open(filename + '_cnm-f.pikl', 'rb'))
        cnmYrA = pickle.load(open(filename + '_cnm-YrA.pikl', 'rb'))

        img = tifffile.imread(self.batch_dir + '/' + str(self.UUID) + '.tiff')
        Cn = cm.local_correlations(img.transpose(1, 2, 0))
        Cn[np.isnan(Cn)] = 0

        self.visualization = cm.utils.visualization.view_patches_bar(Yr, self.cnmA[:, self.idx_components],
                                                                     self.cnmC[self.idx_components], cnmb, cnm_f,
                                                                     self.dims[0], self.dims[1],
                                                                     YrA=cnmYrA[self.idx_components], img=Cn)

    def import_cnmf_into_viewer(self):
        self.get_cnmf_results()

        vi = ViewerInterface(self.viewer_ref)

        if not vi.discard_workEnv():
            return

        vi.viewer.status_bar_label.showMessage('Loading CNMFE data, please wait...')
        pickle_file_path = self.batch_dir + '/' + str(self.UUID) + '_workEnv.pik'
        tiff_path = self.batch_dir + '/' + str(self.UUID) + '.tiff'

        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path, tiff_path)
        vi.update_workEnv()

        input_params = pickle.load(open(self.batch_dir + '/' + str(self.UUID) + '.params', 'rb'))

        self.viewer_ref.parent().ui.actionROI_Manager.trigger()

        for m in self.viewer_ref.parent().running_modules:
            if isinstance(m, ModuleGUI):
                m.start_cnmfe_mode()
                m.add_all_cnmfe_components(cnmA=self.cnmA,
                                           cnmC=self.F_dff,
                                           idx_components=self.idx_components,
                                           dims=self.dims,
                                           input_params_dict=input_params,
                                           dfof=True)

        if 'name_cnmf' in input_params.keys():
            vi.viewer.ui.label_curr_img_seq_name.setText(input_params['name_cnmf'])

if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2], sys.argv[3])
