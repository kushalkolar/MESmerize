# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...common.qdialogs import *
from ...common.configuration import proj_cfg
from ..core.common import ViewerUtils
import numpy as np
from .pytemplates.caiman_importer_pytemplate import *
from caiman.utils.utils import load_dict_from_hdf5
import os


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.pushButton_select_file.clicked.connect(self.select_file)
        self.ui.pushButton_import.clicked.connect(self.import_file)

        self.cnmf_data = None
        self.path = None

    def _load_data(self, path: str):
        try:
            self.cnmf_data = load_dict_from_hdf5(path)
        except Exception as e:
            self.cnmf_data = None
            self.path = None
            raise ValueError("Error while opening the file, make sure it is a valid Caiman HDF5 output file.\n")
        else:
            self.path = path

    @present_exceptions('Error importing caiman data')
    @use_open_file_dialog('Select HDF5 output file', exts=['*.hdf5', '*.h5', '*.hdf'])
    def select_file(self, path: str, *args):
        self._load_data(path)
        self.ui.label_file.setText(path)

    @present_exceptions('Error importing caiman data')
    def import_file(self, path: str = None):
        # Ask user if clear work env if it's not empty
        if hasattr(self.vi.viewer.workEnv, 'roi_manager'):
            if self.vi.viewer.workEnv.roi_manager is not None:
                if len(self.vi.viewer.workEnv.roi_manager.roi_list) > 0:
                    if QtWidgets.QMessageBox.warning(self, 'ROIs currently present in work environment',
                                                     'This will elar ROIs that are currently in the work '
                                                     'environment continue?',
                                                     QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == \
                            QtWidgets.QMessageBox.No:
                        return

        if (path is None) and (self.path is None):
            raise ValueError("Must specify path as an argument")

        # If this was used in command line mode
        elif path:
            self._load_data(path)

        self.vi.viewer.status_bar_label.showMessage('Importing CNMF ROIs from HDF5 file, please wait...')

        # Load data using the appropriate back-end manager
        if self.vi.viewer.workEnv.imgdata.ndim == 4:
            roi_manager_gui = self.vi.viewer.parent().get_module('roi_manager')
            roi_manager_gui.start_backend('VolCNMF')

            roi_manager_gui.manager.add_all_components(
                self.cnmf_data,
                input_params_dict=self.cnmf_data['params'],
            )
        else:
            roi_manager_gui = self.vi.viewer.parent().get_module('roi_manager')
            roi_manager_gui.start_backend('CNMFROI')

            roi_manager_gui.manager.add_all_components(
                self.cnmf_data,
                input_params_dict=self.cnmf_data['params'],
            )

        # TODO: ADD THE INPUT PARAMS FROM THE HDF5 FILE TO THE HISTORY TRACE, NEEDS TO OVERWRITE IF ALREADY EXISTS.

        self.vi.viewer.status_bar_label.showMessage('Finished CNMF ROIs!')
