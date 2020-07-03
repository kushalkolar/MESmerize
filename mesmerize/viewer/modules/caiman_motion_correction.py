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

        d = {'output_bit_depth': self.ui.comboBoxOutputBitDepth.currentText()}

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

        if group_params:
            d.update({'mc_kwargs': mc_params})

        else:
            d.update({**mc_params})

        return d

    def add_to_batch_elas_corr(self):
        """
        Add a batch item with the currently set parameters and the current work environment.
        """
        d = self.get_params()

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
            input_params = params
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
