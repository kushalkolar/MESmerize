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
from pyqtgraphCore import PlotItem, PlotDataItem, PlotCurveItem, ScatterPlotItem, InfiniteLine
from pyqtgraphCore.functions import pseudoScatter
from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from .pytemplates.stats_gui_pytemplate import *
from . import DataTypes
from .HistoryWidget import HistoryTreeWidget
from .stats_plots import *
from .pytemplates.stim_plots_pytemplate import *
from .pytemplates.stats_peak_plots_pytemplate import *
from .pytemplates.beeswarm_plots_pytemplate import *
import sys
import numpy as np
import scipy as scipy
import pandas as pd
from functools import partial
import pickle
import os
from common import configuration


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
        self._dock_titles = ['Transmissions w/history', 'Peak Plot Controls',
                             'Stim Plot Controls', 'Violin Plot Controls', 'Beeswarm Plot Controls',
                             'Parallel Coor Plot Controls']
        self.tabWidget.currentChanged.connect(self._set_stack_index)
        self.tabWidget.setCurrentIndex(0)
        self._init_plot_interface()

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

        if not os.path.exists(configuration.sys_cfg_path + '/console_history/'):
            os.makedirs(configuration.sys_cfg_path + '/console_history')

        cmd_history_file = configuration.sys_cfg_path + '/console_history/stats_gui.pik'

        self.dockConsole.setWidget(ConsoleWidget(namespace=ns, text=txt,
                                                 historyFile=cmd_history_file))

        self.dockConsole.hide()

    """
    #########################################################################################
                                    Input Transmissions stuff
    #########################################################################################
    """

    # Call by Peak_Features node in flowchart, constructs StatsTransmission from normal Transmissions
    def input_transmissions(self, transmissions_list):
        self.listwGroups.hide()
        self.listwStats.hide()
        if hasattr(self, 'lineEdGroupList'):
            if not QtWidgets.QMessageBox.question(self, 'Discard current data?',
                                              'You have data open in this window, would you '
                                              'like to discard them and load the new data?') == QtWidgets.QMessageBox.Yes:
                return

        self.transmissions_list = transmissions_list

        srcs_list = []
        for transmission in self.transmissions_list:
            srcs_list.append(transmission.src)

        self._set_history_widget(srcs_list)
        self._setup_group_entries(len(transmissions_list))

    def _save_raw_trans(self):
        if not hasattr(self, 'transmissions_list'):
            QtWidgets.QMessageBox.warning(self, 'Nothing to save', 'There are no raw transmissions to save')

        for i in range(len(self.transmissions_list)):
            path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Transmission ' + str(i), '', '(*.trn)')
            if path == '':
                return
            if path[0].endswith('.trn'):
                path = path[0]
            else:
                path = path[0] + '.trn'

            try:
                self.transmissions_list[i].to_pickle(path)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

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
                if QtWidgets.QMessageBox.question(self, 'Empty entry', 'The entry for Transmission ' + str(i) + ' is empty '
                                            'would you like to skip this transmission and not annotate groups to it?',
                                                  QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                    return
            group_list = [e.strip() for e in entry.text().split(',')]
            gt = DataTypes.GroupTransmission.from_ca_data(self.transmissions_list[i], group_list)
            self.gts.append(gt)
            i += 1

        self.listwGroups.show()
        self.listwStats.show()
        self.StatsData = DataTypes.StatsTransmission.from_group_trans(self.gts)
        self.listwGroups.addItems(self.StatsData.all_groups)
        self.set_data()

    def _del_group_entries(self):
        for item in self.btnAutoList:
            item.deleteLater()
        for item in self.labelTransmissionList:
            item.deleteLater()
        for item in self.lineEdGroupList:
            item.deleteLater()

    def _auto_slot(self, i):
        QtWidgets.QMessageBox.information(self, 'Error', 'Not implemented')
        pass

    """#########################################################################################
                                            Plotting
    ############################################################################################"""

    def _init_plot_interface(self):
        self.plots_interface = PlotInterface(self)

    def set_data(self):
        if not hasattr(self, 'StatsData') and not hasattr(self, 'gts'):
            return
        self.listwGroups.clear()
        self.listwGroups.addItems(self.StatsData.all_groups)
        self.plot_all()

    def plot_all(self):
        group_colors = {}
        c = ['b', 'g', 'r', 'c', 'm', 'y']
        i = 0
        for group in self.StatsData.all_groups:
            group_colors.update({group: c[i%6]})
            i +=1

        self.plots_interface.set_data(df=self.StatsData.df, group_dict=group_colors)
        self.plots_interface.plot()

    def _set_stack_index(self, i):
        self.dockWidget.setWindowTitle(self._dock_titles[i])

    def _set_matplotlib_controls(self):
        xpos = 10
        ypos = 10
        labelGroupList = []
        btnColorList = []

        parent = self.stack_page_violin_plots

        for group in self.StatsData.all_groups:
            labelGroup = QtWidgets.QLabel(parent)
            labelGroup.setGeometry(xpos, ypos, 100, 26)
            labelGroup.setText(group)

            labelGroupList.append(labelGroup)

            btnColor = ColorButton(parent)
            btnColor.setGeometry(xpos + 120, ypos, 50, 26)

            btnColorList.append(btnColor)

            ypos += 35

    """
    #########################################################################################
                                    Saving & Loading files
    #########################################################################################
    """

    def _save_stats_transmission(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Stats Transmission as', '', '(*.strn)')
        if path == '':
            return

        if path[0].endswith('.strn'):
            path = path[0]
        else:
            path = path[0] + '.strn'

        try:
            self.StatsData.to_pickle(path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

    def _open_stats_transmission(self):
        if hasattr(self, 'StatsData'):
            if not QtWidgets.QMessageBox.question(self, 'Discard current data?',
                                              'You have data open in this window, would you '
                                              'like to discard them and load the new data?',
                                                  QtWidgets.QMessageBox.Yes,
                                                  QtWidgets.QMessageBox.No) \
                                                == QtWidgets.QMessageBox.Yes:
                return

        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Import Statistics object', '', '(*.strn)')
        if path == '':
            return
        try:
            self.StatsData = DataTypes.StatsTransmission.from_pickle(path[0])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return

        self.set_data()
        self._set_history_widget(self.StatsData.src)

    def _open_groups(self):
        groups = []
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, 'Import Group object', '', '(*.gtrn)')
        print(paths)
        if paths == '':
            return
        if paths[0] == []:
            return
        try:
            for path in paths[0]:
                groups.append(DataTypes.GroupTransmission.from_pickle(path))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!', 'Could not open the chosen file.\n' + str(e))
            return

        if hasattr(self, 'StatsData'):
            l = [self.StatsData] + groups
            self.StatsData = DataTypes.StatsTransmission.merge([l])
        else:
            self.StatsData = DataTypes.StatsTransmission.from_group_trans(groups)
            self.gts += groups

    def _save_groups(self):
        if not hasattr(self, 'gts'):
            QtWidgets.QMessageBox.warning(self, 'Save Error', 'No open Groups to save!')
            return

        for i in range(len(self.gts)):
            path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Group Transmission ' + str(i), '', '(*.gtrn)')
            if path == '':
                return
            if path[0].endswith('.gtrn'):
                path = path[0]
            else:
                path = path[0] + '.gtrn'

            try:
                self.gts[i].to_pickle(path)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))


