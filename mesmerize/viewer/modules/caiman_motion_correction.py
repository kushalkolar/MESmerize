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


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchRigid.clicked.connect(self.add_to_batch_rig_corr)
        self.ui.btnAddToBatchElastic.clicked.connect(self.add_to_batch_elas_corr)

        self.ui.btnShowQuilt.clicked.connect(self.draw_quilt)

        self.ui.sliderOverlaps.valueChanged.connect(self.draw_quilt)
        self.ui.sliderStrides.valueChanged.connect(self.draw_quilt)

        self.overlapsH = []
        self.overlapsV = []

        self._input_workEnv = None

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

    def set_params(self, params: dict):
        """
        Set all parameters from a dict. All keys must be present in the dict and of the correct type.

        :param params: dict of parameters
        """
        self.ui.spinboxX.setValue(params['max_shifts_x'])
        self.ui.spinboxY.setValue(params['max_shifts_y'])
        self.ui.spinboxIterRigid.setValue(params['iters_rigid'])
        self.ui.lineEditNameRigid.setText(params['name_rigid'])
        self.ui.spinboxMaxDev.setValue(params['max_dev'])
        self.ui.sliderStrides.setValue(params['strides'])
        self.ui.sliderOverlaps.setValue(params['overlaps'])
        self.ui.spinboxUpsample.setValue(params['upsample'])
        self.ui.lineEditNameElastic.setText(params['name_elas'])
        if params['output_bit_depth'] == 'Do not convert':
            self.ui.comboBoxOutputBitDepth.setCurrentIndex(0)
        elif params['output_bit_depth'] == '8':
            self.ui.comboBoxOutputBitDepth.setCurrentIndex(1)
        elif params['output_bit_depth'] == '16':
            self.ui.comboBoxOutputBitDepth.setCurrentIndex(2)
        self.ui.spinBoxGSig_filt.setValue(params['gSig_filt'])

    def set_input_workEnv(self, workEnv):
        self._input_workEnv = workEnv

    def get_input_workEnv(self):
        if self._input_workEnv is None:
            raise ValueError('Input work environment is not set')
        else:
            return self._input_workEnv

    def add_to_batch_rig_corr(self):
        pass

    def add_to_batch_elas_corr(self):
        """
        Add a batch item with the currently set parameters and the current work environment.
        """
        d = self.get_params()

        name = self.ui.lineEditNameElastic.text()

        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CaImAn motion correction: ' + name + ' to batch...')

        self.set_input_workEnv(self.vi.viewer.workEnv)
        self.add_to_batch()

        # batch_manager.add_item(module='caiman_motion_correction',
        #                        viewer_reference=self.vi.viewer,
        #                        name=name,
        #                        input_workEnv=self.vi.viewer.workEnv,
        #                        input_params=d,
        #                        info=d)

        self.vi.viewer.status_bar_label.showMessage('Done adding CaImAn motion correction: ' + name + ' to batch!')

        self.ui.lineEditNameElastic.clear()

    def add_to_batch(self):
        input_params = self.get_params(group_params=True)
        input_workEnv = self.get_input_workEnv()
        item_name = self.ui.lineEditNameElastic.text()
        batch_manager = get_window_manager().get_batch_manager()
        batch_manager.add_item(module='caiman_motion_correction',
                               name=item_name,
                               input_workEnv=input_workEnv,
                               input_params=input_params,
                               info=self.get_params())
