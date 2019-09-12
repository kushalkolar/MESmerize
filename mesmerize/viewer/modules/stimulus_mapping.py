#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from ..core.common import ViewerUtils
from .stimmap_modules.page import Page
from .stimmap_modules.main_widget_pytemplate import *
from ...pyqtgraphCore.imageview import ImageView
from ...pyqtgraphCore import LinearRegionItem
from ...common import configuration, get_project_manager
import pandas as pd
from typing import *


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer):
        QtWidgets.QDockWidget.__init__(self, parent)
        self.vi = ViewerUtils(viewer)

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        # self.stim_types = dict.fromkeys(configuration.proj_cfg['STIM_DEFS'])
        self.tabs = {}

        if isinstance(self, ModuleGUI):
            self.setup_tabs()
            self.ui.comboBoxShowTimelineChoice.currentIndexChanged.connect(self.set_timeline)
            self.timeline_stimulus_display = TimeLineStimulusMap(viewer)
            get_project_manager().signal_project_config_changed.connect(self.reset)
            self.ui.btnSetAllMaps.clicked.connect(self.set_all_maps)

    @property
    def maps(self) -> dict:
        """Returns a dictionary of the stimulus maps"""
        return self.tabs

    def setup_tabs(self):
        self.ui.comboBoxShowTimelineChoice.addItems([''])
        self.ui.comboBoxShowTimelineChoice.addItems(configuration.proj_cfg.options('STIM_DEFS'))
        for stim_def in configuration.proj_cfg.options('STIM_DEFS'):
            self.add_stim_type(stim_def)

    def add_stim_type(self, stim_type: str):
        self.ui.tabWidget.addTab(Page(parent=self, stim_type=stim_type), stim_type)
        self.tabs[stim_type] = self.ui.tabWidget.widget(self.ui.tabWidget.count() - 1)

    def get_all_stims_dataframes(self) -> dict:
        d = {}
        for ix in range(self.ui.tabWidget.count()):
            stim_type = self.ui.tabWidget.widget(ix).stim_type
            try:
                df = self.ui.tabWidget.widget(ix).get_dataframe()
            except IndexError:
                d[stim_type] = None
            else:
                d[stim_type] = {}
                d[stim_type]['dataframe'] = df
                d[stim_type]['units'] = self.ui.tabWidget.widget(ix).ui.comboBoxTimeUnits.currentText()
        return d

    def export_map(self):
        path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save stimulus map as', '', '(*.smap)')
        if path == '':
            return
        if path[0].endswith('.smap'):
            path = path[0]
        else:
            path = path[0] + '.smap'

        current_tab = self.ui.tabWidget.currentWidget()
        df = current_tab.get_dataframe()

        pd.to_pickle(df, path, protocol=4)

    def import_map(self):
        pass

    def clear_all_tabs(self):
        for stim_def in self.tabs.keys():
            tab = self.tabs[stim_def]
            assert isinstance(tab, Page)
            tab.clear()
        self.ui.tabWidget.clear()
        self.ui.comboBoxShowTimelineChoice.clear()

    def reset(self):
        self.clear_all_tabs()
        self.setup_tabs()

    def set_all_data(self, dataframes_dict: dict):
        self.reset()
        for stim_type in dataframes_dict.keys():
            if dataframes_dict[stim_type] is None:
                continue
                
            tab = self.tabs[stim_type]
            tab.set_data(dataframes_dict[stim_type])#['dataframe'])
            # if dataframes_dict[stim_type]['units'] == 'seconds':
            tab.ui.comboBoxTimeUnits.setCurrentIndex(0)
            # elif dataframes_dict[stim_type]['units'] == 'frames':
            #     tab.ui.comboBoxTimeUnits.setCurrentIndex(1)

    def set_all_maps(self):
        self.set_timeline(self.ui.comboBoxShowTimelineChoice.currentIndex())

    def export_to_work_env(self):
        d = self.get_all_stims_dataframes()

        for stim_type in d.keys():
            if d[stim_type] is None:
                continue

            if d[stim_type]['units'] == 'seconds':
                fps = self.vi.viewer.workEnv.meta['fps']
                d[stim_type]['dataframe']['start'] = d[stim_type]['dataframe']['start'] * fps
                d[stim_type]['dataframe']['start'] = d[stim_type]['dataframe']['start'].astype(int)

                d[stim_type]['dataframe']['end'] = d[stim_type]['dataframe']['end'] * fps
                d[stim_type]['dataframe']['end'] = d[stim_type]['dataframe']['end'].astype(int)

            d[stim_type] = d[stim_type]['dataframe']

        self.vi.viewer.workEnv.stim_maps = d

    def set_timeline(self, ix: int):
        self.export_to_work_env()
        if ix == 0:
            self.timeline_stimulus_display.clear_all()
            return

        stim_type = self.ui.comboBoxShowTimelineChoice.itemText(ix)
        if stim_type == '':
            self.timeline_stimulus_display.clear_all()
            return

        # tab_page = self.tabs[stim_type]
        # assert isinstance(tab_page, Page)

        try:
            # df = tab_page.get_dataframe()
            df = self.vi.viewer.workEnv.stim_maps[stim_type]
        except IndexError as ie:
            QtWidgets.QMessageBox.information(self, 'IndexError', str(ie))
            return

        # units = self.vi.viewer.workEnv.stim_maps[stim_type]['units']
        #
        # if units == 'seconds':
        #     fps = self.vi.viewer.workEnv.meta['fps']
        #     df['start'] = df['start'] * fps
        #     df['start'] = df['start'].astype(int)
        #     df['end'] = df['end'] * fps
        #     df['end'] = df['end'].astype(int)

        self.timeline_stimulus_display.set_from_stimulus_mapping(df)


class TimeLineStimulusMap:
    def __init__(self, viewer: ImageView):
        self.viewer = viewer
        self.linear_regions = []

    def add_linear_region(self, frame_start: int, frame_end: int, color: Tuple[float, float, float, float]):
        linear_region = LinearRegionItem(values=[frame_start, frame_end],
                                         brush=color, movable=False, bounds=[frame_start, frame_end])
        linear_region.setZValue(0)
        linear_region.lines[0].setPen(color)
        linear_region.lines[1].setPen(color)

        self.linear_regions.append(linear_region)
        self.viewer.ui.roiPlot.addItem(linear_region)

    def del_linear_region(self, linear_region: LinearRegionItem):
        self.viewer.ui.roiPlot.removeItem(linear_region)
        linear_region.deleteLater()
        self.linear_regions.remove(linear_region)

    def clear_all(self):
        for region in self.linear_regions:
            self.viewer.ui.roiPlot.removeItem(region)
            region.deleteLater()
        self.linear_regions = []

    def set_from_stimulus_mapping(self, dataframe: pd.DataFrame):
        """
        :param dataframe: dataframe of stimulus information with units as frames (not seconds)
                           for start and end times of stimuli
        """
        self.clear_all()
        for ix, row in dataframe.iterrows():
            self.add_linear_region(row['start'], row['end'], row['color'])


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ModuleGUI(parent=None, viewer=None)
    w.add_stim_type('bah test')
    w.add_stim_type('bah test2')
    w.ui.tabWidget.clear()
    w.show()
    app.exec_()
