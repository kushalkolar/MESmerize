#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

if __name__ == '__main__':
    from stimmap_modules.page import Page
    from stimmap_modules.main_widget_pytemplate import *
    # from viewer.core.common import ViewerInterface
    from pyqtgraph.imageview import ImageView
    # from common import configuration
else:
    from .stimmap_modules.page import Page
    from .stimmap_modules.main_widget_pytemplate import *
    # from ..core.common import ViewerInterface
    from pyqtgraphCore.imageview import ImageView
    from common import configuration
import pandas as pd


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer):
        QtWidgets.QDockWidget.__init__(self, parent)
        # self.vi = ViewerInterface(viewer)

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        # self.stim_types = dict.fromkeys(configuration.proj_cfg['STIM_DEFS'])
        self.tabs = {}

        self.setup_tabs()
        configuration.project_manager.signal_project_config_changed.connect(self.reset)

    def setup_tabs(self):
        for stim_def in configuration.proj_cfg.options('STIM_DEFS'):
            self.add_stim_type(stim_def)

    def add_stim_type(self, stim_type: str):
        self.ui.tabWidget.addTab(Page(parent=self, stim_type=stim_type), stim_type)
        self.tabs[stim_type] = self.ui.tabWidget.widget(self.ui.tabWidget.count() - 1)

    def get_all_stims_dataframes(self) -> dict:
        d = {}
        for ix in range(self.ui.tabWidget.count()):
            stim_type = self.ui.tabWidget.widget(ix).stim_type
            df = self.ui.tabWidget.widget(ix).get_dataframe()
            d[stim_type] = df
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

    def reset(self):
        self.clear_all_tabs()
        self.setup_tabs()

    def set_all_data(self, dataframes_dict: dict):
        self.reset()
        for stim_type in dataframes_dict.keys():
            tab = self.tabs[stim_type]
            assert isinstance(tab, Page)
            tab.set_data(dataframes_dict[stim_type])


class TimeLineStimulusMap:
    def __init__(self, viewer: ImageView):
        pass

    def add_stimulus(self):
        pass

    def del_stimulus(self):
        pass

    def clear_map(self):
        pass

    def set_map(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ModuleGUI(parent=None, viewer=None)
    w.add_stim_type('bah test')
    w.add_stim_type('bah test2')
    w.ui.tabWidget.clear()
    w.show()
    app.exec_()
