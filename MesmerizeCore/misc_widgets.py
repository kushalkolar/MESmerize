#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 16 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .meta_editor_pytemplate import Ui_meta_editor_template
from .exporter_pytemplate import Ui_exporter_template


class MetaDataEditor(QtWidgets.QWidget, Ui_meta_editor_template):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.show()

    def fill_widget(self, meta_d):
        if 'fps' in meta_d.keys():
            if type(meta_d['fps']) is float:
                self.doubleSpinFPS.setValue(meta_d['fps'])
        if 'date' in meta_d.keys():
            ymd = meta_d['date'].split('_')[0]
            hms = meta_d['date'].split('_')[1]

            self.lineEdYYYYMMDDD.setText(str(ymd))
            self.lineEdHHMMSS.setText(str(hms))

    def get_data(self):
        ymd = int(self.lineEdYYYYMMDDD.text())
        hms = int(self.lineEdHHMMSS.text())
        date = str(ymd) + '_' + str(hms)

        fps = self.doubleSpinFPS.value()

        d = {'fps': fps, 'date': date}

        return d


class Exporter(QtWidgets.QWidget, Ui_exporter_template):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        formats = ['tiff', 'MJPG', 'X264', 'gif']
        self.comboBoxFormat.addItems(formats)
        self.labelSlider.setText(str(self.sliderFPS_Scaling.value()/10))
        self.sliderFPS_Scaling.valueChanged.connect(lambda v: self.labelSlider.setText(str(v/10)))
        self.comboBoxFormat.currentTextChanged.connect(self._enable_non_tiff)

    def _enable_non_tiff(self, f):
        if f == 'tiff':
            self._enable_non_tiff_ui(False)
        else:
            self._enable_non_tiff_ui(True)

    def _enable_non_tiff_ui(self, b=True):
        self.radioAuto.setEnabled(b)
        self.radioFromViewer.setEnabled(b)
        self.sliderFPS_Scaling.setEnabled(True)

    def file_path_dialog(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Export filename, do not type an extension', '', '(*.*)')
        if path == '':
            return

        self.lineEdPath.setText(path[0])
