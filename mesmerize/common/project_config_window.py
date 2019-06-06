#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
import sys
from . import get_project_manager, get_window_manager
from . import configuration
from .pytemplates.project_config_pytemplate import *
from numpy import int64, float64
from glob import glob
import pickle


'''
Just a simple GUI for modifying the project config file.
'''


class ColumnsPage(QtWidgets.QWidget):
    def __init__(self, parent=None, *args):
        QtWidgets.QWidget.__init__(self, parent, *args)
        self._context_menu_selected_list_widget = None
        self.setWindowTitle('Project Configuration')

    def setupGUI(self):
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        configuration.open_proj_config()
        self.ui.listwInclude.addItems(configuration.proj_cfg.options('INCLUDE'))
        self.ui.listwExclude.addItems(configuration.proj_cfg.options('EXCLUDE'))
        self.ui.listwROIDefs.addItems(configuration.proj_cfg.options('ROI_DEFS'))
        self.ui.listwStimDefs.addItems(configuration.proj_cfg.options('STIM_DEFS'))
        self.ui.listwCustomColumns.addItems(configuration.proj_cfg.options('CUSTOM_COLUMNS'))

        self.ui.radioButtonBoolean.clicked.connect(self.disable_custom_column_line_edit_validator)
        self.ui.radioButtonStr.clicked.connect(self.disable_custom_column_line_edit_validator)
        self.ui.radioButtonInt64.clicked.connect(self.set_custom_column_line_edit_validator)
        self.ui.radioButtonFloat64.clicked.connect(self.set_custom_column_line_edit_validator)
        
        self.ui.btnAddNewROICol.clicked.connect(self.add_roi_def)
        self.ui.btnAddNewStimCol.clicked.connect(self.add_stim_def)

        self.ui.btnAddCustomColumn.clicked.connect(self.add_custom_column)

        self.ui.btnSave.clicked.connect(self.save_config)

        self.custom_to_add = {}

        action_delete_column = QtWidgets.QWidgetAction(self)
        action_delete_column.setText('Delete column')
        action_delete_column.triggered.connect(self.delete_column)

        self.delete_column_menu = QtWidgets.QMenu(self)
        self.delete_column_menu.addAction(action_delete_column)

        self.ui.listwROIDefs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listwROIDefs.customContextMenuRequested.connect(lambda p: self.bulid_delete_menu(p, self.ui.listwROIDefs))

        self.ui.listwStimDefs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listwStimDefs.customContextMenuRequested.connect(lambda p: self.bulid_delete_menu(p, self.ui.listwStimDefs))

        self.ui.listwCustomColumns.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.listwCustomColumns.customContextMenuRequested.connect(lambda p: self.bulid_delete_menu(p, self.ui.listwCustomColumns))

        self.new_roi_defs = []
        # TODO: Deletable columns for ROI, Stim, and Custom columns.

    def bulid_delete_menu(self, p, list_widget):
        self._context_menu_selected_list_widget = list_widget
        self.delete_column_menu.exec_(list_widget.mapToGlobal(p))

    def delete_column(self):
        if self._context_menu_selected_list_widget is None:
            return
        item = self._context_menu_selected_list_widget.takeItem(self._context_menu_selected_list_widget.currentRow())

        includes = [self.ui.listwInclude.item(i).text() for i in range(self.ui.listwInclude.count())]

        if item.text() in includes:
            self.ui.listwInclude.takeItem(includes.index(item.text()))
            return

        excludes = [self.ui.listwExclude.item(i).text() for i in range(self.ui.listwExclude.count())]
        if item.text() in excludes:
            self.ui.listwExclude.takeItem(excludes.index(item.text()))

    def add_roi_def(self):
        if self.ui.lineEdNewROIDef.text() != '':
            text = self.ui.lineEdNewROIDef.text().replace(' ', '_')



            if text in get_project_manager().dataframe.columns:
                QtWidgets.QMessageBox.warning(self, 'Name already exists',
                                              'The entered column name already exists in the dataframe. '
                                              'Enter a different name.')
                return

            self.ui.listwROIDefs.addItem(text)
            self.ui.listwInclude.addItem(text)
            self.ui.lineEdNewROIDef.clear()
            self.new_roi_defs.append(text)
        
    def add_stim_def(self):
        if self.ui.lineEdNewStimCol.text() != '':
            text = self.ui.lineEdNewStimCol.text().replace(' ', '_')

            if text in get_project_manager().dataframe.columns:
                QtWidgets.QMessageBox.warning(self, 'Name already exists',
                                              'The entered column name already exists in the dataframe. '
                                              'Enter a different name.')

            self.ui.listwStimDefs.addItem(text)
            self.ui.listwInclude.addItem(text)
            self.ui.lineEdNewStimCol.clear()

    def save_config(self):
        if len(get_window_manager().flowcharts) > 0:
            if QtWidgets.QMessageBox.question(self,
                                              'Flowcharts are open',
                                              'Updating the project configuration while you are actively using a flowchart '
                                              'will remove the inputs to any <Load_Proj_DF> that are open and you will '
                                              'need to create these nodes again.\n'
                                              'Do you still want to continue?',
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return

        include = []
        for i in range(0, self.ui.listwInclude.count()):
            include.append(self.ui.listwInclude.item(i).text())
        configuration.proj_cfg['INCLUDE'] = dict.fromkeys(include)
        
        exclude = []
        for i in range(0, self.ui.listwExclude.count()):
            exclude.append(self.ui.listwExclude.item(i).text())
        configuration.proj_cfg['EXCLUDE'] = dict.fromkeys(exclude)
        
        roi_defs = []
        for i in range(0, self.ui.listwROIDefs.count()):
            roi_defs.append(self.ui.listwROIDefs.item(i).text())
        configuration.proj_cfg['ROI_DEFS'] = dict.fromkeys(roi_defs)

        images_dir = configuration.proj_path + '/images'
        for new_def in self.new_roi_defs:
            for f in glob(images_dir + '/*.pik'):
                p = pickle.load(open(f, 'rb'))
                for s in p['roi_states']['states']:
                    s['tags'].update({new_def: 'untagged'})
                pickle.dump(p, open(f, 'wb'))

        self.new_roi_defs = []

        stim_defs = []
        for i in range(0, self.ui.listwStimDefs.count()):
            stim_defs.append(self.ui.listwStimDefs.item(i).text())
        configuration.proj_cfg['STIM_DEFS'] = dict.fromkeys(stim_defs)

        custom_colums = [self.ui.listwCustomColumns.item(i).text() for i in range(self.ui.listwCustomColumns.count())]
        for c in configuration.proj_cfg.options('CUSTOM_COLUMNS'):
            if c not in custom_colums:
                configuration.proj_cfg.remove_option('CUSTOM_COLUMNS', c)

        for column in self.custom_to_add.keys():
            configuration.proj_cfg.set('CUSTOM_COLUMNS', column, str(self.custom_to_add[column]['type']))

        configuration.save_proj_config()
        get_project_manager().update_project_config_requested(self.custom_to_add)
        self.ui.btnClose.click()

    def set_custom_column_line_edit_validator(self):
        if self.ui.radioButtonInt64.isChecked():
            self.ui.lineEditCustomColumnReplacementValue.setValidator(QtGui.QIntValidator())
        elif self.ui.radioButtonFloat64.isChecked():
            self.ui.lineEditCustomColumnReplacementValue.setValidator(QtGui.QDoubleValidator())

    def disable_custom_column_line_edit_validator(self):
        self.ui.lineEditCustomColumnReplacementValue.setValidator(None)

    def add_custom_column(self):
        name = self.ui.lineEditCustomColumnName.text()
        if name == '':
            return

        if name in get_project_manager().dataframe.columns:
            QtWidgets.QMessageBox.warning(self, 'Name already exists',
                                          'The entered column name already exists in the dataframe. '
                                          'Enter a different name.')
            return

        replacement_value = self.ui.lineEditCustomColumnReplacementValue.text()

        if self.ui.radioButtonStr.isChecked():
            if replacement_value == '':
                replacement_value = 'untagged'
            column_type = 'str'

        elif self.ui.radioButtonInt64.isChecked():
            if replacement_value == '':
                replacement_value = 0
            else:
                replacement_value = int64(replacement_value)
            column_type = 'int64'

        elif self.ui.radioButtonFloat64.isChecked():
            if replacement_value == '':
                replacement_value = 0.0
            else:
                replacement_value = float64(replacement_value)
            column_type = 'float64'

        elif self.ui.radioButtonBoolean.isChecked():
            column_type = 'bool'

            if replacement_value not in ['True', 'False'] and not get_project_manager().dataframe.empty:
                QtWidgets.QMessageBox.warning(self, 'Invalid replacement value',
                                              'You can enter only True or False for boolean data types')
            else:
                replacement_value = bool(replacement_value)

        else:
            QtWidgets.QMessageBox.warning(self, 'No data type selected',
                                          'You must select a data type')
            return

        name = name.replace(' ', '_')
        self.ui.listwCustomColumns.addItem(name)
        self.ui.listwInclude.addItem(name)
        self.ui.lineEditCustomColumnReplacementValue.clear()
        self.ui.lineEditCustomColumnName.clear()

        self.custom_to_add.update({name: {'type': column_type, 'replacement_value': replacement_value}})


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = QtWidgets.QTabWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        
        # Adds a new tab, places an instance of TabPage widget which is displayed in the whole tab.
        self.tabs.addTab(ColumnsPage(self.tabs), 'Columns')
        # Setup the GUI in that tab
        self.tabs.widget(self.tabs.count() - 1).setupGUI()

        self.tabs.widget(0).ui.btnClose.clicked.connect(self.close)
