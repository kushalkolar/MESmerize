#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon March 5 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from typing import Union


class HistoryTreeWidget(QtWidgets.QTreeWidget):
    _exclude_top_level_expansion = {'CurvePath', 'ImgInfoPath', 'ImgPath', 'ImgUUID',
                                    'ROI_State','meta', 'sitm_maps', 'uuid_curve'}
    
    def __init__(self, parent=None):
        super(HistoryTreeWidget, self).__init__(parent)
        self.top_level_keys = None

    def fill_widget(self, src: Union[dict, list]):
        """
        :param src: dict or list to fill in the tree widget.
        """
        self.clear()
        if type(src) is dict:
            self.top_level_keys = set(src.keys()) - self._exclude_top_level_expansion

        self._fill_item(self.invisibleRootItem(), src)

    def _fill_item(self, item, value):
        tn = 0
        # item.setExpanded(True)
        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, str(key))
                item.addChild(child)
                self._fill_item(child, val)

        elif type(value) is list:
            for val in value:
                child = QtWidgets.QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, self._get_key(val))
                    for v in val.values():
                        self._fill_item(child, v)
                elif type(val) is list:
                    child.setText(0, 'Transmission ' + str(tn))
                    self._fill_item(child, val)
                    tn += 1
                else:
                    child.setText(0, str(val))
                # child.setExpanded(False)
        else:
            child = QtWidgets.QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)

        if self.top_level_keys is not None:
            self._expand_top_level()

    def _expand_top_level(self):
        for k in self.top_level_keys:
            if str(k).startswith('_'):
                continue
            items = self.findItems(k, Qt.MatchExactly)
            for item in items:
                item.setExpanded(True)

    def _get_key(self, d):
        k = ''
        for key in d.keys():
            k = key + k
        return k
    
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    history_tree = HistoryTreeWidget()
    win.setCentralWidget(history_tree)
    import pickle

    df = pickle.load(open('/share/data/longterm/4/kushal/kushal_on_ssd2/cell_types_project/fft_data_with_index.trn', 'rb'))['df']

    history_tree.fill_widget(df.iloc[0].to_dict())
    win.resize(300, 600)

    win.show()
    app.exec_()
