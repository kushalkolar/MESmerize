# -*- coding: utf-8 -*-
'''
!!! ** NOT A PART OF MESMERIZE. JUST FOR TESTING ** !!!
'''
"""
This example demonstrates the use of ImageView, which is a high-level widget for 
displaying and analyzing 2D and 3D data. ImageView provides:

  1. A zoomable region (ViewBox) for displaying the image
  2. A combination histogram and gradient editor (HistogramLUTItem) for
     controlling the visual appearance of the image
  3. A timeline for selecting the currently displayed frame (for 3D data only).
  4. Tools for very basic analysis of image data (see ROI and Norm buttons)

"""

## Add path to library (just for examples; you do not need this)
#import initExample

import numpy as np
from pyqtgraphCore.Qt import QtCore, QtGui
import pyqtgraphCore as pg
#import MesmerizeCore.FileInput as FileInput

# Interpret image data as row-major instead of col-major
pg.setConfigOptions(imageAxisOrder='row-major')

app = QtGui.QApplication([])

## Create window with ImageView widget
win = QtGui.QMainWindow()
win.resize(1400,980)
viewer = pg.ImageView()
win.setCentralWidget(viewer)
win.show()
win.setWindowTitle('Mesmerize - viewer')

## Set a custom color map
colors = [
    (0, 0, 0),
    (45, 5, 61),
    (84, 42, 55),
    (150, 87, 60),
    (208, 171, 141),
    (255, 255, 255)
]
cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
viewer.setColorMap(cmap)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
