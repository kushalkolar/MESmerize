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
# from ..common import ViewerInterface, BatchRunInterface
# from MesmerizeCore.packager import viewerWorkEnv as ViewerWorkEnv
# from MesmerizeCore import configuration
# from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
# if not len(sys.argv) > 1:
#     from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
# from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import json
import caiman as cm

from builtins import zip
from builtins import str
from builtins import map
from builtins import range
from past.utils import old_div
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from caiman.source_extraction import cnmf
from caiman.utils.utils import download_demo
from caiman.utils import visualization
from caiman.components_evaluation import estimate_components_quality_auto
import os
import pickle
from glob import glob
from functools import partial
import traceback
from time import time


if not sys.argv[0] == __file__:
    from ..roi_manager import ModuleGUI
    from ...core.common import ViewerInterface, ViewerWorkEnv
    from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget


def run(batch_dir: str, UUID: str):
    start_time = time()

    output = {'status': 0, 'output_info': ''}
    n_processes = os.environ['_MESMERIZE_N_THREADS']
    n_processes = int(n_processes)
    file_path = batch_dir + '/' + UUID

    filename = file_path + '.tiff'
    input_params = pickle.load(open(file_path + '.params', 'rb'))

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

    print('*********** Creating Process Pool ***********')

    c, dview, n_processes = cm.cluster.setup_cluster(backend='local',  # use this one
                                                     n_processes=n_processes,
                                                     single_thread=False)
    if 'bord_px' in input_params.keys():
        bord_px = input_params['bord_px']
    else:
        bord_px = 6

    try:
        print('Creating memmap')
        fname_new = cm.save_memmap_each(
            filename,
            base_name='memmap_' + UUID,
            order='C',
            border_to_0=bord_px,
            dview=dview)
        fname_new = cm.save_memmap_join(fname_new, base_name='memmap_' + UUID, dview=dview)
        # load memory mappable file
        Yr, dims, T = cm.load_memmap(fname_new)
        Y = Yr.T.reshape((T,) + dims, order='F')
        # compute some summary images (correlation and peak to noise)
        # change swap dim if output looks weird, it is a problem with tiffile
        cn_filter, pnr = cm.summary_images.correlation_pnr(
            Y, gSig=gSig, swap_dim=False)
        if not input_params['do_cnmfe'] and input_params['do_corr_pnr']:
            pickle.dump(cn_filter, open(UUID + '_cn_filter.pikl', 'wb'), protocol=4)
            pickle.dump(pnr, open(UUID + '_pnr.pikl', 'wb'), protocol=4)

            output_file_list = [UUID + '_pnr.pikl',
                                UUID + '_cn_filter.pikl',
                                UUID + '_dims.pikl',
                                UUID + '.out'
                                ]

            output.update({'output': UUID,
                           'status': 1,
                           'output_info': 'inspect correlation & pnr',
                           'output_files': output_file_list
                           })

            dview.terminate()

            for mf in glob(batch_dir + '/memmap_*'):
                os.remove(mf)

            end_time = time()
            processing_time = (end_time - start_time) / 60
            output.update({'processing_time': processing_time})

            json.dump(output, open(file_path + '.out', 'w'))

            return

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
        cnm.fit(Y)

        #  DISCARD LOW QUALITY COMPONENTS
        idx_components, idx_components_bad, comp_SNR, r_values, pred_CNN = estimate_components_quality_auto(
            Y, cnm.A, cnm.C, cnm.b, cnm.f, cnm.YrA, frate,
            decay_time, gSig, dims, dview=dview,
            min_SNR=min_SNR, r_values_min=r_values_min, use_cnn=False)

        # np.save(filename[:-5] + '_curves.npy', cnm.C)
        pickle.dump(Yr, open(UUID + '_Yr.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.A, open(UUID + '_cnm-A.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.b, open(UUID + '_cnm-b.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.C, open(UUID + '_cnm-C.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.f, open(UUID + '_cnm-f.pikl', 'wb'), protocol=4)
        pickle.dump(idx_components, open(UUID + '_idx_components.pikl', 'wb'), protocol=4)
        pickle.dump(cnm.YrA, open(UUID + '_cnm-YrA.pikl', 'wb'), protocol=4)
        pickle.dump(pnr, open(UUID + '_pnr.pikl', 'wb'), protocol=4)
        pickle.dump(cn_filter, open(UUID + '_cn_filter.pikl', 'wb'), protocol=4)
        pickle.dump(dims, open(UUID + '_dims.pikl', 'wb'), protocol=4)

        output_file_list = [UUID + '_Yr.pikl',
                            UUID + '_cnm-A.pikl',
                            UUID + '_cnm-b.pikl',
                            UUID + '_cnm-C.pikl',
                            UUID + '_cnm-f.pikl',
                            UUID + '_idx_components.pikl',
                            UUID + '_cnm-YrA.pikl',
                            UUID + '_pnr.pikl',
                            UUID + '_cn_filter.pikl',
                            UUID + '_dims.pikl',
                            UUID + '.out'
                            ]
        output.update({'output': filename[:-5],
                       'status': 1,
                       'output_files': output_file_list
                       })

    except Exception as e:
        output.update({'status': 0, 'output_info': traceback.format_exc()})

    dview.terminate()

    for mf in glob(batch_dir + '/memmap_*'):
        os.remove(mf)

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

        filename = batch_dir + '/' + str(UUID)
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

            self.btnCNMFE = QtWidgets.QPushButton()
            self.btnCNMFE.setText('CaImAn CNMFE visualization')
            layout.addWidget(self.btnCNMFE)

            self.btnImportIntoViewer = QtWidgets.QPushButton()
            self.btnImportIntoViewer.setText('Import CNMFE output into chosen Viewer')
            layout.addWidget(self.btnImportIntoViewer)

            self.setLayout(layout)

            self.btnCP.clicked.connect(self.output_corr_pnr)
            self.btnCNMFE.clicked.connect(self.output_cnmfe)
            self.btnImportIntoViewer.clicked.connect(self.import_cnmfe_into_viewer)
            self.show()

    def output_corr_pnr(self):  # , batch_dir, UUID, viewer_ref):
        filename = self.batch_dir + '/' + str(self.UUID)
        print(self.batch_dir)
        print(str(self.UUID))
        print(filename)
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

        # visualization.inspect_correlation_pnr(cn_filter, pnr)

    def get_cnmfe_results(self):
        filename = self.batch_dir + '/' + str(self.UUID)

        self.cnmA = pickle.load(open(filename + '_cnm-A.pikl', 'rb'))
        self.cnmb = pickle.load(open(filename + '_cnm-b.pikl', 'rb'))
        self.cnm_f = cnm_f = pickle.load(open(filename + '_cnm-f.pikl', 'rb'))
        self.cnmC = pickle.load(open(filename + '_cnm-C.pikl', 'rb'))
        self.cnmYrA = pickle.load(open(filename + '_cnm-YrA.pikl', 'rb'))
        self.idx_components = pickle.load(open(filename + '_idx_components.pikl', 'rb'))
        self.dims = pickle.load(open(filename + '_dims.pikl', 'rb'))

    def output_cnmfe(self):  # , batch_dir, UUID, viewer_ref):
        filename = self.batch_dir + '/' + str(self.UUID)

        self.get_cnmfe_results()

        Yr = pickle.load(open(filename + '_Yr.pikl', 'rb'))

        cnmb = pickle.load(open(filename + '_cnm-b.pikl', 'rb'))
        cnm_f = pickle.load(open(filename + '_cnm-f.pikl', 'rb'))
        cnmYrA = pickle.load(open(filename + '_cnm-YrA.pikl', 'rb'))
        cn_filter = pickle.load(open(filename + '_cn_filter.pikl', 'rb'))
        self.visualization = cm.utils.visualization.view_patches_bar(Yr, self.cnmA[:, self.idx_components],
                                                                     self.cnmC[self.idx_components], cnmb, cnm_f,
                                                                     self.dims[0], self.dims[1],
                                                                     YrA=cnmYrA[self.idx_components], img=cn_filter)
        #self.hide()

    def import_cnmfe_into_viewer(self):
        self.get_cnmfe_results()

        vi = ViewerInterface(self.viewer_ref)

        if not vi.discard_workEnv():
            return

        vi.viewer.status_bar_label.showMessage('Loading CNMFE data, please wait...')
        pickle_file_path = self.batch_dir + '/' + str(self.UUID) + '_workEnv.pik'
        tiff_path = self.batch_dir + '/' + str(self.UUID) + '.tiff'

        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path, tiff_path)
        vi.update_workEnv()

        input_params = pickle.load(open(self.batch_dir + '/' + str(self.UUID) + '.params', 'rb'))

        vi.viewer.workEnv.history_trace.append({'cnmfe': input_params})

        self.viewer_ref.parent().ui.actionROI_Manager.trigger()

        for m in self.viewer_ref.parent().running_modules:
            if isinstance(m, ModuleGUI):
                m.start_cnmfe_mode()
                m.add_all_cnmfe_components(cnmA=self.cnmA,
                                           cnmb=self.cnmb,
                                           cnmC=self.cnmC,
                                           cnm_f=self.cnm_f,
                                           cnmYrA=self.cnmYrA,
                                           idx_components=self.idx_components,
                                           dims=self.dims,
                                           input_params_dict=input_params)

        if 'name_cnmfe' in input_params.keys():
            name = input_params['name_cnmfe']
        else:
            name = ''
        vi.viewer.ui.label_curr_img_seq_name.setText('CNMFE of: ' + name)
        #self.hide()
        self.close()


if sys.argv[0] == __file__:
    run(sys.argv[1], sys.argv[2], sys.argv[3])
