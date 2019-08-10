#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 17 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from .tab_area_widget import TabAreaWidget
import pandas as pd
from ...common import configuration, get_project_manager, get_window_manager
from ...misc_widgets.list_widget_dialog import ListWidgetDialog
from functools import partial
from ...viewer.core.common import ViewerUtils
from ...viewer.core.viewer_work_environment import ViewerWorkEnv
from collections import UserList
# from ...common.window_manager import WindowClass
from ...common import start
import os


class ProjectBrowserWidget(QtWidgets.QWidget):
    def __init__(self, parent, dataframe: pd.DataFrame):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.tabs = {}
        self.dataframe = dataframe

        self.vertical_layout = QtWidgets.QVBoxLayout(self)

        self.tab_widget = QtWidgets.QTabWidget(parent=self)

        # self.tabs_widget.tabBar().tabCloseRequested.connect(lambda ix: self.del_tab(ix))

        self.vertical_layout.addWidget(self.tab_widget)

        self.add_tab(dataframe, [], is_root=True)

        self.tab_widget.tabCloseRequested.connect(lambda ix: self.del_tab(ix))

        get_project_manager().signal_dataframe_changed.connect(self.update_dataframe_data)

    @QtCore.pyqtSlot(pd.DataFrame)
    def update_dataframe_data(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe  # This is probably not necessary

        tab_area = self.tabs['root']
        assert isinstance(tab_area, TabAreaWidget)

        tab_area.dataframe = self.dataframe
        tab_area.populate_tab()

        for tab_name in self.tabs.keys():
            pass

    def _create_root_context_menu(self):
        pass

    def add_tab(self, dataframe: pd.DataFrame, filter_history: list, is_root=False, name: str = None):
        if not is_root and name is None:
            tab_name = QtWidgets.QInputDialog.getText(self, None, 'Enter name for new tab: ')
            if tab_name[0] == '' or tab_name[1] is False:
                return
            elif tab_name[0] in get_project_manager().child_dataframes.keys():
                QtWidgets.QMessageBox.warning(self, 'DataFrame title already exists!',
                                              'That name already exists in your project, choose a different name!')
                self.add_tab(dataframe, filter_history, is_root)
            tab_name = tab_name[0]
            get_project_manager().add_sub_dataframe(tab_name, filter_history, dataframe)
        elif is_root:
            tab_name = 'root'
        else:
            tab_name = name

        tab_area_widget = TabAreaWidget(self.tab_widget, tab_name, dataframe, filter_history, is_root)
        tab_area_widget.signal_new_tab_requested.connect(self.slot_new_tab_requested)
        tab_area_widget.signal_open_sample_in_viewer_requested.connect(self.slot_open_sample_id_in_viewer)

        self.tab_widget.addTab(tab_area_widget, tab_name)

        self.tab_widget.setTabsClosable(True)
        bar = self.tab_widget.tabBar()
        bar.setTabButton(0, bar.RightSide, None)

        self.tabs.update({tab_name: tab_area_widget})

        if is_root:
            num_columns = len(tab_area_widget.columns)
            self.resize(min(1920, num_columns * 215), 400)

        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    @QtCore.pyqtSlot(pd.DataFrame, list)
    def slot_new_tab_requested(self, dataframe: pd.DataFrame, filter_history: list):
        self.add_tab(dataframe, filter_history)

    def del_tab(self, ix: int):
        print(ix)
        if QtWidgets.QMessageBox.question(self, 'Remove Tab?', 'Are you sure you want to delete this tab? '
                                                       'Only the filter operations to get this child DataFrame will be '
                                                       'removed, your data is still in the Root DataFrame.',
                                      QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return

        tab_name = self.tab_widget.widget(ix).tab_name
        self.tab_widget.removeTab(ix)
        get_project_manager().remove_sub_dataframe(tab_name)

    @QtCore.pyqtSlot(str)
    def slot_open_sample_id_in_viewer(self, sample_id: str):
        viewer = get_window_manager().get_new_viewer_window().viewer_reference

        vi = ViewerUtils(viewer_reference=viewer)

        row = self.dataframe[self.dataframe['SampleID'] == sample_id].iloc[0]
        pikPath = os.path.join(configuration.proj_path, row['ImgInfoPath'])
        tiffPath = os.path.join(configuration.proj_path, row['ImgPath'])

        vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=pikPath, tiff_path=tiffPath)
        vi.update_workEnv()
        vi.viewer.workEnv.restore_rois_from_states()
        vi.viewer.ui.label_curr_img_seq_name.setText(sample_id)

        try:
            self.lwd.deleteLater()
        except:
            pass

        vi.viewer.workEnv.saved = True
        