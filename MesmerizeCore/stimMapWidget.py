#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 22:50:23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

Just a simple GUI for mapping any auxiliary voltage information to stimulus definitions.
"""
import pickle
import sys
sys.path.append('..')
if __name__ == '__main__':
    from stimMap_one_row_pytemplate import *
    import configuration
else:
    from .stimMap_one_row_pytemplate import *
    from settings import configuration
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QWidget):
    def __init__(self, voltagesDict):
        super().__init__()
        self.voltagesDict = voltagesDict
        self.tabs = QtWidgets.QTabWidget()
        self.setWindowTitle('Stimulus Maps Entry')
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        for channel in voltagesDict.keys():
            self.tabs.addTab(TabPage(self.tabs), channel)
            # Setup the GUI in that tab
            self.tabs.widget(self.tabs.count() -1).setupGUI(voltagesDict[channel], channel)


            self.tabs.widget(self.tabs.count() -1).ui.exportBtn.clicked.connect(self._exportMap)
            self.tabs.widget(self.tabs.count() - 1).ui.importBtn.clicked.connect(self._importMap)

    def _exportMap(self):
        currMap = self._getStimMap()
        exportPath = QtGui.QFileDialog.getSaveFileName(self, 'Export Stimulus Map', '',
                                                       '(*.smap)')
        if exportPath == '':
            return

        if exportPath[0].endswith('.smap'):
            exportPath = exportPath[0]

        else:
            exportPath = exportPath[0] + '.smap'

        pickle.dump(currMap, open(exportPath, 'wb'), protocol=4)

    def _importMap(self):
        path = QtGui.QFileDialog.getOpenFileName(self, 'Import stimulus map file', '', '(*.smap)')

        if path == '':
            return

        dmap = pickle.load(open(path[0], 'rb'))

        page = self.tabs.currentWidget()
        keyval = list(dmap.keys())[0]
        for i in range(0, len(page.ui.labelVoltage)):
            if page.ui.labelVoltage[i].text() in dmap[keyval]['values'].keys():
                page.ui.stimLineEdit[i].setText(dmap[keyval]['values'][page.ui.labelVoltage[i].text()][0])
                page.ui.aux_1_colorBtn[i].setColor(dmap[keyval]['values'][page.ui.labelVoltage[i].text()][-1])

    def _getStimMap(self, page=None):
        if page is None:
            page = self.tabs.currentWidget()
        machine_channel = page.ui.titleLabelChannel.objectName()
        d = {}

        for i in range(0, len(page.ui.labelVoltage)):
            d[page.ui.labelVoltage[i].text()] = [
                str(page.ui.aux_1_stimBox[i].currentText()) + str(page.ui.stimLineEdit[i].text()),
                page.ui.aux_1_colorBtn[i].color()]

        page_map = {}
        page_map[machine_channel] = {}
        page_map[machine_channel]['channel_name'] = page.ui.lineEdChannelName.text()
        page_map[machine_channel]['values'] = d

        return page_map

    def getAllStimMaps(self):
        mes_maps = {}

        for c in range(0, self.tabs.count()):

            if self.tabs.widget(c).ui.lineEdChannelName.text() == '':
                continue

            page = self.tabs.widget(c)

            mes_maps = {**self._getStimMap(page), **mes_maps}

        return mes_maps


class TabPage(QtGui.QWidget):
    def __init__(self, parent=None, *args):
        QtGui.QWidget.__init__(self, parent, *args)

    def setupGUI(self, voltList, channel):
        self.ui = Ui_Form()
        self.ui.setupUi(self, voltList, channel, configuration.cfg.options('STIM_DEFS'),
                        configuration.cfg.options('ALL_STIMS'))
        
# For testing
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = Window(mesfile.voltDict)
    win.resize(520,120)
    win.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
#    window = QtGui.QMainWindow()
#    window.resize(520,120)
#    gui = stimMapGUI()
#    gui.ui.setupUi(gui,[1,2,3,4])
#    window.setCentralWidget(gui)
#    window.show()
#    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QtGui.QApplication.instance().exec_()
    