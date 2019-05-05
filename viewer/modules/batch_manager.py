#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerInterface
from ..core.viewer_work_environment import ViewerWorkEnv
from common import configuration
from .pytemplates.batch_manager_pytemplate import *
import json
import pandas
from .batch_run_modules import * #DO NOT REMOVE THIS LINE
import uuid
import numpy as np
# from .common import BatchRunInterface
import pickle
import tifffile
import os
from stat import S_IEXEC
# from multiprocessing import Queue
from functools import partial
from collections import deque
import psutil
from signal import SIGKILL
import traceback
from misc_widgets.list_widget_dialog import ListWidgetDialog
from common import window_manager
from glob import glob
from multiprocessing import Pool
from uuid import UUID as UUIDType
from datetime import datetime
from time import time


class ModuleGUI(QtWidgets.QWidget):
    """GUI for the Batch Manager"""
    listwchanged = QtCore.pyqtSignal()

    def __init__(self, parent, run_batch: list = None):
        print('starting batch mananger')
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        date = datetime.fromtimestamp(time())
        time_str = date.strftime('%Y%m%d') + '_' + date.strftime('%H%M%S')
        self.ui.lineEditWorkDir.setText('/work/' + os.environ['USER'] + '/' + time_str)
        self.ui.checkBoxWorDir.setChecked(True)
        self.ui.lineEditWorkDir.setEnabled(True)
        self.working_dir = self.ui.lineEditWorkDir.text()

        self.ui.listwBatch.itemDoubleClicked.connect(self.list_widget_item_double_clicked_slot)

        self.ui.btnStart.clicked.connect(self.process_batch)
        self.ui.btnStart.setDisabled(True)
        self.ui.btnStartAtSelection.clicked.connect(lambda: self.process_batch(
            start_ix=self.ui.listwBatch.indexFromItem(self.ui.listwBatch.currentItem()).row()))
        self.ui.btnStartAtSelection.setDisabled(True)

        self.ui.btnAbort.clicked.connect(self._terminate_qprocess)
        self.ui.btnAbort.setDisabled(True)
        self.ui.btnOpen.clicked.connect(self.open_batch)
        self.ui.btnDelete.clicked.connect(self.del_item)
        self.ui.btnViewInput.clicked.connect(self.btn_view_input_slot)
        self.ui.btnNew.clicked.connect(self.create_new_batch)

        listwmodel = self.ui.listwBatch.model()
        listwmodel.rowsInserted.connect(self.listwchanged.emit)
        listwmodel.rowsRemoved.connect(self.listwchanged.emit)

        self.ui.scrollAreaStdOut.setStyleSheet('background-color: #131926')
        self.ui.textBrowserStdOut.setTextColor(QtGui.QColor('#b7b7b7'))

        self.ui.scrollAreaStdOut.hide()
        self.resize(1200, 650)
        self.ui.listwBatch.currentItemChanged.connect(self.show_item_info)

        self.output_widgets = []
        self.df = pandas.DataFrame()
        self.init_batch(run_batch)

        self.ui.btnCompress.clicked.connect(self.compress_all)

    def compress_all(self):
        if QtWidgets.QMessageBox.warning(self, 'Compress Warning',
                                         'YOU CANNOT ABORT THIS PROCESS ONCE IT STARTS, PROCEED?',
                                         QtWidgets.QMessageBox.Yes,
                                         QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return

        # t = (psutil.virtual_memory().available / (10**9)) / ()

        n, ok = QtWidgets.QInputDialog.getInt(self, 'Number of threads to use', 'Enter number of threads to use. \nDo not use more than: available ram / (size of largest image * 2)', 5, 1, 7, 1, QtWidgets.QInputDialog.Cancel)

        if not ok:
            return

        uuids = self.df.uuid[self.df.compress == False]

        l = []

        for u in uuids:
            l += glob(self.batch_path + '/*' + str(u) + '*.tiff')

        p = Pool(n)

        p.map(self._compress_tiff, l)

    def _compress_tiff(self, path):
        imgseq = tifffile.imread(path)

        backup_path = path + '_bak'
        os.rename(path, backup_path)

        tifffile.imsave(path, data=imgseq.astype(np.uint16), compress=1)

        os.remove(backup_path)

    def export_submission_scripts(self):
        pass

    def init_batch(self, run_batch):
        if run_batch is None:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose the location of an existing batch folder '
                                                                    'or a location for a new batch folder')
            if path == '':
                return
        else:
            path = run_batch[0]
            print('Opening batch: ' + path)

        dfpath = path + '/dataframe.batch'
        if os.path.isfile(dfpath):
            self.open_batch_dir(path)

        else:
            self.create_new_batch_dir(path)

        self.ui.btnStart.setEnabled(True)
        self.ui.btnStartAtSelection.setEnabled(True)

        if run_batch is not None:
            print('Running from item ' + run_batch[1])
            ix = self.df.index[self.df['uuid'] == UUIDType(run_batch[1])]
            i = int(ix.to_native_types()[0])
            self.process_batch(start_ix=i, clear_viewers=True)

    def create_new_batch(self):
        if self.ui.listwBatch.count() > 0:
            if QtWidgets.QMessageBox.warning(self, 'Create Batch?', 'Close the current batch and open another one?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a batch')
        if path == '':
            return

        if any(s in path for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid path',
                                          'Batch path cannot contain spaces or special characters')
            return

        self.create_new_batch_dir(path)

    def create_new_batch_dir(self, path: str):
        name, start = QtWidgets.QInputDialog.getText(self, '', 'Batch Name:', QtWidgets.QLineEdit.Normal, '')

        if any(s in name for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid name',
                                          'Batch name can only contain alphanumeric characters')
            return

        if start and name != '':
            batch_path = path + '/' + name
            os.makedirs(batch_path)
            self.batch_path = batch_path
        else:
            return
        self.ui.listwBatch.clear()

        self.df = pandas.DataFrame(columns=['module', 'input_params', 'output', 'info', 'uuid', 'compressed'])
        self.df.to_pickle(self.batch_path + '/dataframe.batch')

        self.setWindowTitle('Batch Manager: ' + os.path.basename(self.batch_path))
        self.ui.labelBatchPath.setText(os.path.dirname(self.batch_path))
        self.show()

    def btn_view_input_slot(self):
        # TODO: This should ask which viewer to display output in if more than 2 are open
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        viewers = configuration.window_manager.viewers

        if len(configuration.window_manager.viewers) > 1:
            self.lwd = ListWidgetDialog()
            self.lwd.listWidget.addItems([str(i) for i in range(len(viewers))])
            self.lwd.label.setText('Viewer to show input in:')
            self.lwd.btnOK.clicked.connect(partial(self.show_input_in_viewer, viewers, r, UUID))
        else:
            self.show_input_in_viewer(viewers[0], r, UUID)

    def show_input_in_viewer(self, viewers, r: pandas.Series, UUID: uuid.UUID):
        """
        :param  r:  Row of batch DataFrame corresponding to the selected item
        """
        if not isinstance(viewers, window_manager.WindowClass):
            viewer = viewers.viewer_reference
        else:
            if self.lwd.listWidget.currentItem() is None:
                QtWidgets.QMessageBox.warning(self, 'Nothing selected', 'You must select from the list')
                return
            i = int(self.lwd.listWidget.currentItem().data(0))
            viewer = viewers[i].viewer_reference

        vi = ViewerInterface(viewer_reference=viewer)

        if r['input_item'].item() is None:
            if not vi.discard_workEnv():
                return
            pikpath = self.batch_path + '/' + str(UUID) + '_workEnv.pik'
            tiffpath = self.batch_path + '/' + str(UUID) + '.tiff'
            vi.viewer.status_bar_label.showMessage('Please wait, loading input into work environment...')
            if os.path.isfile(pikpath) and os.path.isfile(tiffpath):
                vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=pikpath, tiff_path=tiffpath)
                vi.update_workEnv()
                vi.enable_ui(True)
                vi.viewer.status_bar_label.showMessage('Done! loaded input into work environment.')
                vi.viewer.ui.label_curr_img_seq_name.setText('Input of item: ' + r['name'].item())

            else:
                QtWidgets.QMessageBox.warning(self, 'Input file does not exist',
                                              'The input files do not exist for this item.')
                vi.viewer.status_bar_label.showMessage('Error, could not load input into work environment.')
        if hasattr(self, 'lwd'):
            self.lwd.deleteLater()

    def list_widget_item_double_clicked_slot(self, s: QtWidgets.QListWidgetItem):
        """Calls subclass of BatchRunInterface.show_output()"""
        self.ui.scrollAreaOutputInfo.show()
        item_txt = s.text()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        module = r['module'].item()
        m = globals()[module]

        output = self.get_batch_item_output(UUID)

        if output is None:
            return

        if output['status'] == 1:
            if len(configuration.window_manager.viewers) > 1:
                viewers = configuration.window_manager.viewers

                self.lwd = ListWidgetDialog()
                self.lwd.listWidget.addItems([str(i) for i in range(len(viewers))])
                self.lwd.label.setText('Viewer to use for output:')
                self.lwd.btnOK.clicked.connect(partial(self.show_item_output, m, viewers, UUID))
            else:
                self.show_item_output(m, configuration.window_manager.viewers[0], UUID)

    def show_item_output(self, module, viewers, UUID: uuid.UUID):
        """
        :param module: The module name under /batch_run_modules that the batch item is from
        """
        if len(self.output_widgets) > 3:
            try:
                self.output_widgets[0].close()
            except:
                pass

        if not isinstance(viewers, window_manager.WindowClass):
            viewer = viewers.viewer_reference
        else:
            if self.lwd.listWidget.currentItem() is None:
                QtWidgets.QMessageBox.warning(self, 'Nothing selected', 'You must select from the list')
                return
            i = int(self.lwd.listWidget.currentItem().data(0))
            viewer = viewers[i].viewer_reference
        try:
            self.output_widgets.append(module.Output(self.batch_path, UUID, viewer))
        except:
            QtWidgets.QMessageBox.warning(self, 'Error showing item output',
                                          'The following error occured while '
                                          'trying to load the output of the chosen item\n' + traceback.format_exc())
        if hasattr(self, 'lwd'):
            self.lwd.deleteLater()

    def show_item_info(self, s: QtWidgets.QListWidgetItem):
        """Shows any info (such as the batch module's params) in the meta-info label"""
        if not isinstance(s, QtWidgets.QListWidgetItem):
            return
        UUID = s.data(3)
        row = self.df.loc[self.df['uuid'] == UUID]
        meta = row['info'].item()
        info = "\n".join([": ".join([key, str(val)]) for key, val in meta.items()])

        self.ui.textBrowserItemInfo.setText(str(UUID) + '\n\n' + info)

        output = self.get_batch_item_output(UUID)

        self.ui.textBrowserOutputInfo.setText('')

        if output is None:
            self.ui.textBrowserOutputInfo.setText('Output file does not exist for selected item')
            return
        else:
            self.ui.textBrowserOutputInfo.setText(str(output))

    def disable_ui_buttons(self, b):
        self.ui.btnStart.setDisabled(b)
        self.ui.btnStartAtSelection.setDisabled(b)
        self.ui.btnDelete.setDisabled(b)
        self.ui.btnAbort.setEnabled(b)

    def process_batch(self, start_ix=0, clear_viewers=False):
        """Process everything in the batch by calling subclass of BatchRunInterface.process() for all items in batch"""

        self.ui.checkBoxWorDir.setDisabled(True)
        self.ui.lineEditWorkDir.setDisabled(True)

        if len(self.df.index) == 0:
            pass

            QtWidgets.QMessageBox.warning(self, 'Nothing to run', 'Nothing in the batch to run!')
            return

        if configuration.sys_cfg['PATHS']['env'] == '':
            QtWidgets.QMessageBox.warning(self, 'Environment not set', 'You must set the environment in System Configuration')
            return

        if configuration.sys_cfg['PATHS']['caiman'] == '':
            if QtWidgets.QMessageBox.question(self, 'CaImAn dir not set', 'You have not set the CaImAn directory. '
                                                                          'Without this CaImAn modules will not run. '
                                                                          'Do you wish to continue anyways?',
                                              QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        if not clear_viewers:
            if QtWidgets.QMessageBox.question(self, 'Clear all viewers?',
                                                  'Would you like to clear all viewer work '
                                                  'environments before starting the batch?',
                                                  QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                self._clear_viewers()
        else:
            self._clear_viewers()

        self.current_batch_item_index = start_ix - 1
        self.disable_ui_buttons(True)
        # self.run_next_item()
        self.ui.scrollAreaStdOut.show()
        self.ui.scrollAreaOutputInfo.show()
        self.current_std_out = deque(maxlen=100)
        self.run_batch_item()

    def set_list_widget_item_color(self, ix: int, color: str):
        if color == 'orange':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#ffb347')))
        elif color == 'green':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#77dd77')))
        elif color == 'red':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#fe0d00')))
        elif color == 'blue':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#85e3ff')))

    def _clear_viewers(self):
        for viewer in configuration.window_manager.viewers:
            vi = ViewerInterface(viewer.viewer_reference)
            vi.discard_workEnv()

    @QtCore.pyqtSlot()
    def run_batch_item(self):
        if self.current_batch_item_index > -1:
            UUID = self.df.iloc[self.current_batch_item_index]['uuid']
            output = self.get_batch_item_output(UUID)

            if output is None:
                self.set_list_widget_item_color(ix=self.current_batch_item_index, color='orange')

            elif output['status']:
                if 'output_files' in output.keys() and self.ui.checkBoxWorDir.isChecked() and os.path.isdir(self.working_dir):
                    output_files_list = output['output_files']
                    shell_str = '#!/bin/bash\n'

                    for of in output_files_list:
                        src = self.working_dir + '/' + of
                        dst = self.batch_path + '/' + of
                        shell_str += 'mv ' + src + ' ' + dst + '\n'

                    shell_str += 'rm ' + self.working_dir + '/*' + str(UUID) + '*'
                    move_sh_path = self.working_dir + '/move.sh'

                    with(open(move_sh_path, 'w')) as sh_mv_f:
                        sh_mv_f.write(shell_str)

                    mv_st = os.stat(move_sh_path)
                    os.chmod(move_sh_path, mv_st.st_mode | S_IEXEC)

                    self.move_process = QtCore.QProcess()
                    self.move_process.setWorkingDirectory(self.working_dir)
                    self.move_process.finished.connect(partial(self.set_list_widget_item_color, self.current_batch_item_index, 'green'))
                    self.move_process.start(move_sh_path)
                    self.set_list_widget_item_color(ix=self.current_batch_item_index, color='blue')

                else:
                    self.set_list_widget_item_color(ix=self.current_batch_item_index, color='green')

            else:
                self.set_list_widget_item_color(ix=self.current_batch_item_index, color='red')

        self.current_batch_item_index += 1
        self.ui.progressBar.setValue(int(self.current_batch_item_index / len(self.df.index) * 100))
        if self.current_batch_item_index == len(self.df.index):
            self.ui.progressBar.setValue(100)
            self.disable_ui_buttons(False)
            self.ui.checkBoxWorDir.setEnabled(True)
            self.ui.lineEditWorkDir.setEnabled(True)
            QtWidgets.QMessageBox.information(self, 'Batch is done!', 'Yay, your batch has finished processing!')
            return

        r = self.df.iloc[self.current_batch_item_index]
        m = globals()[r['module']]
        module_path = os.path.abspath(m.__file__)

        self.process = QtCore.QProcess()
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        # self.process.readyReadStandardError.connect(partial(self.print_qprocess_std_err, self.process))
        self.process.readyReadStandardOutput.connect(partial(self.print_qprocess_std_out, self.process))

        self.process.finished.connect(self.run_batch_item)
        sh_file = self.batch_path + '/' + 'run.sh'

        if configuration.sys_cfg['PATHS']['env_type'] == 'anaconda':
            env_path = configuration.sys_cfg['PATHS']['env']
            anaconda_dir =  os.path.dirname(os.path.dirname(os.path.dirname(env_path)))
            env_name = os.path.basename(os.path.normpath(env_path))
            env_activation = 'export PATH=' + anaconda_dir +':$PATH\nsource activate ' + env_name
        elif configuration.sys_cfg['PATHS']['env_type'] == 'virtual':
            env_path = configuration.sys_cfg['PATHS']['env']
            env_activation = 'source ' + env_path + '/bin/activate'
        else:	
            raise ValueError('Invalid configruation value for environment path. Please check the entry for "env" under'
                             'section [PATH] in the config file.')
        caiman_path = configuration.sys_cfg['PATHS']['caiman']

        if self.ui.checkBoxWorDir.isChecked():
            try:
                self.working_dir = self.ui.lineEditWorkDir.text()
                if not os.path.isdir(self.working_dir):
                    os.makedirs(self.working_dir)
                elif os.path.isfile(self.working_dir):
                    QtWidgets.QMessageBox.warning(self, 'Choose different dir', 'Choose a different directory')
            except PermissionError:
                QtWidgets.QMessageBox.warning(self, 'Permission denied',
                                              'You do not appear to have permission to write to the chosen work'
                                              'directory.')
                return

            cp_to_work_dir_str = 'cp ' + self.batch_path + '/*' + str(r['uuid']) + '* ' + self.working_dir

        else:
            self.working_dir = self.batch_path
            cp_to_work_dir_str = ''


        with open(sh_file, 'w') as sf:
            sf.write('#!/bin/bash\n' +
                     env_activation + '\n' +
                     'export PYTHONPATH="' + caiman_path + '"\n' +
                     'export MKL_NUM_THREADS=1\n' +
                     'export OPENBLAS_NUM_THREADS=1\n' +
                     'export USE_CUDA=' + configuration.sys_cfg['HARDWARE']['USE_CUDA'] + '\n' +
                     cp_to_work_dir_str + '\n' +
                     'python "' +
                     module_path + '" "' +
                     self.working_dir + '" "' +
                     str(r['uuid']) + '" ' +
                     configuration.sys_cfg['HARDWARE']['n_processes'] + '\n')

        st = os.stat(sh_file)
        os.chmod(sh_file, st.st_mode | S_IEXEC)
        self.process.setWorkingDirectory(self.working_dir)
        self.process.start(sh_file)
        self.ui.listwBatch.item(self.current_batch_item_index).setBackground(QtGui.QBrush(QtGui.QColor('yellow')))

    def create_run_script(self, parent_dir):
        pass

    def get_batch_item_output(self, UUID: uuid.UUID):
        out_file = self.working_dir + '/' + str(UUID) + '.out'
        if os.path.isfile(out_file):
            output = json.load(open(out_file, 'r'))
            return output
        
        out_file = self.batch_path + '/' + str(UUID) + '.out'
        
        if os.path.isfile(out_file):
            output = json.load(open(out_file, 'r'))
            return output
        else:
            return None

    def _terminate_qprocess(self):
        try:
            py_proc = psutil.Process(self.process.pid()).children()[0].pid
        except psutil.NoSuchProcess:
            return
        children = psutil.Process(py_proc).children()
        os.kill(py_proc, SIGKILL)
        for child in children:
            os.kill(child.pid, SIGKILL)

    def print_qprocess_std_out(self, std_out):
        self.current_std_out.append((str(std_out.readAllStandardOutput())))
        self.ui.textBrowserStdOut.append('\n'.join(self.current_std_out))

    def add_item(self, module: str, viewer_reference, input_workEnv: ViewerWorkEnv, input_params: dict, name='', info=''):

        """
        :param  module:         The module to run from /batch_run_modules.

        :param viewer_reference: Viewer to communicate with
        :type  viewer_reference: ImageView

        :param  name:           A name for the batch item

        :param  input_workEnv:  Input workEnv that the module will use

        :param  input_params:   Input params that the module will use.
                                Depends on your subclass of BatchRunInterface.process() method
        :type   input_params:   dict

        :param  info:           A dictionary with any metadata information to display in the scroll area label.
        """
        if input_workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Work Environment is empty!', 'The current work environment is empty,'
                                                                              ' nothing to add to the batch!')
            return
        vi = ViewerInterface(viewer_reference)
        UUID = uuid.uuid4()

        if module == 'CNMFE' or module == 'caiman_motion_correction' or module == 'CNMF':
            filename = self.batch_path + '/' + str(UUID) + '.tiff'
            tifffile.imsave(filename, data=input_workEnv.imgdata.seq.T, bigtiff=True)
            input_workEnv.to_pickle(self.batch_path, filename=str(UUID) + '_workEnv', save_img_seq=False)

        pickle.dump(input_params, open(self.batch_path + '/' + str(UUID) + '.params', 'wb'), protocol=4)

        input_params = np.array(input_params, dtype=object)
        meta = np.array(info, dtype=object)

        self.df = self.df.append({'module': module,
                                  'name': name,
                                  'input_item': None,
                                  'input_params': input_params,
                                  'info': info,
                                  'uuid': UUID,
                                  'output': None,
                                  }, ignore_index=True)

        assert isinstance(self.df, pandas.DataFrame)

        self.ui.listwBatch.addItem(module + ': ' + name)
        n = self.ui.listwBatch.count()
        item = self.ui.listwBatch.item(n - 1)
        assert isinstance(item, QtWidgets.QListWidgetItem)
        item.setData(3, UUID)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

    def del_item(self):
        """Delete an item from the batch and any corresponding dependents of the item's output"""
        if QtWidgets.QMessageBox.question(self, 'Confirm deletion',
                                          'Are you sure you want to delete the selected item from the batch? '
                                          'This will also remove ALL files associated to the item',
                                          QtWidgets.QMessageBox.Yes,
                                          QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        assert isinstance(self.df, pandas.DataFrame)

        dependents = self.df.loc[self.df['input_item'] == UUID]
        if not dependents.empty:
            if QtWidgets.QMessageBox.warning(self, 'This item has dependents!',
                                             'There are other items in your batch list that are dependent on the item you '
                                             'have selected to delete. If you delete this item from the batch then all '
                                             'dependent items will also be deleted.\n\nDo you still wish to continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return

            for item in self.ui.listwBatch.items():
                if item.data(3) == UUID:
                    ix = self.ui.listwBatch.indexFromItem(item).row()
                    self.ui.listwBatch.takeItem(ix)

            self.df = self.df.loc[self.df['input_item'] != UUID]

        self.df = self.df[self.df['uuid'] != UUID]
        self.df.reset_index(drop=True, inplace=True)

        ix = self.ui.listwBatch.indexFromItem(s).row()
        self.ui.listwBatch.takeItem(ix)

        for file in glob(self.batch_path + '/*' + str(UUID) + '*'):
            os.remove(file)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

    def save_batch(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Batch as', '', '(*.batch)')
        if path == '':
            return

        if path[0].endswith('.batch'):
            path = path[0]
        else:
            path = path[0] + '.batch'

        try:
            d = {'batch_path': self.batch_path,
                 'df': self.df}
            pickle.dump(d, open(path[0]))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

    def open_batch(self):
        if self.ui.listwBatch.count() > 0:
            if QtWidgets.QMessageBox.warning(self, 'Open Batch', 'Close the current batch and open a new one?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Batch', directory='/home/')
        if path == '':
            return

        if any(s in path for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid batch path', 'Batch path can only contain alphanumeric characters')
            return
        self.open_batch_dir(path)

    def open_batch_dir(self, path: str):
        dfpath = path + '/dataframe.batch'
        if not os.path.isfile(dfpath):
            QtWidgets.QMessageBox.warning(self, 'Invalid batch dir',
                                          'The selected directory does not appear to be a valid  batch directory '
                                          'since it does not contain a "dataframe.batch" file')
            return
        try:
            df = pandas.read_pickle(dfpath)
            assert isinstance(df, pandas.DataFrame)
            self.df = df
            if 'compressed' not in self.df.columns:
                self.df['compressed'] = False * self.df.index.size
            self.batch_path = path
            self.setWindowTitle('Batch Manager: ' + os.path.basename(self.batch_path))
            self.ui.labelBatchPath.setText(os.path.dirname(self.batch_path))

            self.ui.listwBatch.clear()

            for ix, r in self.df.iterrows():
                self.ui.listwBatch.addItem(r['module'] + ': ' + r['name'])
                n = self.ui.listwBatch.count()
                item = self.ui.listwBatch.item(n - 1)
                assert isinstance(item, QtWidgets.QListWidgetItem)
                item.setData(3, r['uuid'])

                output = self.get_batch_item_output(r['uuid'])

                if output is None:
                    continue
                elif output['status']:
                    self.ui.listwBatch.item(n - 1).setBackground(
                        QtGui.QBrush(QtGui.QColor('#77dd77'))) # green
                else:
                    self.ui.listwBatch.item(n - 1).setBackground(
                        QtGui.QBrush(QtGui.QColor('#fe0d00'))) # red

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!',
                                          'Could not open the dataframe file.\n' + traceback.format_exc())
            return
