#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 5 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mesmerize.common import start
# from analysis.DataTypes import Transmission
#
#
# from clustering.LDA.main_window import LDAPlot
# import pickle

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    start.window_manager()
    # w = LDAPlot()
    #
    # t = Transmission.from_pickle('/home/kushal/MESmerize/clustering/LDA/test_df.pickle')
    # w.update_input_transmissions([t])
    #
    # w.show()


    if not len(sys.argv) > 1:
        start.main()

    elif sys.argv[1] == 'run':
        if sys.argv[2] == 'batch':
            start.main()
            start.background_batch([sys.argv[3], sys.argv[4]])

    elif sys.argv[1].endswith('.tiff') or sys.argv[1].endswith('.tif'):
        start.viewer(sys.argv[1])

    elif sys.argv[1].endswith('.fc') or sys.argv[1].endswith('.fcd'):
        start.flowchart(sys.argv[1])

    else:
        raise ValueError('Invalid argument')

    app.exec_()
