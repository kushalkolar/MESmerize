#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon March 5 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets


class HistoryTreeWidget(QtWidgets.QTreeWidget):
    def fill_widget(self, src_list: list):
        """
        :param src_list: List of Transmission.src objects.
        """
        self.clear()
        self._fill_item(self.invisibleRootItem(), src_list)

    def _fill_item(self, item, value):
        tn = 0
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QtWidgets.QTreeWidgetItem()
                child.setText(0, key)
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
                child.setExpanded(False)
        else:
            child = QtWidgets.QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)

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
    win.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
