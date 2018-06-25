#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraphCore.widgets.ColorButton import ColorButton
from functools import partial
if __name__ == '__main__':
    from main_widget_pytemplate import Ui_MainWidget
    from tab_page_pytemplate import Ui_TabPage
else:
    from .main_widget_pytemplate import Ui_MainWidget
    from .tab_page_pytemplate import Ui_TabPage


# class StimulusMap:
#     def __init__(self):
#         self.data = None
#
#
#
#
#     @staticmethod
#     def get_empty_dataframe():
#         return pd.DataFrame(columns=['name', 'start', 'stop', 'color'])
#
#     def from_mes_data(self):
#         self._stimMaps = {}
#
#         if origin == 'mesfile':
#             # Organize stimulus maps from mesfile objects
#             try:
#                 mes_meta = self.meta['orig_meta']
#             except (KeyError, IndexError) as e:
#                 raise KeyError('Stimulus Data not found! Could not find the stimulus data in the meta-data for this image.')
#                 self.data = None
#                 return
#             for machine_channel in dm.keys():
#                 ch_dict = dm[machine_channel]
#                 try:
#                     y = mes_meta[machine_channel]['y']
#                     x = mes_meta[machine_channel]['x'][1]
#
#                     firstFrameStartTime = mes_meta['FoldedFrameInfo']['firstFrameStartTime']
#                     frameTimeLength = mes_meta['FoldedFrameInfo']['frameTimeLength']
#
#                     current_map = []
#
#                     for i in range(0, y.shape[1] - 1):
#                         # To convert negative zero to positive zero, and correct for floating point errors
#                         voltage = str(fix_fp_errors(y[1][i]))
#
#                         tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)
#
#                         if tstart_frame < 0:
#                             tstart_frame = 0
#
#                         tend_frame = int(((y[0][i + 1] * x) - firstFrameStartTime) / frameTimeLength)
#
#                         current_map.append([ch_dict['values'][voltage], (tstart_frame, tend_frame)])
#
#                     self._stimMaps[ch_dict['channel_name']] = current_map
#
#                 except (KeyError, IndexError) as e:
#                     QtGui.QMessageBox.information(None, 'FYI: Missing channels in current image',
#                                                   'Voltage values not found for: "' + str(ch_dict['channel_name']) + \
#                                                   '" in <' + str(machine_channel) + '>.\n' + str(e),
#                                                   QtGui.QMessageBox.Ok)
#
#             return
#
#     def from_csv(self):
#         pass
#
#     def from_manual_entry(self):
#         pass


class GUI(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        # self.ui.btnAddRow.clicked.connect(self.add_row)

    def add_stim_type(self, stim_type):
        self.ui.tabWidget.addTab(Page(parent=self, name=stim_type), stim_type)

    # def add_row(self):
    #     row = Row(parent=self)
    #     self.ui.tabWidget.currentWidget().vlayout.addWidget(row)

    def get_all_stims_dataframes(self) -> dict:
        d = {}
        for ix in range(self.ui.tabWidget.count()):
            name = self.ui.tabWidget.widget(ix).name
            df = self.ui.tabWidget.widget(ix).get_dataframe()
            d[name] = df
        return d

    def export_map(self):
        pass

    def import_map(self):
        pass


class Page(QtWidgets.QWidget):
    def __init__(self, parent, name):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_TabPage()
        self.ui.setupUi(self)

        self.rows = []
        self.ui.btnAddRow.clicked.connect(self.add_row)

    def set_data(self, dataframe: pd.DataFrame):
        self.clear()
        for ix, series in dataframe.iterrows():
            self.add_row(series)

    def add_row(self, pd_series=None):
        row = Row(pd_series)
        row.btn_remove.clicked.connect(partial(self.delete_row, row))
        self.ui.verticalLayout.insertLayout(self.ui.verticalLayout.count() - 1, row.hlayout)
        self.rows.append(row)

    def delete_row(self, row):
        self.ui.verticalLayout.removeItem(row.hlayout)
        row.delete()
        row.hlayout.deleteLater()
        row.deleteLater()
        self.rows.remove(row)

    def clear(self):
        for row in self.rows:
            self.delete_row(row)

    def get_dataframe(self) -> pd.DataFrame:
        l = []
        for row in self.rows:
            l.append(row.get_dict())
        return pd.DataFrame(l)


class Row(QtWidgets.QWidget):
    def __init__(self, pd_series=None, label=None):

        """
        :type pd_series: pd.Series
        :type label: str
        """
        QtWidgets.QWidget.__init__(self)

        self.hlayout = QtWidgets.QHBoxLayout()

        if label is not None:
            self.qlabel = QtWidgets.QLabel(self)
            self.qlabel.setText(label)
            self.hlayout.addWidget(self.qlabel)
        else:
            self.qlabel = QtWidgets.QLabel(self)

        self.name = QtWidgets.QLineEdit(self)
        self.name.setPlaceholderText('Stimulus Name')
        self.hlayout.addWidget(self.name)

        self.start = QtWidgets.QLineEdit(self)
        self.start.setValidator(QtGui.QDoubleValidator())
        self.start.setPlaceholderText('Start time')
        self.hlayout.addWidget(self.start)

        self.end = QtWidgets.QLineEdit(self)
        self.end.setPlaceholderText('End time')
        self.end.setValidator(QtGui.QDoubleValidator())
        self.hlayout.addWidget(self.end)

        self.color_btn = ColorButton(self)
        self.hlayout.addWidget(self.color_btn)

        self.btn_remove = QtWidgets.QPushButton(self)
        self.btn_remove.setText('Remove stim')
        self.hlayout.addWidget(self.btn_remove)

        if pd_series is not None:
            self.name.setText(pd_series['name'])
            self.start.setText(pd_series['start'])
            self.end.setText(pd_series['end'])
            self.color_btn.setColor(pd_series['color'])

    def get_dict(self) -> dict:
        d = {'name': self.name.text(),
             'start': self.start.text(),
             'end': self.end.text(),
             'color': self.color_btn.color()
             }
        return d

    def delete(self):
        self.qlabel.deleteLater()
        self.name.deleteLater()
        self.start.deleteLater()
        self.end.deleteLater()
        self.btn_remove.deleteLater()
        self.color_btn.deleteLater()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = GUI()
    w.add_stim_type('bah test')
    w.add_stim_type('bah test2')
    w.show()
    app.exec_()
