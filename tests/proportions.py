#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from PyQt5 import QtWidgets
import pickle
from mesmerize.analysis import Transmission
from mesmerize.plotting import ProportionsWidget
from mesmerize.pyqtgraphCore.console import ConsoleWidget


def run() -> QtWidgets.QWidget:
    t = Transmission.from_hdf5('/share/data/temp/kushal/jorgen_wt_pfeatures.trn')
    y_pred = pickle.load(open('/work/kushal/kshape_20190622_173737/y_pred.pickle', 'rb'))
    t.df['y_pred'] = y_pred

    w = ProportionsWidget()
    w.set_input(t)

    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = run()
    c = ConsoleWidget(namespace={'this': w})
    c.show()
    app.exec_()
