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
from MesmerizeCore.packager import viewerWorkEnv
from MesmerizeCore import configuration
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

class ModuleGUI(ViewerInterface, QtWidgets.QDockWidget):
    """GUI for the Batch Manager"""
    listwchanged = QtCore.pyqtSignal()

    def __init__(self, parent, viewer_ref):
        ViewerInterface.__init__(self, viewer_ref)

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.listwBatch.itemDoubleClicked.connect(self.show_item_output)
        self.ui.listwBatch.itemClicked.connect(self.show_item_meta)

        self.ui.btnStart.clicked.connect(self.process_batch)
        self.ui.btnAbort.clicked.connect(self._terminate_qprocess)
        self.ui.btnAbort.setDisabled(True)
        self.ui.btnOpen.clicked.connect(self.open_batch)
        self.ui.btnDelete.clicked.connect(self.del_item)
        self.ui.btnViewInput.clicked.connect(self.show_input)

        listwmodel = self.ui.listwBatch.model()
        listwmodel.rowsInserted.connect(self.listwchanged.emit)
        listwmodel.rowsRemoved.connect(self.listwchanged.emit)

        self.df = pandas.DataFrame(columns=['module', 'input_params', 'output', 'meta', 'uuid'])

        self.batch_path = configuration.projPath + '/batches' + '/' + \
                          datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
        os.makedirs(self.batch_path)

        self.setWindowTitle('Batch Manager: ' + self.batch_path.split('/')[-1])

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

        self.ui.scrollAreaStdOut.setStyleSheet('background-color: #000000')
        self.ui.labelStdOut.setStyleSheet('color: #FFFFFF')

        self.ui.scrollAreaStdOut.hide()

    @staticmethod
    def get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def show_input(self):
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        if r['input_item'].item() is None:
            if not self.VIEWER_discard_workEnv():
                return
            pikpath = self.batch_path + '/' + str(UUID) + '_workEnv.pik'
            tiffpath = self.batch_path + '/' + str(UUID) + '.tiff'
            self.viewer_ref.workEnv = viewerWorkEnv.from_pickle(pikPath=pikpath, tiffPath=tiffpath)
            self.VIEWER_update_workEnv()
            self.VIEWER_enable_ui(True)

    def show_item_output(self, s: QtWidgets.QListWidgetItem):
        """Calls subclass of BatchRunInterface.show_output()"""
        self.ui.scrollAreaOutputInfo.show()
        self.resize(1200, 650)
        item_txt = s.text()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        module = r['module'].item()
        m = globals()[module]

        output = self.get_batch_item_output(UUID)

        self.ui.labelOutputInfo.setText('')

        if output['status'] == 1:
            m.output(self.batch_path, UUID, self.viewer_ref)


    def show_item_meta(self, s: QtWidgets.QListWidgetItem):
        """Shows any meta-info (such as the batch module's params) in the meta-info label
        Also shows output info"""
        UUID = s.data(3)
        row = self.df.loc[self.df['uuid'] == UUID]
        meta = row['meta'].item().item()
        info = "\n".join([": ".join([key, str(val)]) for key, val in meta.items()])

        self.ui.labelMeta_info.setText(str(UUID) + '\n' + info)

        output = self.get_batch_item_output(UUID)

        self.ui.labelOutputInfo.setText('')

        if output is None:
            self.ui.labelOutputInfo.setText('Output file does not exist for selected item')
            return
        elif output['status'] == 0:
            self.ui.labelOutputInfo.setText(output['error_msg'])
        elif output['stutus'] == 1:
            self.ui.labelOutputInfo.setText(output['output_info'])

    def process_batch(self):
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

        self.ui.btnStart.setDisabled(True)
        self.ui.btnDelete.setDisabled(True)
        self.ui.btnAbort.setEnabled(True)
        self.VIEWER_discard_workEnv()
        self.current_batch_item_index = -1

        # self.run_next_item()
        self.ui.scrollAreaStdOut.show()
        self.ui.scrollAreaOutputInfo.show()
        self.resize(1200, 650)
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
            self.ui.btnStart.setEnabled(True)
            self.ui.btnDelete.setEnabled(True)
            self.ui.btnAbort.setDisabled(True)
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
                     'python ' +
                     module_path + ' ' +
                     self.batch_path + ' ' +
                     str(r['uuid']) + ' ' +
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
            output = json.load(open(out_file, 'rb'))
            return output
        else:
            return None

    def _terminate_qprocess(self):
        py_proc = psutil.Process(self.process.pid()).children()[0].pid
        children = psutil.Process(py_proc).children()
        os.kill(py_proc, SIGKILL)
        for child in children:
            os.kill(child.pid, SIGKILL)

    # @QtCore.pyqtSlot()
    # def run_next_item(self):
    #     print('Current item index is: ' + str(self.current_item_index))
    #     if self.current_item_index > -1:
    #         pass
    #         # print(self.current_running_item.get_output())
    #         # try:
    #         #     self.df.iloc[self.current_item_index]['output'] = self.current_running_item.get_output()['output']
    #         # #     self.df.iloc[self.current_item_index]['output_params'] = q['output_params']
    #         # #
    #         #     if self.df.iloc[self.current_item_index]['output']['status'] == 'success':
    #         #         self.ui.listwBatch.item(self.current_item_index).setBackground(QtGui.QBrush(QtGui.QColor('green')))
    #         #     else:
    #         #         self.ui.listwBatch.item(self.current_item_index).setBackground(QtGui.QBrush(QtGui.QColor('red')))
    #         # except:
    #         #     self.df.iloc[self.current_item_index]['output'] = None
    #         # #     self.df.iloc[self.current_item_index]['output_params'] = None
    #         #     self.ui.listwBatch.item(self.current_item_index).setBackground(QtGui.QBrush(QtGui.QColor('red')))
    #         #
    #         # self.current_running_item.signals.finished.disconnect(self.run_next_item)
    #         # del self.current_running_item
    #         # # self.run_thread.terminate()
    #
    #     self.current_item_index += 1
    #     self.ui.progressBar.setValue(self.current_item_index / len(self.df.index))
    #     if self.current_item_index == len(self.df.index):
    #         self.ui.progressBar.setValue(100)
    #         self.ui.btnStart.setEnabled(True)
    #         self.ui.btnDelete.setEnabled(True)
    #         QtWidgets.QMessageBox.information(self, 'Batch is done!', 'Yay, your batch has finished processing!')
    #         return
    #
    #     r = self.df.iloc[self.current_item_index]
    #     m = globals()[r['module']]
    #
    #     module_path = os.path.abspath(m.__file__)
    #
    #     # batch_class = m.Batch
    #     # # assert issubclass(batch_class, BatchRunInterface)
    #     # if not hasattr(self, 'thread_pool'):
    #     #     self.thread_pool = QtCore.QThreadPool()
    #     #     # self.thread_pool.setMaxThreadCount(30)
    #     # self.current_running_item = batch_class()
    #     # # assert isinstance(self.current_running_item, QtCore.QObject)
    #     #
    #     # # self.run_thread = QtCore.QThread()
    #     # # self.current_running_item.moveToThread(self.run_thread)
    #     #
    #     # self.current_running_item.signals.finished.connect(self.run_next_item)
    #
    #     input_params = r['input_params'].item()
    #     if type(r['input_workEnv']) is uuid.UUID:
    #         input_workEnv = self.df.loc[self.df['uuid'] == r['input_workEnv']]['output_workEnv']
    #     else:
    #         input_workEnv = r['input_workEnv']
    #
    #     # self.q = Queue()
    #     # self.current_running_item.set_inputs(input_workEnv, input_params=r['input_params'].item())
    #     process = QtCore.QProcess()
    #     process.readyReadStandardOutput.connect(partial(self.print_qprocess_std_out, process))
    #     process.finished.connect(self.run_next_item)
    #
    #     self.ui.listwBatch.item(self.current_item_index).setBackground(QtGui.QBrush(QtGui.QColor('yellow')))
    #     sh_file = self.batch_path + '/' + 'run.sh'
    #     with open(sh_file, 'w') as sf:
    #         sf.write('export PATH="/share/software/anaconda3/bin:$PATH";'
    #                   'source activate compiled_opencv_with_cuda;'
    #                   'export PYTHONPATH=/home/kushal/CaImAn-master/;'
    #                   'which python')
    #     process.start(sh_file)
    #                   # 'python ' + module_path + ' ' + str(r['uuid']))
    #     # process.start('python ' + module_path + ' ' + str(r['uuid']))
    #     # process.start('which python')
    #     # process.start('#!/bin/bash;printenv;python ' + module_path + ' ' + str(r['uuid']))
    #
    #     # print(module_path)
    #     # self.current_running_item.start()
    #     # self.thread_pool.start(self.current_running_item)
    #     # self.current_running_item.process(input_workEnv=input_workEnv, input_params=r['input_params'].item())

    def print_qprocess_std_out(self, std_out):
        self.current_std_out.append((str(std_out.readAllStandardOutput())))
        self.ui.labelStdOut.setText('\n'.join(self.current_std_out))

    def add_item(self, module, input_workEnv, input_params, name='', meta=''):
        """
        :param  module:         The module to run, based on common.BatchRunInterface.
        :type   module:         str

        :param  name:           A name for the batch item
        :type   name:           str

        :param  input_workEnv:  Input workEnv that the module will use
        :type   input_workEnv:  viewerWorkEnv

        :param  input_params:   Input params that the module will use.
                                Depends on your subclass of BatchRunInterface.process() method
        :type   input_params:   dict

        :param  meta:           A dictionary with any metadata information to display in the scroll area label.
        :type   meta:           dict
        """
        if input_workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Work Environment is empty!', 'The current work environment is empty,'
                                                                              ' nothing to add to the batch!')
            return

        UUID = uuid.uuid4()

        if module == 'CNMFE' or module == 'caiman_motion_correction':
            filename = self.batch_path + '/' + str(UUID) + '.tiff'
            tifffile.imsave(filename, data=input_workEnv.imgdata.seq.T)
            input_workEnv.to_pickle(self.batch_path, filename=str(UUID) + '_workEnv', save_img_seq=False)

        pickle.dump(input_params, open(self.batch_path + '/' + str(UUID) + '.params', 'wb'), protocol=4)

        input_params = np.array(input_params, dtype=object)
        meta = np.array(meta, dtype=object)

        self.df = self.df.append({'module': module,
                                  'name': name,
                                  'input_item': None,
                                  'input_params': input_params,
                                  'meta': meta,
                                  'uuid': UUID,
                                  'output': None,
                                  }, ignore_index=True)

        self.ui.listwBatch.addItem(module + ': ' + name)
        n = self.ui.listwBatch.count()
        item = self.ui.listwBatch.item(n - 1)
        assert isinstance(item, QtWidgets.QListWidgetItem)
        item.setData(3, UUID)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

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
            QtWidgets.QMessageBox.Warning(self, 'Invalid batch dir',
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
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the dataframe file.\n' + str(e))
            return

