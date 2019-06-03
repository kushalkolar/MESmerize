#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget


class Lineplot(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        self.ax = self.fig.add_subplot(111)
        self.plot = None

    def set(self):
        pass

    def set_multi(self, data, num_columns: int = 1):
        pass

    def clear(self):
        self.ax.cla()
