#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 21 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .main_window_pytemplate import *
from ..pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from ..pyqtgraphCore.console import ConsoleWidget
from ..pyqtgraphCore.imageview import ImageView
from .modules import *
from .core.common import ViewerInterface
import numpy as np
from .core.viewer_work_environment import ViewerWorkEnv
from ..common import configuration, doc_pages
from .image_menu.main import ImageMenu
from spyder.widgets.variableexplorer import objecteditor
import traceback
from .core.add_to_project import AddToProjectDialog
import os
from . import image_utils
import importlib
from .modules import custom_modules


class MainWindow(QtWidgets.QMainWindow):
    standard_modules = {'tiff_io': tiff_io.ModuleGUI,
                        'mesfile': mesfile_io.ModuleGUI,
                        'cnmf': cnmf.ModuleGUI,
                        'cnmfe': cnmfe.ModuleGUI,
                        'caiman_motion_correction': caiman_motion_correction.ModuleGUI,
                        'roi_manager': roi_manager.ModuleGUI,
                        'stimulus_mapping': stimulus_mapping.ModuleGUI,
                        'script_editor': script_editor.ModuleGUI
                        }

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.running_modules = []
        # TODO: Integrate viewer initiation here instead of outside
        self.ui.actionMesfile.triggered.connect(lambda: self.run_module(mesfile_io.ModuleGUI))
        self.ui.actionTiff_file.triggered.connect(lambda: self.run_module(tiff_io.ModuleGUI))
        self.ui.actionCNMF.triggered.connect(lambda: self.run_module(cnmf.ModuleGUI))
        self.ui.actionCNMF_E.triggered.connect(lambda: self.run_module(cnmfe.ModuleGUI))
        self.ui.actionMotion_Correction.triggered.connect(lambda: self.run_module(caiman_motion_correction.ModuleGUI))
        self.ui.actionROI_Manager.triggered.connect(lambda: self.run_module(roi_manager.ModuleGUI))
        self.ui.actionStimulus_Mapping.triggered.connect(lambda: self.run_module(stimulus_mapping.ModuleGUI))
        self.ui.actionScript_Editor.triggered.connect(lambda: self.run_module(script_editor.ModuleGUI))

        self.ui.actionWork_Environment_Info.triggered.connect(self.open_workEnv_editor)
        self.ui.actionAdd_to_project.triggered.connect(self.add_work_env_to_project)
        self.ui.actionSave_work_environment.triggered.connect(self.save_work_environment_dialog)
        self.ui.actionOpen_docs.triggered.connect(doc_pages['viewer'])

        self.add_to_project_dialog = None
        self.custom_modules = None
        self._cms = []
        self._cms_actions = []
        self.set_custom_module_triggers()

        self.ui.dockConsole.hide()

    def set_custom_module_triggers(self):
        self.custom_modules = dict()

        for mstr in custom_modules.__all__:
            mstr = '.' + mstr
            mod = importlib.import_module(mstr, package='mesmerize.viewer.modules.custom_modules')
            c = getattr(mod, 'ModuleGUI')
            self.custom_modules[mod.module_name] = c

            name = mod.module_name
            action = QtWidgets.QAction(self)
            action.setCheckable(False)
            action.setObjectName("custom_module" + name)
            action.setText(name)

            action.triggered.connect(lambda: self.run_module(c))

            self._cms_actions.append(action)
            self.ui.menuCustom_Modules.addAction(self._cms_actions[-1])

    @property
    def viewer_reference(self):
        return self._viewer

    @viewer_reference.setter
    def viewer_reference(self, viewer: ImageView):
        self._viewer = viewer
        self._viewer.workEnv = ViewerWorkEnv()

        self.run_module(roi_manager.ModuleGUI, hide=True)
        self.roi_manager = self.running_modules[-1]

        status_label = self.statusBar()
        status_bar = self.statusBar()
        # status_bar.addWidget(status_label)

        self._viewer.status_bar_label = status_label

        self.initialize_menubar_triggers()

        ns = {'np': np,
              'vi': self.vi,
              'viewer': self.vi.viewer,
              'ViewerWorkEnv': ViewerWorkEnv,
              'get_workEnv': self.vi.viewer.get_workEnv,
              # 'get_seq': self.vi.viewer.workEnv.get_seq,
              # 'get_meta': self.vi.viewer.workEnv.get_meta,
              # 'get_imgdata': self.vi.viewer.workEnv.get_imgdata,
              'update_workEnv': self.vi.update_workEnv,
              'clear_workEnv': self.vi._clear_workEnv,
              'running_modules': self.running_modules,
              'get_module': self.run_module,
              'get_batch_manager': self.get_batch_manager,
              'roi_manager': self.vi.viewer.workEnv.roi_manager,
              'objecteditor': objecteditor,
              'image_utils': image_utils,
              'main': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "ViewerInterface as vi \n" \
              "self as main         \n" \
              "objecteditor as objecteditor\n" \
              "ViewerWorkEnv class: workEnv\n" \
              "useful shorcuts for scripting, see docs:\n" \
              "viewer, get_workEnv(), running_modules\n" \
              "get_workEnv().imgdata, get_workEnv().imgdata.seq, get_workEnv().meta, get_workEnv().roi_manager\n" \
              "useful functions for scripting:\n" \
              "update_workEnv, clear_workEnv, get_module, get_batch_manager\n" \
              "For useful image utility functions: image_utils"

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history/')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/viewer.pik'

        self.console = ConsoleWidget(namespace=ns, text=txt, historyFile=cmd_history_file)

        self.ui.dockConsole.setWidget(self.console)

    def run_module(self, module_class, hide=False) -> object:
        """
        :param module_class: The python module imported within this main_window module or the module name as a str
        :param hide: To not show the widget, useful for scripting
        :return: Return the chosen module, instantiate it if it's not already running.
        """
        # Show the QDockableWidget if it's already running
        if type(module_class) is str:
            module_class = {**self.standard_modules, **self.custom_modules}[module_class]

        for m in self.running_modules:
            if isinstance(m, module_class):
                if not hide:
                    m.show()
                return m

        # Else create instance and start running it
        m = module_class(self, self._viewer)
        self.running_modules.append(m)

        if not hide:
            self.running_modules[-1].show()
        else:
            self.running_modules[-1].hide()
        return self.running_modules[-1]

    def update_available_inputs(self):
        for m in self.running_modules:
            if hasattr(m, 'update_available_inputs'):
                m.update_available_inputs()

    def initialize_menubar_triggers(self):
        self.ui.actionBatch_Manager.triggered.connect(self.start_batch_manager)

        self.vi = ViewerInterface(self._viewer)

        self.ui.actionDump_Work_Environment.triggered.connect(self.vi.discard_workEnv)

        self.image_menu = ImageMenu(self.vi)

        self.ui.actionReset_Scale.triggered.connect(self.image_menu.reset_scale)
        self.ui.actionMeasure.triggered.connect(self.image_menu.measure_tool)
        self.ui.actionResize.triggered.connect(self.image_menu.resize)
        self.ui.actionCrop.triggered.connect(self.image_menu.crop)

        self.ui.actionMean.triggered.connect(self.image_menu.mean_projection)
        self.ui.actionMax.triggered.connect(self.image_menu.max_projection)
        self.ui.actionStandard_Deviation.triggered.connect(self.image_menu.std_projection)
        self.ui.actionClose_all_projection_windows.triggered.connect(self.image_menu.close_projection_windows)

    def get_batch_manager(self) -> object:
        return configuration.window_manager.get_batch_manager()

    def start_batch_manager(self):
        batch_manager = self.get_batch_manager()
        batch_manager.show()

    def open_workEnv_editor(self):
        self.vi.viewer.status_bar_label.showMessage('Please wait, loading editor interface...')

        # if hasattr(self.vi.viewer.workEnv.roi_manager, 'roi_list'):
        #     roi_list = self.vi.viewer.workEnv.roi_manager.roi_list
        # else:
        #     roi_list = None

        # d = {'custom_columns_dict': self.vi.viewer.workEnv.custom_columns_dict,
        #      'isEmpty':             self.vi.viewer.workEnv.isEmpty,
        #      'imgdata':             self.vi.viewer.workEnv.imgdata.seq,
        #      'meta_data':           self.vi.viewer.workEnv.imgdata.meta,
        #      'roi_list':            roi_list,
        #      'comments':            self.vi.viewer.workEnv.comments,
        #      'origin_file':         self.vi.viewer.workEnv.origin_file,
        #      '_saved':              self.vi.viewer.workEnv._saved
        #      }

        try:
            changes = objecteditor.oedit(self.vi.viewer.workEnv)
        except:
            print(traceback.format_exc())
            # QtWidgets.QMessageBox.de(self, 'Unable to open work environment editor',
            #                               'The following error occured while trying to open the work environment editor:'
            #                               '\n', traceback.format_exc())
            return

        if changes is not None:
            try:
                    self.vi.viewer.workEnv = changes
                    self.vi.update_workEnv()
            except:
                QtWidgets.QMessageBox.warning(self, 'Unable to apply changes',
                                              'The following error occured while trying to save changes to the work '
                                              'environment. You may want to use the console and make sure your work '
                                              'environment has not been corrupted.'
                                              '\n' + str(traceback.format_exc()))
                return
        elif changes is None:
            self.vi.viewer.status_bar_label.showMessage('Work environment unchanged')
            return

        self.vi.viewer.status_bar_label.showMessage('Your edits were successfully applied to the work environment!')

        # You can even let the user save changes if they click "OK", and the function returns None if they cancel

    def add_work_env_to_project(self):
        if self.vi.viewer.workEnv.isEmpty:
            QtWidgets.QMessageBox.information(self, 'Empty work environment',
                                              'Nothing to save, work environment is empty')
            return
        if self.add_to_project_dialog is not None:
            try:
                self._delete_add_to_project_dialog()
                self.add_to_project_dialog = None
            except:
                pass

        if configuration.proj_path is None:
            if QtWidgets.QMessageBox.question(self, 'No project open',
                                              'Would you like to switch to project mode?',
                                              QtWidgets.QMessageBox.No,
                                              QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
                return
            else:
                import common.start
                common.start.main()

        if len(self.viewer_reference.workEnv.roi_manager.roi_list) == 0:
            QtWidgets.QMessageBox.warning(self, 'No curves',
                                          'You do not have any curves in your work environment')
            return

        else:
            self.add_to_project_dialog = AddToProjectDialog(self.viewer_reference.workEnv)
            self.add_to_project_dialog.signal_finished.connect(self._delete_add_to_project_dialog)
            self.add_to_project_dialog.show()

    def _delete_add_to_project_dialog(self):
        self.add_to_project_dialog.deleteLater()

    def save_work_environment_dialog(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Work environment file name')
        if path == '':
            return

        try:
            dirname = os.path.dirname(path[0])
            filename = os.path.basename(path[0])
            self.vi.viewer.workEnv.to_pickle(dir_path=dirname, filename=filename)
        except Exception:
            QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + traceback.format_exc())

    def open_work_environment_dialog(self):
        pass