class MPLW(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)

class Plots:
    def __init__(self, curve_plot, violin_plot):
        self.curve_plot = curve_plot
        self.violin_plot = violin_plot

    def setData(self, groups):
        print(groups)
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        ci = 0
        ax = self.curve_plot.fig.add_subplot(111)

        for group in groups:
            c = colors[ci]
            for ix, r in group.df.iterrows():
                if (r['peak_curve'] is not None) and (len(r['peak_curve']) > 0):
                    ax.plot(r['peak_curve']/min(r['peak_curve']), color=c)
            ci +=1

        self.curve_plot.canvas.draw()
        # self.violin_plot.draw()

    def setColor(self):
        pass

    def addGroup(self):
        pass

    def removeGroup(self):
        pass


class PlotInterface:
    def __init__(self, parent):
        assert isinstance(parent, StatsWindow)
        self.plots = []

        self.stims = StimPlots()
        self.plots.append(self.stims)
        parent.stim_plots_tab.layout().addWidget(self.stims)

        self.peaks = PeakPlots()
        self.plots.append(self.peaks)
        parent.peak_plot_tab.layout().addWidget(self.peaks)

        self.paracor = ParaCorPlots()
        self.plots.append(self.paracor)
        parent.paracor_tab.layout().addWidget(self.paracor)

        self.beeswarm = BeesswarmPlots()
        self.plots.append(self.beeswarm)
        parent.beeswarm_tab.layout().addWidget(self.beeswarm)

    def set_data(self, df, group_dict):
        for plot in self.plots:
            plot.set_data(df, group_dict)

    def set_colors(self):
        pass

    def plot(self):
        for plot in self.plots:
            plot.plot_all()


