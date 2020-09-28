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
from ..pyqtgraphCore import setConfigOptions
from .modules import *
from .core.common import ViewerUtils
import numpy as np
from .core.viewer_work_environment import ViewerWorkEnv
from .core.data_types import ImgData
from ..common import configuration, doc_pages
from ..common import get_window_manager
from .image_menu.main import ImageMenu
from spyder.widgets.variableexplorer import objecteditor
import traceback
from .core.add_to_project import AddToProjectDialog
import os
from . import image_utils
import importlib
import importlib.util
# from .modules import custom_modules
from functools import partial
import sys
import pandas as pd
from typing import Optional, Union
from uuid import UUID as UUID_type

_custom_modules_dir = configuration.get_sys_config()['_MESMERIZE_CUSTOM_MODULES_DIR']
_custom_modules_package_name = os.path.basename(os.path.dirname(_custom_modules_dir))
_cmi = os.path.join(_custom_modules_dir, '__init__.py')

if os.path.isfile(_cmi):
    _parent_dir = os.path.abspath(os.path.join(_custom_modules_dir, os.path.pardir))
    sys.path.append(_parent_dir)
    _spec = importlib.util.spec_from_file_location('custom_modules', _cmi)
    custom_modules = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(custom_modules)
    _import_custom_modules = True
else:
    _import_custom_modules = False


dock_widget_area = {'roi_manager': QtCore.Qt.LeftDockWidgetArea,
                    roi_manager.ModuleGUI: QtCore.Qt.LeftDockWidgetArea,

                    'tiff_io': QtCore.Qt.TopDockWidgetArea,
                    tiff_io.ModuleGUI: QtCore.Qt.TopDockWidgetArea,

                    'suite2p_importer': QtCore.Qt.TopDockWidgetArea,
                    suite2p.ModuleGUI: QtCore.Qt.TopDockWidgetArea,

                    'stimulus_mapping': QtCore.Qt.BottomDockWidgetArea,
                    stimulus_mapping.ModuleGUI: QtCore.Qt.BottomDockWidgetArea
                    }

# caiman modules
if configuration.HAS_CAIMAN:
    dock_widget_area.update(
        {
            'cnmf': QtCore.Qt.RightDockWidgetArea,
            cnmf.ModuleGUI: QtCore.Qt.RightDockWidgetArea,

            'cnmfe': QtCore.Qt.RightDockWidgetArea,
            cnmfe.ModuleGUI: QtCore.Qt.RightDockWidgetArea,

            'cnmf_3d': QtCore.Qt.RightDockWidgetArea,
            cnmf_3d.ModuleGUI: QtCore.Qt.RightDockWidgetArea,

            'caiman_motion_correction': QtCore.Qt.RightDockWidgetArea,
            caiman_motion_correction.ModuleGUI: QtCore.Qt.RightDockWidgetArea,

            'caiman_importer': QtCore.Qt.TopDockWidgetArea,
            caiman_importer.ModuleGUI: QtCore.Qt.TopDockWidgetArea,

            'caiman_dfof': QtCore.Qt.RightDockWidgetArea,
            caiman_dfof.ModuleGUI: QtCore.Qt.RightDockWidgetArea,
        }
    )


