#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 27 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from psutil import cpu_count
from . import configuration
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .preferences_pytemplate import *
import os
# configuration.n_processes = cpu_count() - 1


class PreferencesGUI(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.spinBoxCores.setValue(int(configuration.sys_cfg['HARDWARE']['n_processes']))
        self.ui.spinBoxCores.setMaximum(int(cpu_count() / 2 - 1))

        self.ui.btnCaimanPath.clicked.connect(self.choose_caiman_path)
        self.ui.btnAnacondaPath.clicked.connect(self.choose_anaconda_dir_path)

        self.ui.btnReloadConfigFile.clicked.connect(self.reload_config_file)

        self.ui.btnApply.clicked.connect(self.apply)
        self.ui.btnClose.clicked.connect(self.hide)

    def apply(self):
        configuration.sys_cfg['HARDWARE']['n_processes'] = str(self.ui.spinBoxCores.value())
        self.set_anaconda_env()
        self.set_env_variables()
        configuration.write_sys_config()

    def choose_caiman_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select CaImAn path')

        if path == '':
            return

        if not os.path.isdir(path + '/caiman'):
            QtWidgets.QMessageBox.warning(self, 'Invalid CaImAn dir',
                                          'The directory you have chosen is not a CaImAn root directory.'
                                          'You must choose the directory that contains the "caiman" directory under it')
            return

        configuration.sys_cfg['PATHS']['caiman'] = path
        self.ui.lineEditCaimanPath.setText(path)

    def choose_anaconda_dir_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select path to anaconda3')

        if path == '':
            return

        if not os.path.isfile(path + '/bin/activate'):
            QtWidgets.QMessageBox.warning(self, 'Invalid anaconda directory',
                                          'The directory you have chosen does not appear to a valid anaconda3 directory.')
            return

        configuration.sys_cfg['PATHS']['anaconda3'] = path
        self.ui.lineEditAnacondaPath.setText(path)

    def set_anaconda_env(self):
        configuration.sys_cfg['BATCH']['anaconda_env'] = self.ui.lineEditAnacondaEnvName.text()

    def set_env_variables(self):
        configuration.sys_cfg['ENV'] = dict.fromkeys(list(filter(None, self.ui.plainTextEditEnvironmentVariables.toPlainText().split('\n'))))

    def reload_config_file(self):
        configuration.open_sys_config()
        self.load_ui_from_config_file()

    def load_ui_from_config_file(self):
        self.ui.lineEditCaimanPath.setText(configuration.sys_cfg['PATHS']['caiman'])
        self.ui.lineEditAnacondaPath.setText(configuration.sys_cfg['PATHS']['anaconda3'])
        self.ui.lineEditAnacondaEnvName.setText(configuration.sys_cfg['BATCH']['anaconda_env'])
        self.ui.spinBoxCores.setValue(int(configuration.sys_cfg['HARDWARE']['n_processes']))
        self.ui.plainTextEditEnvironmentVariables.setPlainText('\n'.join(configuration.sys_cfg.options('ENV')))

    def show(self):
        self.load_ui_from_config_file()
        super(PreferencesGUI, self).show()
