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
        self.history_widget = HistoryTreeWidget(self)

    def set_history_widget(self, sources):
        self.dockWidgetTransmissions.setWidget(self.history_widget)
        self.history_widget.fill_widget(sources)
        self.dockWidgetTransmissions.show()

    def _set_curve_color(self):
        pass

if __name__ == '__main__':
    r, t = Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/peaks_new_with_bool.trn')
    pwin = Window()

    pwin.set_history_widget([t.src, t.src])