class MainWindow(QtWidgets.QMainWindow):
    standard_modules = {'tiff_io': tiff_io.ModuleGUI,
                        'mesfile': mesfile_io.ModuleGUI,
                        'roi_manager': roi_manager.ModuleGUI,
                        'suite2p_importer': suite2p.ModuleGUI,
                        'stimulus_mapping': stimulus_mapping.ModuleGUI,
                        'script_editor': script_editor.ModuleGUI,
                        'mesc_importer': femtonics_mesc.ModuleGUI,
                        'exporter': exporter.ModuleGUI,
                        }

    if configuration.HAS_TENSORFLOW:
        standard_modules.update(
            {'nuset_segment': nuset_segment.ModuleGUI}
        )

    # caiman modules
    if configuration.HAS_CAIMAN:
        standard_modules.update(
            {
                'cnmf': cnmf.ModuleGUI,
                'cnmfe': cnmfe.ModuleGUI,
                'cnmf_3d': cnmf_3d.ModuleGUI,
                'caiman_motion_correction': caiman_motion_correction.ModuleGUI,
                'caiman_importer': caiman_importer.ModuleGUI,
                'caiman_dfof': caiman_dfof.ModuleGUI,
            }
        )

    available_modules = list(standard_modules.keys())

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.running_modules = []
        # TODO: Integrate viewer initiation here instead of outside
        self.ui.action_mes_importer.triggered.connect(lambda: self.run_module(mesfile_io.ModuleGUI))
        self.ui.action_mesc_importer.triggered.connect(lambda: self.run_module(femtonics_mesc.ModuleGUI))
        self.ui.actionTiff_file.triggered.connect(lambda: self.run_module(tiff_io.ModuleGUI))
        self.ui.actionROI_Manager.triggered.connect(lambda: self.run_module(roi_manager.ModuleGUI))
        self.ui.actionSuite2p_Importer.triggered.connect(lambda: self.run_module(suite2p.ModuleGUI))
        self.ui.actionStimulus_Mapping.triggered.connect(lambda: self.run_module(stimulus_mapping.ModuleGUI))
        self.ui.actionScript_Editor.triggered.connect(lambda: self.run_module(script_editor.ModuleGUI))

        if configuration.HAS_TENSORFLOW:
            self.ui.actionNuSeT_Segmentation.triggered.connect(lambda: self.run_module(nuset_segment.ModuleGUI))


        # TODO: refactor the actions trigger connections so they're automated based on module name
        if configuration.HAS_CAIMAN:
            self.ui.actionCNMF.triggered.connect(lambda: self.run_module(cnmf.ModuleGUI))
            self.ui.actionCNMF_E.triggered.connect(lambda: self.run_module(cnmfe.ModuleGUI))
            self.ui.actionCNMF_3D.triggered.connect(lambda: self.run_module(cnmf_3d.ModuleGUI))
            self.ui.actionMotion_Correction.triggered.connect(
                lambda: self.run_module(caiman_motion_correction.ModuleGUI)
            )
            self.ui.actionCaimanImportHDF5.triggered.connect(lambda: self.run_module(caiman_importer.ModuleGUI))
            self.ui.actionCaimanDFOF.triggered.connect(lambda: self.run_module(caiman_dfof.ModuleGUI))

        self.ui.actionWork_Environment_Info.triggered.connect(self.open_workEnv_editor)
        self.ui.actionAdd_to_project.triggered.connect(self.add_work_env_to_project)
        self.ui.actionSave_work_environment.triggered.connect(self.save_work_environment_dialog)
        self.ui.actionOpen_docs.triggered.connect(doc_pages['viewer'])
        self.ui.actionReport_issue_bug.triggered.connect(doc_pages['issue-tracker'])
        self.ui.actionQuestions_discussion.triggered.connect(doc_pages['gitter'])

        self.add_to_project_dialog = None
        self.custom_modules = None
        self._cms = []
        self._cms_actions = []

        self.setAcceptDrops(True)

        if _import_custom_modules:
            self.set_custom_module_triggers()

        self.ui.dockConsole.hide()

    def set_custom_module_triggers(self):
        self.custom_modules = dict()

        failed_imports = []
        for mstr in custom_modules.__all__:
            try:
                mstr = '.' + mstr
                mod = importlib.import_module(mstr, package=_custom_modules_package_name)
                c = getattr(mod, 'ModuleGUI')
                self.custom_modules[mod.module_name] = c

                name = mod.module_name
                action = QtWidgets.QAction(self)
                action.setCheckable(False)
                action.setObjectName("custom_module" + name)
                action.setText(name)

                action.triggered.connect(partial(self.run_module, c))

                self._cms_actions.append(action)
                self.ui.menuCustom_Modules.addAction(self._cms_actions[-1])
            except ImportError:
                failed_imports.append(mstr)
        if len(failed_imports) > 0:
            names = '\n'.join(failed_imports)
            QtWidgets.QMessageBox.warning(self, 'Failed to load plugings', f'The following plugins failed to load:\n{names}')

        self.available_modules += list(self.custom_modules.keys())

    @property
    def viewer_reference(self):
        return self._viewer

    @viewer_reference.setter
    def viewer_reference(self, viewer: ImageView):
        self._viewer = viewer
        self._viewer.workEnv = ViewerWorkEnv()

        self.run_module(roi_manager.ModuleGUI, hide=True)
        self.roi_manager = self.running_modules[-1]

        self._viewer.ui.btnExportWorkEnv.clicked.connect(
            partial(self.run_module, 'exporter')
        )

        status_label = self.statusBar()

        self._viewer.status_bar_label = status_label

        self.initialize_menubar_triggers()

        ns = {'np':                 np,
              'vi':                 self.vi,
              'viewer':             self.vi.viewer,
              'ViewerWorkEnv':      ViewerWorkEnv,
              'ImgData':            ImgData,
              'get_workEnv':        self.vi.viewer.get_workEnv,
              'get_image':          lambda: self.vi.viewer.get_workEnv().imgdata.seq,
              'get_meta':           lambda: self.vi.viewer.get_workEnv().imgdata.meta,
              'update_workEnv':     self.vi.update_workEnv,
              'clear_workEnv':      self.vi._clear_workEnv,
              'get_module':         self.get_module,
              'get_batch_manager':  self.get_batch_manager,
              'all_modules':        self.available_modules,
              'image_utils':        image_utils,
              'this': self
              }

        txt = "Namespaces:          \n" \
              "numpy as np          \n" \
              "ViewerUtils as vi \n" \
              "self as this \n" \
              "ViewerWorkEnv and ImgData for factory purposes\n" \
              "useful callables for scripting, see docs for examples:\n" \
              "get_workEnv(), get_image(), get_meta(), get_module(<module name>), get_batch_manager()\n" \
              "update_workEnv(), clear_workEnv()\n" \
              "'all_modules' will list all available modules\n" \
              "Some basic image utility functions: image_utils"

        cmd_history_file = os.path.join(configuration.console_history_path, 'viewer.pik')

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
            if self.custom_modules is None:
                cms = {}
            else:
                cms = self.custom_modules
            module_class = {**self.standard_modules, **cms}[module_class]

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

        if (module_class in self.standard_modules.values()) and (module_class in dock_widget_area.keys()):
            self.addDockWidget(dock_widget_area[module_class], m)

        return self.running_modules[-1]

    def get_module(self, module_name: str, hide=False):
        return self.run_module(module_name, hide)

    def update_available_inputs(self):
        for m in self.running_modules:
            if hasattr(m, 'update_available_inputs'):
                m.update_available_inputs()

    def initialize_menubar_triggers(self):
        self.ui.actionBatch_Manager.triggered.connect(self.start_batch_manager)

        self.vi = ViewerUtils(self._viewer)

        self.ui.actionDump_Work_Environment.triggered.connect(self.vi.discard_workEnv)

        self.image_menu = ImageMenu(self.vi)

        self.ui.actionReset_Scale.triggered.connect(self.image_menu.reset_scale)
        self.ui.actionMeasure.triggered.connect(self.image_menu.action_measure_line_invoked)
        self.ui.actionResize.triggered.connect(self.image_menu.resize)
        self.ui.actionCrop.triggered.connect(self.image_menu.crop)

        self.ui.actionMean.triggered.connect(self.image_menu.mean_projection)
        self.ui.actionMax.triggered.connect(self.image_menu.max_projection)
        self.ui.actionStandard_Deviation.triggered.connect(self.image_menu.std_projection)
        self.ui.actionClose_all_projection_windows.triggered.connect(self.image_menu.close_projection_windows)

    def get_batch_manager(self) -> QtWidgets.QWidget:
        return get_window_manager().get_batch_manager()

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
            QtWidgets.QMessageBox.question(self, 'No project open', 'You must have a project open to add to it')
            return

        if len(self.viewer_reference.workEnv.roi_manager.roi_list) == 0:
            QtWidgets.QMessageBox.warning(self, 'No curves', 'You do not have any curves in your work environment')
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

    def closeEvent(self, QCloseEvent):
        if not self.vi.discard_workEnv():
            QCloseEvent.ignore()
        else:
            self.vi._clear_workEnv()
            QCloseEvent.accept()

    def open_from_dataframe(self, proj_path: str,
                            df: pd.DataFrame = None,
                            row: pd.Series = None,
                            sample_id: str = None,
                            uuid_curve: Union[str, UUID_type] = None):

        if df is not None:
            if uuid_curve is not None:
                row = df[df.uuid_curve == uuid_curve]

            elif sample_id is not None:
                rows = df[df.SampleID == sample_id]
                row = rows.iloc[0]

        if row is not None:

            tp = row['ImgPath']
            if isinstance(tp, pd.Series):
                tp = tp.item()

            tiff_path = os.path.join(proj_path, tp)

            pp = row['ImgInfoPath']
            if isinstance(pp, pd.Series):
                pp = pp.item()

            pik_path = os.path.join(proj_path, pp)

            s = row['SampleID']
            if isinstance(s, pd.Series):
                s = s.item()

            roi_state = row['ROI_State']
            if isinstance(roi_state, pd.Series):
                roi_state = roi_state.item()

            if roi_state['roi_type'] == 'CNMFROI':
                cnmf_idx = roi_state['cnmf_idx']
                roi_index = ('cnmf_idx', cnmf_idx)
            else:
                roi_index = None

            self._open_from_dataframe(tiff_path, pik_path, roi_index=roi_index, sample_id=s)
            return

        else:
            raise ValueError('Must specify either df and sample_id/uuid_curve or supply the row (pd.Series)')

    def _open_from_dataframe(self, tiff_path: str, pik_path: str, roi_index: Optional[tuple] = None,
                             sample_id: Optional[str] = None):
        setConfigOptions(imageAxisOrder='row-major')
        self.vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=pik_path, tiff_path=tiff_path)
        self.vi.update_workEnv()

        self.vi.viewer.workEnv.restore_rois_from_states()
        self.vi.viewer.workEnv.changed_items.clear()

        if roi_index is not None:
            roi_list = self.vi.viewer.workEnv.roi_manager.roi_list
            if roi_index[0] == 'cnmf_idx':
                c_idx = roi_index[1]
                list_index = [r.cnmf_idx for r in roi_list].index(c_idx)
            elif roi_index[0] == 'list_index':
                list_index = roi_index[1]
            else:
                raise ValueError('roi_index must be either a cnmf index or the direct list index of the ROI_List object')

            roi_list.list_widget.setCurrentRow(list_index)
            rm: roi_manager.ModuleGUI = self.get_module('roi_manager')
            if rm.ui.checkBoxShowAll.isChecked():
                rm.ui.checkBoxShowAll.click()
            rm.hide()

            # dirty fix for now to get the plot to draw
            rm.set_curveplot_datatype()

        if sample_id is not None:
            self.vi.viewer.ui.label_curr_img_seq_name.setText(sample_id)

        self.vi.viewer.workEnv.saved = True

    def dragEnterEvent(self, QDragEnterEvent):
        if QDragEnterEvent.mimeData().hasUrls():
            QDragEnterEvent.accept()
        else:
            QDragEnterEvent.ignore()

    def dropEvent(self, ev):
        files = ev.mimeData().urls()
        if len(files) == 1:
            file = files[0].path()
        else:
            return

        if file.endswith('.tiff') or file.endswith('.tif'):
            tio = self.get_module('tiff_io')
            assert isinstance(tio, tiff_io.ModuleGUI)
            tio.tiff_file_path = file
            tio.check_meta_path()