class PeakPlots(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_stats_peak_plots_template()
        self.ui.__init__()
        self.ui.setupUi(self)
        self.gplots = []

    def set_data(self, df, groups_dict):
        self.df = df
        self.groups_dict = groups_dict

    def plot_all(self):
        self.plot_overlaps()
        self.plot_group_subplots()

    def plot_overlaps(self):
        self.ui.curve_plot_all_group_peaks.clear()
        self.ymax = 0.0
        for key in self.groups_dict.keys():
            for ix, r in self.df.loc[self.df[key] == True].iterrows():
                try:
                    a = r['_pfeature_peak_curve']
                    if a.size == 0:
                        continue
                    ma = np.max(a)
                    self.ymax = np.maximum(ma, self.ymax)

                    if not hasattr(self, 'ymin'):
                        self.ymin = self.ymax

                    mi = np.min(a)
                    self.ymin = np.minimum(mi, self.ymin)

                    center = r['_pfeature_ix_peak_rel']

                    xs = np.arange((0-center), a.size - center)
                    self.ui.curve_plot_all_group_peaks.plot(x=xs, y=a, pen=self.groups_dict[key])
                except Exception as e:
                    print(e)

    def plot_group_subplots(self):
        for item in self.gplots:
            self.ui.curve_plot_group_peaks.removeItem(item)
        self.ui.curve_plot_group_peaks.clear()
        self.gplots = []

        for key in self.groups_dict.keys():
            self.gplots.append(self.ui.curve_plot_group_peaks.addPlot(title=key))
            for ix, r in self.df.loc[self.df[key] == True].iterrows():
                try:
                    a = r['_pfeature_peak_curve']

                    center = r['_pfeature_ix_peak_rel']

                    xs = np.arange((0-center), a.size - center)

                    self.gplots[-1].plot(x=xs, y=a, pen=self.groups_dict[key])

                except Exception as e:
                    print(e)

        for plot in self.gplots:
            plot.setYRange(self.ymin, self.ymax)


    def plot_headmaps(self):
        pass


class StimPlots(QtWidgets.QWidget):#, Ui_stim_plots_template):
    def __init__(self): #, flags, parent=None, *args, **kwargs):
        #super().__init__()#flags, parent, *args, **kwargs)
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_stim_plots_template()
        self.ui.__init__()
        self.ui.setupUi(self)
        self.gplots = []

    def set_data(self, df, groups_dict):
        self.df = df
        self.groups_dict = groups_dict

    def plot_all(self):
        self.plot_overlaps()
        self.plot_group_subplots()
        self.plot_heatmaps()

    def plot_overlaps(self, update_subplots=True):
        self.ui.stim_plots_overlays.clear()
        self.ymax = 0.0
        for key in self.groups_dict.keys():
            for ix, r in self.df.loc[self.df[key] == True].iterrows():
                a = r['raw_curve']
                ma = np.max(a)
                self.ymax = np.maximum(ma, self.ymax)

                if not hasattr(self, 'ymin'):
                    self.ymin = self.ymax

                mi = np.min(a)
                self.ymin = np.minimum(mi, self.ymin)

                self.ui.stim_plots_overlays.plot(a, pen=self.groups_dict[key])

    def plot_group_subplots(self):
        for item in self.gplots:
            self.ui.stim_plots_groups.removeItem(item)

        self.ui.stim_plots_groups.clear()
        self.gplots = []

        for key in self.groups_dict.keys():
            self.gplots.append(self.ui.stim_plots_groups.addPlot(title=key))

            for ix, r in self.df.loc[self.df[key] == True].iterrows():
                self.gplots[-1].plot(r['raw_curve'], pen=self.groups_dict[key])

            self.gplots[-1].setYRange(self.ymin, self.ymax)

    def plot_heatmaps(self):
        pass


class ViolinPlots:
    pass


class BeesswarmPlots(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = Ui_beeswarm_plots_template()
        self.ui.__init__()
        self.ui.setupUi(self)
        self.fplots = []
        self.inflines = []
        self.inflplots = []

    def set_data(self, df, groups_dict):
        self.df = df
        self.groups_dict = groups_dict
        self.fcols = [col for col in self.df if str(col).startswith('_pfeature')]
        self.fcols.remove('_pfeature_peak_curve')
        self.fcols.remove('_pfeature_uuid')
        self.fcols.remove('_pfeature_ix_peak_rel')

    def plot_all(self):
        n = 0
        self.lastClicked = []
        self.lastClickedColors = []
        self.plots = {}
        for f in self.fcols:
            i = 0
            sp = ScatterPlotItem()

            plot = self.ui.graphicsView.addPlot(title=f[10:])

            ebars = []
            for group in self.groups_dict.keys():
                ys = self.df.loc[self.df[group] == True][f].dropna().values
                yvals = ys.astype(np.float64)
                xs = pseudoScatter(yvals, spacing=0.2, bidir=True) * 0.2
                sp.addPoints(x=xs + i, y=yvals, pen=None, symbol='o', brush=self.groups_dict[group],
                             name=f, size=10)
                i += 1
                #            sp.sigClicked.connect(lambda p: self._clicked(p[0], p[1], f))
            sp.sigClicked.connect(self._clicked)
            plot.addItem(sp)

            self.plots.update({f: plot})
            #            for eb in ebars:
            #                p.addItem(eb)
            n += 1
            if n == 5:
                self.ui.graphicsView.nextRow()

    def _clicked(self, plot, points):
        i = 0
        for item in self.inflines:
            self.inflplots[i].removeItem(item)
            i += 1

        self.inflplots = []
        self.inflines = []
        i = 0
        for p in self.lastClicked:
            p.resetPen()
            p.setBrush(self.lastClickedColors[i])
            i += 1
        self.lastClickedColors = []
        for p in points:
            self.lastClickedColors.append(p.brush())
            p.setPen('w', width=4)
        self.lastClicked = points
        if len(self.lastClicked) == 1:
            yval = self.lastClicked[0].pos()[1]

            fcolvals = self.df[plot.name()].values

            ix = np.where(fcolvals == yval)[0][0]

            #            ix = self.df[self.df[plot.name()] == yval].index[0]

            #            print(self.df.iloc[ix])
            for f in self.fcols:
                try:
                    val = self.df.iloc[ix][f]
                    il = InfiniteLine(pos=val, angle=0, pen='w')

                    print(self.df.iloc[ix])
                    self.plots[f].addItem(il)
                    self.inflines.append(il)
                    self.inflplots.append(self.plots[f])
                except ValueError as e:
                    continue


class ParaCorPlots(MPLW):
    def __init__(self):
        MPLW.__init__(self)

    def set_data(self, df, groups_dict):
        pass

    def plot_all(self):
        pass

if __name__ == '__main__':
    # t1 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t1.trn')
    # t2 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t2.trn')
    # t3 = DataTypes.Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/test_raw_trans_stats_plots_gui/t3.trn')

    app = QtWidgets.QApplication([])
    sw = StatsWindow()
    # sw.input_transmissions([t1, t2, t3])
    # sw.lineEdGroupList[0].setText('A')
    # sw.lineEdGroupList[1].setText('B')
    # sw.lineEdGroupList[2].setText('C')
    sw.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
