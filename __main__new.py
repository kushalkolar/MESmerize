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
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
from MesmerizeCore import welcome_window


if __name__ == '__main__':
    print(sys.argv)
    app = QtWidgets.QApplication([])

    if not len(sys.argv) > 1:
        w = welcome_window.MainWindow()
        w.show()
    else:
        pass

    app.exec_()
