#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 13 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerInterface
from .pytemplates.caiman_motion_correction_pytemplate import *
import json
from ...common import configuration
from ...pyqtgraphCore import LinearRegionItem


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnAddToBatchRigid.clicked.connect(self.add_rig_corr_to_batch)
        self.ui.btnAddToBatchElastic.clicked.connect(self.add_elas_corr_to_batch)

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

    def _make_params_dict(self) -> dict:
        d = {'max_shifts_x':        self.ui.spinboxX.value(),
             'max_shifts_y':        self.ui.spinboxY.value(),
             'iters_rigid':         self.ui.spinboxIterRigid.value(),
             'name_rigid':          self.ui.lineEditNameRigid.text(),
             'max_dev':             self.ui.spinboxMaxDev.value(),
             'strides':             self.ui.sliderStrides.value(),
             'overlaps':            self.ui.sliderOverlaps.value(),
             'upsample':            self.ui.spinboxUpsample.value(),
             'name_elas':           self.ui.lineEditNameElastic.text(),
             'output_bit_depth':    self.ui.comboBoxOutputBitDepth.currentText()
             }
        return d

    def set_params(self, params: dict):
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

    def add_rig_corr_to_batch(self):
        pass

    def add_elas_corr_to_batch(self):
        d = self._make_params_dict()

        batch_manager = configuration.window_manager.get_batch_manager()
        name = self.ui.lineEditNameElastic.text()

        self.vi.viewer.status_bar_label.showMessage('Please wait, adding CaImAn motion correction: ' + name + ' to batch...')

        batch_manager.add_item(module='caiman_motion_correction',
                               viewer_reference=self.vi.viewer,
                               name=name,
                               input_workEnv=self.vi.viewer.workEnv,
                               input_params=d,
                               info=d)

        self.vi.viewer.status_bar_label.showMessage('Done adding CaImAn motion correction: ' + name + ' to batch!')


        self.ui.lineEditNameElastic.clear()
