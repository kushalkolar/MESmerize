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
from .pytemplates.system_config_pytemplate import *
from functools import partial
import traceback
import os


class SystemConfigGUI(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.setWindowTitle('System Configuration')
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.spinBoxThreads.setMaximum(cpu_count() - 1)

        self.set_ui_from_config()

        self.ui.btnApply.clicked.connect(self.set_config_from_ui)
        self.ui.btnClose.clicked.connect(self.close)

        self.ui.pushButtonCUDAError.setVisible(False)
        self.ui.pushButtonCUDAError.setDisabled(True)

        self.check_cuda()

        self.ui.btnReloadConfigFile.clicked.connect(self.set_ui_from_config)
        self.ui.pushButtonResetDefaults.clicked.connect(
            partial(self.set_ui_from_config, configuration.default_sys_config))

        self.saved = True

    def _set_config(self, **kwargs):
        sys_cfg = configuration.get_sys_config()
        for k in kwargs.keys():
            sys_cfg['_MESMERIZE_{}'.format(k.upper())] = kwargs[k]
        configuration.save_sys_config(sys_cfg)

    def set_ui_from_config(self, config: dict = None):
        if config is None:
            config = configuration.get_sys_config()
        n_threads = config['_MESMERIZE_N_THREADS']
        python_call = config['_MESMERIZE_PYTHON_CALL']
        use_cuda = config['_MESMERIZE_USE_CUDA']
        workdir = config['_MESMERIZE_WORKDIR']
        prefix_commands = config['_MESMERIZE_PREFIX_COMMANDS']
        custom_modules_dir = config['_MESMERIZE_CUSTOM_MODULES_DIR']

        self.ui.spinBoxThreads.setValue(n_threads)
        self.ui.lineEditPythonCall.setText(python_call)
        self.ui.checkBoxUseCUDA.setChecked(use_cuda)
        self.ui.lineEditWorkDir.setText(workdir)
        self.ui.plainTextEditPrefixCommands.setPlainText(prefix_commands)
        self.ui.lineEditCustomModulesDir.setText(custom_modules_dir)

    def _get_ui_config(self) -> dict:
        return dict(n_threads=self.ui.spinBoxThreads.value(),
                    python_call=self.ui.lineEditPythonCall.text(),
                    use_cuda=self.ui.checkBoxUseCUDA.isChecked(),
                    workdir=self.ui.lineEditWorkDir.text(),
                    prefix_commands=self.ui.plainTextEditPrefixCommands.toPlainText(),
                    custom_modules_dir=self.ui.lineEditCustomModulesDir.text())

    def set_config_from_ui(self):
        if self.check_workdir():
            self._set_config(**self._get_ui_config())
        else:
            QtWidgets.QMessageBox.warning(self, 'Insufficient permissions',
                                          'You do not have write access to the chosen work directory.\n'
                                          'Enter a different directory')
            return

    def check_workdir(self) -> bool:
        workdir = self.ui.lineEditWorkDir.text()
        if os.access(workdir, os.W_OK):
            return True
        else:
            return False

    def check_cuda(self) -> bool:
        self.cuda_error_msg = None

        try:
            import pycuda
            import skcuda
            from pycuda import driver
            import pycuda.autoinit
            driver.Device.count()
            return True

        except ImportError:
            self.cuda_error_msg = traceback.format_exc()
            self.ui.checkBoxUseCUDA.setText('Use CUDA - Disabled, could not import libraries')

        except driver.LogicError:
            self.cuda_error_msg = traceback.format_exc()
            self.ui.checkBoxUseCUDA.setText('Use CUDA - Disabled, could not find CUDA devices using driver')

        self.disable_cuda_UI()
        return False

    def disable_cuda_UI(self):
        self.ui.checkBoxUseCUDA.setChecked(False)
        self.ui.checkBoxUseCUDA.setDisabled(True)
        self.ui.pushButtonCUDAError.setVisible(True)
        self.ui.pushButtonCUDAError.setEnabled(True)
        self.ui.pushButtonCUDAError.clicked.connect(self.show_cuda_error)

    def show_cuda_error(self):
        QtWidgets.QMessageBox.information(self, 'CUDA Error', self.cuda_error_msg)

    # def close_requested(self):
    #     cfg = self._get_ui_config()
    #     sys_cfg = configuration.get_sys_config()
    #     for k in cfg.keys():
    #         if sys_cfg[k] != cfg[k]:
    #             if QtWidgets.QMessageBox.warning(self, 'Unsaved changes',
    #                                          'You have not applied your changes, '
    #                                          'would you like to close anyways?',
    #                                          QtWidgets.QMessageBox.Yes,
    #                                          QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
    #                 return
    #             else:
    #                 return

    # def show(self):
    #     self.load_ui_from_config_file()
    #     super(SystemConfigGUI, self).show()
