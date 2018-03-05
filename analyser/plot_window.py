#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon March 5 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import sys
sys.path.append('..')
if __name__ == '__main__':
    from plot_window_pytemplate import *
    from DataTypes import Transmission
    from HistoryWidget import HistoryTreeWidget
else:
    from .plot_window_pytemplate import *
    from .DataTypes import Transmission
    from .HistoryWidget import HistoryTreeWidget


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, *args):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Mesmerize - Plot')
        self.show()
        self.history_widget = HistoryTreeWidget()

    def set_history_widget(self, sources):
        self.dockWidgetTransmissions.setWidget(self.history_widget)
        self.history_widget.fill_widget(sources)
        self.dockWidgetTransmissions.show()

    # def _fill_item(self, item, value):
    #     tn = 0
    #     item.setExpanded(True)
    #     if type(value) is dict:
    #         for key, val in sorted(value.items()):
    #             child = QtWidgets.QTreeWidgetItem()
    #             child.setText(0, key)
    #             item.addChild(child)
    #             self._fill_item(child, val)
    #
    #     elif type(value) is list:
    #         for val in value:
    #             child = QtWidgets.QTreeWidgetItem()
    #
    #             item.addChild(child)
    #             if type(val) is dict:
    #                 child.setText(0, self._get_key(val))
    #                 for v in val.values():
    #                     self._fill_item(child, v)
    #             elif type(val) is list:
    #                 child.setText(0, 'Transmission ' + str(tn))
    #                 self._fill_item(child, val)
    #                 tn +=1
    #             else:
    #                 child.setText(0, str(val))
    #             child.setExpanded(False)
    #     else:
    #         child = QtWidgets.QTreeWidgetItem()
    #         child.setText(0, str(value))
    #         item.addChild(child)
    #
    # def _get_key(self, d):
    #     k = ''
    #     for key in d.keys():
    #         k = key + k
    #     return k
    #
    # def fill_widget(self, value):
    #     widget = QtWidgets.QTreeWidget()
    #     widget.clear()
    #     self._fill_item(widget.invisibleRootItem(), value)
    #     self.dockWidgetTransmissions.setWidget(widget)
    #     self.dockWidgetTransmissions.show()



if __name__ == '__main__':
    r, t = Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/peaks_new_with_bool.trn')
    pwin = Window()

    pwin.set_history_widget([t.src, t.src])