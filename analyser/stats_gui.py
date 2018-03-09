#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 7 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import sys
sys.path.append('..')
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from pyqtgraphCore.console import ConsoleWidget
from pyqtgraphCore import ColorButton

if __name__ == '__main__':
    from stats_window import *
    import DataTypes
    from HistoryWidget import HistoryTreeWidget
    import matplotlib_widget
else:
    from .stats_window import *
    from . import DataTypes
    from .HistoryWidget import HistoryTreeWidget
    from . import matplotlib_widget
import sys
import numpy as np
import scipy as scipy
import pandas as pd
from functools import partial
import pickle


class StatsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(StatsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Stats & Plots')
        self.actionSave_Statistics_DataFrame.triggered.connect(self._save_stats_transmission)
        self.actionOpen_Statistics_DataFrame.triggered.connect(self._open_stats_transmission)
        self.actionSave_Group_Transmissions.triggered.connect(self._save_groups)
        self.actionLoad_Groups.triggered.connect(self._open_groups)
        self.actionSave_Incoming_Transmissions.triggered.connect(self._save_raw_trans)
        self._dock_titles = ['Transmissions w/history', 'matplotlib Controls',
                             'matplotlib Controls', 'Box Plot Controls']
        self.tabWidget.currentChanged.connect(self._set_stack_index)

        ns = {'np': np,
              'pickle': pickle,
              'scipy': scipy,
              'pd': pd,
              'DataTypes': DataTypes,
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
        self.listwGroups.hide()
        if hasattr(self, 'lineEdGroupList'):
            if not QtGui.QMessageBox.question(self, 'Discard current data?',
                                              'You have data open in this window, would you '
                                              'like to discard them and load the new data?') == QtGui.QMessageBox.Yes:
                return

        self.transmissions_list = transmissions_list

        srcs_list = []
        for transmission in self.transmissions_list:
            srcs_list.append(transmission.src)

        self._set_history_widget(srcs_list)
        self._setup_group_entries(len(transmissions_list))

    def _save_raw_trans(self):
        if not hasattr(self, 'transmissions_list'):
            QtGui.QMessageBox.warning(self, 'Nothing to save', 'There are no raw transmissions to save')

        for i in range(len(self.transmissions_list)):
            path = QtGui.QFileDialog.getSaveFileName(None, 'Save Transmission ' + str(i), '', '(*.trn)')
            if path == '':
                return
            if path[0].endswith('.trn'):
                path = path[0]
            else:
                path = path[0] + '.trn'

            try:
                self.transmissions_list[i].to_pickle(path)
            except Exception as e:
                QtGui.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

    def _set_history_widget(self, srcs):
        if len(self.stack_page_transmission_history.children()) > 0:
            for item in self.stack_page_transmission_history.children():
                if isinstance(item, HistoryTreeWidget):
                    item.fill_widget(srcs)
        else:
            layout = QtWidgets.QVBoxLayout(self.stack_page_transmission_history)
            history_widget = HistoryTreeWidget()
            layout.addWidget(history_widget)
            history_widget.fill_widget(srcs)
            history_widget.show()

        self.stackedWidget.setCurrentIndex(0)
        self.dockWidget.setWindowTitle(self._dock_titles[0])

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
        btnSetGroups.clicked.connect(self._del_group_entries)
        btnSetGroups.clicked.connect(btnSetGroups.deleteLater)

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

        self.listwGroups.show()
        self.StatsData = DataTypes.StatsTransmission.from_group_trans(self.gts)
        self.listwGroups.addItems(self.StatsData.all_groups)
        self._init_curve_tab()
        self._init_violin_tab()
        self.set_data()
        # self.set_data()
    def _del_group_entries(self):
        for item in self.btnAutoList:
            item.deleteLater()
        for item in self.labelTransmissionList:
            item.deleteLater()
        for item in self.lineEdGroupList:
            item.deleteLater()

    def set_data(self):
        if not hasattr(self, 'StatsData') and not hasattr(self, 'gts'):
            return
        if not hasattr(self, 'curve_plots'):
            self._init_curve_tab()
        if not hasattr(self, 'violin_plots'):
            self._init_violin_tab()

        self.plots = matplotlib_widget.Plots(self.curve_plots, self.violin_plots)
        self.plots.setData(self.gts)

        self.listwGroups.clear()
        self.listwGroups.addItems(self.StatsData.all_groups)

    def _init_curve_tab(self):
        self.curve_plots = matplotlib_widget.Curves()
        self.curve_tab.layout().addWidget(self.curve_plots)

    def _init_violin_tab(self):
        self.violin_plots = matplotlib_widget.Violins()
        self.violin_tab.layout().addWidget(self.violin_plots)

    def _auto_slot(self, i):
        QtGui.QMessageBox.information(self, 'Error', 'Not implemented')
        pass

    def _set_stack_index(self, i):
        self.dockWidget.setWindowTitle(self._dock_titles[i])
        if i == 0:
            self.stackedWidget.setCurrentIndex(0)
            return
        elif i == 1 or i == 2:
            self.stackedWidget.setCurrentIndex(1)
            return
        elif i == 3:
            self.stackedWidget.setCurrentIndex(2)
            return

    def _set_matplotlib_controls(self):
        xpos = 10
        ypos = 10
        labelGroupList = []
        btnColorList = []

        parent = self.stack_page_matplotlib

        for group in self.StatsData.all_groups:
            labelGroup = QtWidgets.QLabel(parent)
            labelGroup.setGeometry(xpos, ypos, 100, 26)
            labelGroup.setText(group)

            labelGroupList.append(labelGroup)

            btnColor = ColorButton(parent)
            btnColor.setGeometry(xpos + 120, ypos, 50, 26)

            btnColorList.append(btnColor)

            ypos += 35

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

    def _open_groups(self):
        groups = []
        paths = QtGui.QFileDialog.getOpenFileNames(None, 'Import Group object', '', '(*.gtrn)')
        print(paths)
        if paths == '':
            return
        if paths[0] == []:
            return
        try:
            for path in paths[0]:
                groups.append(DataTypes.GroupTransmission.from_pickle(path))
        except Exception as e:
            QtGui.QMessageBox.warning(None, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return

        if hasattr(self, 'StatsData'):
            l = [self.StatsData] + groups
            self.StatsData = DataTypes.StatsTransmission.merge([l])
        else:
            self.StatsData = DataTypes.StatsTransmission.from_group_trans(groups)
            self.gts += groups

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
    t1 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t1.trn')
    t2 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t2.trn')
    t3 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t3.trn')
    
    app = QtWidgets.QApplication([])
    sw = StatsWindow()
    sw.input_transmissions([t1, t2, t3])
    sw.lineEdGroupList[0].setText('A')
    sw.lineEdGroupList[1].setText('B')
    sw.lineEdGroupList[2].setText('C')
    sw.show()
    
    
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
