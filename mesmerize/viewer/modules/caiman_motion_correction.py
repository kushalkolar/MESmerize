#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerUtils
from .pytemplates.caiman_motion_correction_pytemplate import *
from ...common import get_window_manager
from ...pyqtgraphCore import LinearRegionItem
from uuid import UUID
from copy import deepcopy
from joblib import Parallel, delayed
import numpy as np
from psutil import cpu_count
import tifffile
from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import os
from math import ceil
from itertools import product
from typing import *


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchElastic.clicked.connect(self.add_to_batch_elas_corr)

        self.ui.btnShowQuilt.clicked.connect(self.draw_quilt)

        self.ui.sliderOverlaps.valueChanged.connect(self.draw_quilt)
        self.ui.sliderStrides.valueChanged.connect(self.draw_quilt)

        self.overlapsH = []
        self.overlapsV = []

        self.ncols_projection_plots = 3
        self.cmap_projection_plots = 'gray'
        self.projections_plot_widget = None
        self.projections_plot_vmin_vmax_stds = 5

        self.currrent_projections: List[np.ndarray] = None

        self.ui.pushButtonViewProjections.clicked.connect(self.view_output_projections)

    def draw_quilt(self):
        if self.ui.btnShowQuilt.isChecked() is False:
            self.remove_quilt()
            return
        if len(self.overlapsV) > 0:
            for overlap in self.overlapsV:
                self.vi.viewer.view.removeItem(overlap)
            for overlap in self.overlapsH:
                self.vi.viewer.view.removeItem(overlap)
            self.overlapsV = []
            self.overlapsH = []

        w = int(self.vi.viewer.view.addedItems[0].width())
        k = self.ui.sliderStrides.value()

        h = int(self.vi.viewer.view.addedItems[0].height())
        j = self.ui.sliderStrides.value()

        val = int(self.ui.sliderOverlaps.value())

        for i in range(1, int(w / k) + 1):
            linreg = LinearRegionItem(values=[i * k, i * k + val], brush=(255, 255, 255, 80),
                                      movable=False, bounds=[i * k, i * k + val])
            self.overlapsV.append(linreg)
            self.vi.viewer.view.addItem(linreg)

        for i in range(1, int(h / j) + 1):
            linreg = LinearRegionItem(values=[i * j, i * j + val], brush=(255, 255, 255, 80),
                                      movable=False, bounds=[i * j, i * j + val],
                                      orientation=LinearRegionItem.Horizontal)
            self.overlapsH.append(linreg)
            self.vi.viewer.view.addItem(linreg)

    def remove_quilt(self):
        for o in self.overlapsV:
            self.vi.viewer.view.removeItem(o)
        for o in self.overlapsH:
            self.vi.viewer.view.removeItem(o)
        self.overlapsH = []
        self.overlapsV = []

    def get_params(self, group_params: bool = False) -> dict:
        """
        Get a dict of the set parameters
        :return: parameters dict
        :rtype: dict
        """

        if self.ui.spinBoxGSig_filt.value() == 0:
            gSig_filt = None
        else:
            gSig = self.ui.spinBoxGSig_filt.value()
            gSig_filt = (gSig, gSig)

        d = \
            {
                'output_bit_depth': self.ui.comboBoxOutputBitDepth.currentText(),
                'template': None
            }

        mc_params = \
            {
                'max_shifts': (self.ui.spinboxX.value(), self.ui.spinboxY.value()),
                'niter_rig': self.ui.spinboxIterRigid.value(),
                'max_deviation_rigid': self.ui.spinboxMaxDev.value(),
                'strides': (self.ui.sliderStrides.value(), self.ui.sliderStrides.value()),
                'overlaps': (self.ui.sliderOverlaps.value(), self.ui.sliderOverlaps.value()),
                'upsample_factor_grid': self.ui.spinboxUpsample.value(),
                'gSig_filt': gSig_filt
            }

        # Update the dict with any user entered kwargs
        if self.ui.groupBox_motion_correction_kwargs.isChecked():
            _kwargs = self.ui.plainTextEdit_mc_kwargs.toPlainText()
            mc_params.update(eval(f"dict({_kwargs})"))

        if self.vi.viewer.workEnv.imgdata.ndim == 4:
            is_3d = True
        else:
            is_3d = False

        d['is_3d'] = is_3d

        if group_params:
            d.update({'mc_kwargs': mc_params})

        else:
            d.update({**mc_params})

        return d

    def add_to_batch_elas_corr(self):
        """
        Add a batch item with the currently set parameters and the current work environment.
        """

        name = self.ui.lineEditNameElastic.text()

        self.vi.viewer.status_bar_label.showMessage(
            'Please wait, adding CaImAn motion correction: ' + name + ' to batch...')

        self.add_to_batch()

        self.vi.viewer.status_bar_label.showMessage('Done adding CaImAn motion correction: ' + name + ' to batch!')

        self.ui.lineEditNameElastic.clear()

    def add_to_batch(self, params: dict = None) -> UUID:
        if params is None:
            input_params = self.get_params(group_params=True)
            item_name = self.ui.lineEditNameElastic.text()
            input_params['item_name'] = item_name
        else:
            # check that params dict is formatted properly
            required_keys = ['item_name', 'mc_kwargs', 'output_bit_depth']
            if any([k not in params.keys() for k in required_keys]):
                raise ValueError(f'Must pass a params dict with the following keys:\n'
                                 f'{required_keys}\n'
                                 f'Please see the docs for more information.')
            input_params = deepcopy(params)
            item_name = input_params['item_name']

        input_workEnv = self.vi.viewer.workEnv
        batch_manager = get_window_manager().get_batch_manager()
        u = batch_manager.add_item(module='caiman_motion_correction',
                                   name=item_name,
                                   input_workEnv=input_workEnv,
                                   input_params=input_params,
                                   info=input_params
                                   )

        return u

    @staticmethod
    def _get_projection(proj_type: str,  batch_path: str, item_uuid: UUID):
        tiff_path = os.path.join(batch_path, f'{item_uuid}_mc.tiff')
        tif = tifffile.TiffFile(tiff_path, is_nih=True)
        seq = tif.asarray(maxworkers=cpu_count())

        func = getattr(np, f"nan{proj_type}")
        return func(seq, axis=0)

    def view_output_projections(self):
        batch_manager = get_window_manager().get_batch_manager()
        batch_path = batch_manager.batch_path

        items = batch_manager.get_selected_items()  # get a list of indices and UUIDs for the selected items
        self._projection_item_indices = items[0]
        item_uuids = items[1]

        if len(self._projection_item_indices) > 3:
            if QtWidgets.QMessageBox.question(
                self, 'Many items selected',
                f"You have selected < {len(self._projection_item_indices)} > items, "
                f"it may take a while to calculate these projections.\n"
                f"Do you still want to continue?",
                QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes
            ) == QtWidgets.QMessageBox.No:
                return

        proj = self.ui.comboBoxProjectionsOption.currentText()

        print("Calculating projections, please wait...")

        self.currrent_projections = Parallel(n_jobs=cpu_count(), verbose=5)(
            delayed(ModuleGUI._get_projection)(proj, batch_path, item_uuid) for item_uuid in item_uuids
        )

        self.nrows_projection_plots = ceil(len(self._projection_item_indices) / self.ncols_projection_plots)

        self.plot_output_projections()

    def plot_output_projections(self):
        if self.currrent_projections is None:
            raise AttributeError("Projections not calculated")

        print("Plotting projections")
        if self.projections_plot_widget is None:
            self.projections_plot_widget = MatplotlibWidget()
        else:
            self.projections_plot_widget.fig.clear()

        self.projections_plot_widget.axs = self.projections_plot_widget.fig.subplots(self.nrows_projection_plots, self.ncols_projection_plots)

        for i, axes_ix in enumerate(
                product(range(self.nrows_projection_plots), range(self.ncols_projection_plots))
        ):
            if not i < len(self._projection_item_indices):
                break

            index = self._projection_item_indices[i]
            projection = self.currrent_projections[i]

            proj_mean = np.nanmean(projection)
            proj_std = np.nanstd(projection)

            z = self.projections_plot_vmin_vmax_stds * proj_std

            vmin = max(proj_mean - z, np.nanmin(projection))
            vmax = min(proj_mean + z, np.nanmax(projection))

            self.projections_plot_widget.axs[axes_ix].imshow(
                projection,
                cmap=self.cmap_projection_plots,
                vmin=vmin,
                vmax=vmax
            )
            self.projections_plot_widget.axs[axes_ix].set_title(index)
            self.projections_plot_widget.axs[axes_ix].set_title(index)

        self.projections_plot_widget.fig.tight_layout()
        self.projections_plot_widget.draw()
        self.projections_plot_widget.show()
