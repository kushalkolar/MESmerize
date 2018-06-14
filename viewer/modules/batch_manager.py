#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .common import ViewerInterface
from ..core.viewer_work_environment import ViewerWorkEnv
from settings import configuration
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from .pytemplates.batch_manager_pytemplate import *
import json
import pandas
from .batch_run_modules import *
import uuid
import numpy as np
# from .common import BatchRunInterface
import pickle
import tifffile
import time
from datetime import datetime
import os
from stat import S_IEXEC
# from multiprocessing import Queue
from functools import partial
from collections import deque
import psutil
from signal import SIGKILL
import traceback


class ModuleGUI(QtWidgets.QDockWidget):
    """GUI for the Batch Manager"""
    listwchanged = QtCore.pyqtSignal()

    def __init__(self, parent, viewer_reference):
        self.vi = ViewerInterface(viewer_reference)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.listwBatch.itemDoubleClicked.connect(self.show_item_output)

        self.ui.btnStart.clicked.connect(self.process_batch)
        self.ui.btnStartAtSelection.clicked.connect(lambda: self.process_batch(start_ix=self.ui.listwBatch.indexFromItem(self.ui.listwBatch.currentItem()).row()))

        self.ui.btnAbort.clicked.connect(self._terminate_qprocess)
        self.ui.btnAbort.setDisabled(True)
        self.ui.btnOpen.clicked.connect(self.open_batch)
        self.ui.btnDelete.clicked.connect(self.del_item)
        self.ui.btnViewInput.clicked.connect(self.show_input)

        listwmodel = self.ui.listwBatch.model()
        listwmodel.rowsInserted.connect(self.listwchanged.emit)
        listwmodel.rowsRemoved.connect(self.listwchanged.emit)

        self.df = pandas.DataFrame(columns=['module', 'input_params', 'output', 'info', 'uuid'])

        self.batch_path = configuration.proj_path + '/batches' + '/' + \
                          datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
        os.makedirs(self.batch_path)

        self.setWindowTitle('Batch Manager: ' + self.batch_path.split('/')[-1])

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

        self.ui.scrollAreaStdOut.setStyleSheet('background-color: #131926')
        # self.ui.textBrowserStdOut.setTextBackgroundColor(QtGui.QColor(131926))
        self.ui.textBrowserStdOut.setTextColor(QtGui.QColor('#b7b7b7'))

        self.ui.scrollAreaStdOut.hide()
        self.resize(1200, 650)
        self.ui.listwBatch.currentItemChanged.connect(self.show_item_info)

        self.output_widgets = []

    def show_input(self, viewer_reference):
        # TODO: This should ask which viewer to display output in if more than 2 are open
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        if r['input_item'].item() is None:
            if not self.vi.discard_workEnv():
                return
            pikpath = self.batch_path + '/' + str(UUID) + '_workEnv.pik'
            tiffpath = self.batch_path + '/' + str(UUID) + '.tiff'
            self.vi.viewer.status_bar_label.setText('Please wait, loading input into work environment...')
            if os.path.isfile(pikpath) and os.path.isfile(tiffpath):
                self.vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pikPath=pikpath, tiffPath=tiffpath)
                self.vi.update_workEnv()
                self.vi.enable_ui(True)
            else:
                QtWidgets.QMessageBox.warning(self, 'Input file does not exist',
                                              'The input files do not exist for this item.')
                self.vi.viewer.status_bar_label.clear()

    def show_item_output(self, s: QtWidgets.QListWidgetItem):
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
            self.output_widgets.append(m.Output(self.batch_path, UUID, self.vi.viewer))

    def show_item_info(self, s: QtWidgets.QListWidgetItem):
        """Shows any info (such as the batch module's params) in the meta-info label"""
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
            self.ui.textBrowserOutputInfo.setText(output['output_info'])

    def disable_ui_buttons(self, b):
        self.ui.btnStart.setDisabled(b)
        self.ui.btnStartAtSelection.setDisabled(b)
        self.ui.btnDelete.setDisabled(b)
        self.ui.btnAbort.setEnabled(b)

    def process_batch(self, start_ix=0):
        # TODO: This should ask if user wants to clear all viewer work environments before running the batch
        """Process everything in the batch by calling subclass of BatchRunInterface.process() for all items in batch"""

        if len(self.df.index) == 0:
            pass

            QtWidgets.QMessageBox.warning(self, 'Nothing to run', 'Nothing in the batch to run!')
            return

        if configuration.sys_cfg['BATCH']['anaconda_env'] == '':
            QtWidgets.QMessageBox.warning(self, 'Anaconda env not set', 'You must set the name of the anaconda '
                                                                        'environment which you wish to use with '
                                                                        'QProcess')
            return

        if configuration.sys_cfg['PATHS']['anaconda3'] == '':
            QtWidgets.QMessageBox.warning(self, 'Anaconda directory not set', 'You must set the anaconda directory')
            return

        if configuration.sys_cfg['PATHS']['caiman'] == '':
            if QtWidgets.QMessageBox.question(self, 'CaImAn dir not set', 'You have not set the CaImAn directory. '
                                                                          'Without this CaImAn modules will not run. '
                                                                          'Do you wish to continue anyways?',
                                              QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return

        self.vi.discard_workEnv()
        self.current_batch_item_index = start_ix -1
        self.disable_ui_buttons(True)
        # self.run_next_item()
        self.ui.scrollAreaStdOut.show()
        self.ui.scrollAreaOutputInfo.show()
        self.current_std_out = deque(maxlen=100)
        self.run_batch_item()

    @QtCore.pyqtSlot()
    def run_batch_item(self):
        if self.current_batch_item_index > -1:
            UUID = self.df.iloc[self.current_batch_item_index]['uuid']
            output = self.get_batch_item_output(UUID)
            if output is None:
                self.ui.listwBatch.item(self.current_batch_item_index).setBackground(
                    QtGui.QBrush(QtGui.QColor('orange')))

            elif output['status']:
                self.ui.listwBatch.item(self.current_batch_item_index).setBackground(
                    QtGui.QBrush(QtGui.QColor('green')))
            else:
                self.ui.listwBatch.item(self.current_batch_item_index).setBackground(
                    QtGui.QBrush(QtGui.QColor('red')))

        self.current_batch_item_index += 1
        self.ui.progressBar.setValue(int(self.current_batch_item_index / len(self.df.index) * 100))
        if self.current_batch_item_index == len(self.df.index):
            self.ui.progressBar.setValue(100)
            self.disable_ui_buttons(False)
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

        with open(sh_file, 'w') as sf:
            sf.write('#!/bin/bash\n'
                     'export PATH="' + configuration.sys_cfg['PATHS']['anaconda3'] + ':$PATH"\n'
                     'source activate ' + configuration.sys_cfg['BATCH']['anaconda_env'] + '\n'
                     'export PYTHONPATH="' + configuration.sys_cfg['PATHS']['caiman'] + '"\n'
                     'export MKL_NUM_THREADS=1\n' +
                     'export OPENBLAS_NUM_THREADS=1\n'
                     'python "' +
                     module_path + '" "' +
                     self.batch_path + '" "' +
                     str(r['uuid']) + '" ' +
                     configuration.sys_cfg['HARDWARE']['n_processes'] +
                     '\n')
        st = os.stat(sh_file)
        os.chmod(sh_file, st.st_mode | S_IEXEC)
        self.process.setWorkingDirectory(self.batch_path)
        self.process.start(sh_file)
        self.ui.listwBatch.item(self.current_batch_item_index).setBackground(QtGui.QBrush(QtGui.QColor('yellow')))

    def get_batch_item_output(self, UUID):
        out_file = self.batch_path + '/' + str(UUID) + '.out'
        if os.path.isfile(out_file):
            output = json.load(open(out_file, 'r'))
            return output
        else:
            return None

    def _terminate_qprocess(self):
        py_proc = psutil.Process(self.process.pid()).children()[0].pid
        children = psutil.Process(py_proc).children()
        os.kill(py_proc, SIGKILL)
        for child in children:
            os.kill(child.pid, SIGKILL)

    def print_qprocess_std_out(self, std_out):
        self.current_std_out.append((str(std_out.readAllStandardOutput())))
        self.ui.textBrowserStdOut.append('\n'.join(self.current_std_out))

    def add_item(self, module, viewer_reference, input_workEnv, input_params, name='', info=''):
        # TODO: This should utilize the work environment from the viewer_reference that is passed

        """
        :param  module:         The module to run, based on common.BatchRunInterface.
        :type   module:         str

        :param viewer_reference:ViewerWorkEnv to communicate with
        :type  viewer_reference:

        :param  name:           A name for the batch item
        :type   name:           str

        :param  input_workEnv:  Input workEnv that the module will use
        :type   input_workEnv:  viewerWorkEnv

        :param  input_params:   Input params that the module will use.
                                Depends on your subclass of BatchRunInterface.process() method
        :type   input_params:   dict

        :param  info:           A dictionary with any metadata information to display in the scroll area label.
        :type   info:           dict
        """
        if input_workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Work Environment is empty!', 'The current work environment is empty,'
                                                                              ' nothing to add to the batch!')
            return
        self.vi.viewer.status_bar_label.setText('Adding to batch, please wait...')
        UUID = uuid.uuid4()

        if module == 'CNMFE' or module == 'caiman_motion_correction':
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

        self.ui.listwBatch.addItem(module + ': ' + name)
        n = self.ui.listwBatch.count()
        item = self.ui.listwBatch.item(n - 1)
        assert isinstance(item, QtWidgets.QListWidgetItem)
        item.setData(3, UUID)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

        self.vi.viewer.status_bar_label.setText('Added item to batch!')

    def del_item(self):
        """Delete an item from the batch and any corresponding dependents of hte item's output"""
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

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

        self.df = self.df.loc[self.df['uuid'] != UUID]

        ix = self.ui.listwBatch.indexFromItem(s).row()
        self.ui.listwBatch.takeItem(ix)

    def save_batch(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Batch as', '', '(*.batch)')
        if path == '':
            return

        if path[0].endswith('.batch'):
            path = path[0]
        else:
            path = path[0] + '.batch'

        try:
            d = {'batch_path':  self.batch_path,
                 'df':          self.df}
            pickle.dump(d, open(path[0]))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

    def open_batch(self):
        if self.ui.listwBatch.count() > 0:
            if QtWidgets.QMessageBox.warning(self, 'Warning!', 'If you open a new batch, the current batch will be '
                                                               'DISCARDED. Do you still want to continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Batch', directory=configuration.projPath + '/batches')
        dfpath = path + '/dataframe.batch'
        if path == '':
            return
        elif not os.path.isfile(dfpath):
            QtWidgets.QMessageBox.warning(self, 'Invalid batch dir',
                                          'The selected directory does not appear to be a valid  batch directory '
                                          'since it does not contain a "dataframe.batch" file')
            return
        try:
            df = pandas.read_pickle(dfpath)
            self.df = df
            self.batch_path = path
            self.setWindowTitle('Batch Manager: ' + self.batch_path.split('/')[-1])

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
                        QtGui.QBrush(QtGui.QColor('green')))
                else:
                    self.ui.listwBatch.item(n - 1).setBackground(
                        QtGui.QBrush(QtGui.QColor('red')))

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the dataframe file.\n' + traceback.format_exc())
            return

