#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 18 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
from PyQt5 import QtCore, QtGui, QtWidgets
from .add_to_project_dialog_pytemplate import Ui_Form
from common import configuration
from .viewer_work_environment import ViewerWorkEnv
from numpy import int64, float64


class AddToProjectDialog(QtWidgets.QWidget):
    signal_finished = QtCore.pyqtSignal()

    def __init__(self, work_environment: ViewerWorkEnv):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Add to project')

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.setWindowTitle('Add to Project')

        self.work_environment = work_environment

        if self.work_environment.sample_id != '' and self.work_environment.sample_id is not None:
            self.ui.lineEditAnimalID.setText(self.work_environment.sample_id.split('-_-')[0])
            self.ui.lineEditTrialID.setText(self.work_environment.sample_id.split('-_-')[1])
            self.ui.radioButtonSaveChanges.setVisible(True)
        else:
            self.ui.radioButtonSaveChanges.setVisible(False)

        self.custom_column_entries = []

        for custom_column in configuration.proj_cfg.options('CUSTOM_COLUMNS'):
            data_type = configuration.proj_cfg['CUSTOM_COLUMNS'][custom_column]

            if data_type == 'bool':
                combo_box = QtWidgets.QComboBox(self)
                combo_box.setObjectName(custom_column)

                combo_box.addItems(['True', 'False'])

                label = QtWidgets.QLabel(self)
                label.setText(custom_column)

                self.ui.verticalLayout.insertWidget(2, combo_box)
                self.ui.verticalLayout.insertWidget(2, label)

                self.custom_column_entries.append(combo_box)

            else:
                line_edit = QtWidgets.QLineEdit(self)
                line_edit.setObjectName(custom_column)
                line_edit.setPlaceholderText(custom_column + ' :' + data_type)

                self.ui.verticalLayout.insertWidget(2, line_edit)

                if data_type == 'int64':
                    line_edit.setValidator(QtGui.QIntValidator())
                elif data_type == 'float64':
                    line_edit.setValidator(QtGui.QDoubleValidator())

                self.custom_column_entries.append(line_edit)

        self.ui.checkBoxSaveChanges.setVisible(False)

        self.ui.btnProceed.clicked.connect(self.slot_proceed)

    def update_work_environment_dicts(self):
        animal_id = self.ui.lineEditAnimalID.text()
        trial_id = self.ui.lineEditTrialID.text()
        sample_id = animal_id + '-_-' + trial_id

        self.work_environment.sample_id = sample_id

        self.work_environment.comments = self.ui.textBoxComments.toPlainText()

        for entry in self.custom_column_entries:
            if isinstance(entry, QtWidgets.QLineEdit):
                val = entry.text()

                if configuration.proj_cfg['CUSTOM_COLUMNS'][entry.objectName()] == 'int64':
                    val = int64(val)
                elif configuration.proj_cfg['CUSTOM_COLUMNS'][entry.objectName()] == 'float64':
                    val = float64(val)

            elif isinstance(entry, QtWidgets.QComboBox):
                if entry.currentText() == 'True':
                    val = True
                elif entry.currentText() == 'False':
                    val = False

            self.work_environment.custom_columns_dict.update({entry.objectName(): val})

    def must_enter_sample_id_dialog(self):
        QtWidgets.QMessageBox.warning(self, 'Animal & Trial ID', 'You must enter Animal ID and Trial ID')

    def slot_proceed(self):
        if self.ui.lineEditAnimalID == '':
            self.must_enter_sample_id_dialog()
            return
        if self.ui.lineEditTrialID == '':
            self.must_enter_sample_id_dialog()
            return

        animal_id = self.ui.lineEditAnimalID.text()
        trial_id = self.ui.lineEditTrialID.text()
        sample_id = animal_id + '-_-' + trial_id

        if (sample_id in configuration.project_manager.dataframe['SampleID'].values) and not self.check_save_changes():
            QtWidgets.QMessageBox.warning(self, 'SampleID exists in project',
                                          'The combination of animal ID and '
                                          'trial ID already exists in the project dataframe. '
                                          'You must choose a unique combination.')
            return

        self.setDisabled(True)
        self.label_wait = QtWidgets.QLabel(self)
        self.label_wait.setText('Please wait...')
        self.ui.verticalLayout.addWidget(self.label_wait)

        self.update_work_environment_dicts()

        if self.ui.radioButtonAddToDataFrame.isChecked():
            self.add_to_dataframe()

        elif self.check_save_changes():
            self.save_changes_to_sample()

    def check_save_changes(self):
        if self.ui.radioButtonSaveChanges.isChecked() and self.ui.checkBoxSaveChanges.isChecked():
            return True
        else:
            return False

    def add_to_dataframe(self):
        dicts_to_append = self.work_environment.to_pandas(configuration.proj_path)
        configuration.project_manager.append_to_dataframe(dicts_to_append)
        self.work_environment.saved = True
        self.label_wait.setText('FINISHED!')
        # self.signal_finished.emit()

    def save_changes_to_sample(self):
        dicts_to_append = self.work_environment.to_pandas(configuration.proj_path)
        configuration.project_manager.change_sample_rows(self.work_environment.sample_id, dicts_to_append)
        self.work_environment.saved = True
        self.label_wait.setText('FINISHED!')

        # self.signal_finished.emit()

    def close(self):
        self.signal_finished.emit()
        super(AddToProjectDialog, self).close()