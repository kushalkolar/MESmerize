#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 7 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.console import ConsoleWidget

if __name__ == '__main__':
    from stats_window import *
    import DataTypes
else:
    from .stats_window import *
    from . import DataTypes
    from .HistoryWidget import HistoryTreeWidget
import sys
import numpy as np
import scipy as scipy
import pandas as pd
import matplotlib.pyplot as pyplot
from functools import partial
import pickle

class StatsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(StatsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Stats & Plots')
        self.dockWidget.hide()
        self.actionSave_Statistics_DataFrame.triggered.connect(self._save_stats_transmission)
        self.actionSave_Group_Transmissions.triggered.connect(self._save_groups)
        self.actionOpen_Statistics_DataFrame.triggered.connect(self._open_stats_transmission)

        ns = {'np': np,
              'pickle': pickle,
              'scipy': scipy,
              'pd': pd,
              'DataTypes': DataTypes,
              'pyplot': pyplot,
              'main': self,
              'curr_tab': self.tabWidget.currentWidget
              }

        txt = "Namespaces:\n" \
              "pickle as pickle\n" \
              "numpy as 'np'\n" \
              "scipy as 'scipy'\n" \
              "pyplot as 'pyplot\n" \
              "dt as 'DataTypes'\n" \
              "self as 'main'\n\n" \
              "To access plots in current tab call curr_tab()\n" \
              "Example:\n" \
              "tab0 = curr_tab()\ntab0.p1.plot(x, np.sin(x))"

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile='./test_history.pik'))

        self.dockConsole.hide()

    def input_transmissions(self, transmissions_list):
        if hasattr(self, 'lineEdGroupList'):
            if not QtGui.QMessageBox.question(self, 'Discard current data?',
                                              'You have data open in this window, would you '
                                              'like to discard them and load the new data?') == QtGui.QMessageBox.Yes:
                return

        self.transmissions_list = transmissions_list
        self.dockWidget.show()

        srcs_list = []
        for transmission in self.transmissions_list:
            srcs_list.append(transmission.src)

        self._set_history_widget(srcs_list)

        self._setup_group_entries(len(transmissions_list))

    def _setup_group_entries(self, n):
        xpos = 10
        ypos = 10

        self.btnAutoList = []
        self.labelTransmissionList = []
        self.lineEdGroupList = []

        for i in range(0, n):
            btnAuto = QtWidgets.QPushButton(self.tabWidget.widget(0))
            btnAuto.setGeometry(xpos, ypos, 50, 26)
            btnAuto.setText('Auto')

            self.btnAutoList.append(btnAuto)
            btnAuto.clicked.connect(partial(self._auto_slot, i))

            labelTransmission = QtWidgets.QLabel(self.tabWidget.widget(0))
            labelTransmission.setGeometry(xpos + 60, ypos, 150, 26)
            labelTransmission.setText('Transmission ' + str(i) + ' :')

            self.labelTransmissionList.append(labelTransmission)

            lineEdGroup = QtWidgets.QLineEdit(self.tabWidget.widget(0))
            lineEdGroup.setGeometry(xpos + 65 + 100, ypos, 520, 26)
            lineEdGroup.setPlaceholderText('Group Names separated by commas ( , )')

            self.lineEdGroupList.append(lineEdGroup)

            ypos += 35

        btnSetGroups = QtWidgets.QPushButton(self.tabWidget.widget(0))
        btnSetGroups.setGeometry(xpos, ypos + 10, 75, 26)
        btnSetGroups.setText('Set Groups')
        btnSetGroups.clicked.connect(self._set_groups)

    def _auto_slot(self, i):
        QtGui.QMessageBox.information(self, 'Not implemented', 'Not implemented')
        pass

    def _set_groups(self):
        i = 0
        self.gts = []
        for entry in self.lineEdGroupList:
            if entry.text() == '':
                if QtGui.QMessageBox.question(self, 'Empty entry', 'The entry for Transmission ' + str(i) + ' is empty '
                                            'would you like to skip this transmission and not annotate groups to it?',
                                              QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                    return
            group_list = [e.strip() for e in entry.text().split(',')]
            gt = DataTypes.GroupTransmission.from_ca_data(self.transmissions_list[i], group_list)
            self.gts.append(gt)
            i += 1

        self.StatsData = DataTypes.StatsTransmission.from_group_trans(self.gts)

    def _set_history_widget(self, srcs):
        history_widget = HistoryTreeWidget()
        history_widget.fill_widget(srcs)
        self.dockWidget.setWidget(history_widget)

    def _reset_group_entries(self):
        for item in self.btnAutoList:
            item.deletelater()
        for item in self.labelTransmissionList:
            item.deletelater()
        for item in self.lineEdGroupList:
            item.deletelater()

    def _save_stats_transmission(self):
        path = QtGui.QFileDialog.getSaveFileName(None, 'Save Stats Transmission as', '', '(*.strn)')
        if path == '':
            return

        if path[0].endswith('.strn'):
            path = path[0]
        else:
            path = path[0] + '.strn'

        try:
            self.StatsData.to_pickle(path)
        except Exception as e:
            QtGui.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))


    def _open_stats_transmission(self):
        if hasattr(self, 'StatsData'):
            if not QtGui.QMessageBox.question(self, 'Discard current data?',
                                              'You have data open in this window, would you '
                                              'like to discard them and load the new data?') == QtGui.QMessageBox.Yes:
                return

        path = QtGui.QFileDialog.getOpenFileName(None, 'Import Statistics object', '', '(*.strn)')
        if path == '':
            return
        try:
            self.StatsData = DataTypes.StatsTransmission.from_pickle(path[0])
        except Exception as e:
            QtGui.QMessageBox.warning(None, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return

    def _save_groups(self):
        if not hasattr(self, 'gts'):
            QtGui.QMessageBox.warning(self, 'Save Error', 'No open Groups to save!')
            return

        for i in range(len(self.gts)):
            path = QtGui.QFileDialog.getSaveFileName(None, 'Save Group Transmission ' + str(i), '', '(*.gtrn)')
            if path == '':
                return
            if path[0].endswith('.gtrn'):
                path = path[0]
            else:
                path = path[0] + '.gtrn'

            try:
                self.gts[i].to_pickle(path)
            except Exception as e:
                QtGui.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))




if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    sw = StatsWindow()
    sw._setup_group_entries(3)
    sw.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
