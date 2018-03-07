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

if __name__ == '__main__':
    from stats_window import *
    import DataTypes
else:
    from .stats_window import *
    from . import DataTypes
    from .HistoryWidget import HistoryTreeWidget
import sys
import pickle


class StatsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(StatsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Stats & Plots')
        self.dockWidget.hide()

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

            labelTransmission = QtWidgets.QLabel(self.tabWidget.widget(0))
            labelTransmission.setGeometry(xpos + 60, ypos, 150, 26)
            labelTransmission.setText('Transmission ' + str(n) + ' :')

            self.labelTransmissionList.append(labelTransmission)

            lineEdGroup = QtWidgets.QLineEdit(self.tabWidget.widget(0))
            lineEdGroup.setGeometry(xpos + 65 + 100, ypos, 520, 26)
            lineEdGroup.setPlaceholderText('Group Names separated by commas ( , )')
            lineEdGroup.deleteLater()

            self.lineEdGroupList.append(lineEdGroup)

            ypos += 35

        btnSetGroups = QtWidgets.QPushButton(self.tabWidget.widget(0))
        btnSetGroups.setGeometry(xpos, ypos + 10, 75, 26)
        btnSetGroups.setText('Set Groups')
        btnSetGroups.clicked.connect(self._setGroups)

    def _setGroups(self):
        i = 0
        gts = []
        for entry in self.lineEdGroupList:
            group_list = [entry.strip() for e in entry.text().split(',')]
            gt = DataTypes.GroupTranmission.from_ca_data(self.transmissions_list[i])
            gts.append(gt)
            i +=1

        self.StatsData = DataTypes.StatsTransmission.from_group_trans(gts)
        pickle.dump(open('/home/kushal/Sars_stuff/github-repos/MESmerize/analyser/test_stats.pik', 'wb'), protocol=4)

    def input_transmissions(self, srcs_list, transmissions_list):

        if not hasattr(self, 'lineEdGroupList'):
            return

        if not QtGui.QMessageBox.question(self, 'Discard current data?', 'You have data open in this window, would you '
                                                                     'like to discard them and load the new data?') == \
                QtGui.QMessageBox.Yes:
            return

        self.transmissions_list = transmissions_list
        self.dockWidget.show()
        self._set_history_widget(srcs_list)

        self._setup_group_entries(len(transmissions_list))


    def _set_history_widget(self, srcs):
        history_widget = HistoryTreeWidget()
        history_widget.fill_widget(srcs)
        self.dockWidget.setWidget(history_widget)

    def _reset_group_entries(self):
        for item in self.btnAutoList:
            item.deletelater()
        for item in self. labelTransmissionList:
            item.deletelater()
        for item in self.lineEdGroupList:
            item.deletelater()




if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    sw = StatsWindow()
    sw.setup_group_entries(3)
    sw.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
