# -*- coding: utf-8 -*-
"""
This example demonstrates a very basic use of flowcharts: filter data,
displaying both the input and output of the filter. The behavior of
the filter can be reprogrammed by the user.

Basic steps are:
  - create a flowchart and two plots
  - input noisy data to the flowchart
  - flowchart connects data to the first plot, where it is displayed
  - add a gaussian filter to lowpass the data, then display it in the second plot.
"""
import sys
# import initExample ## Add path to library (just for examples; you do not need this)
sys.setrecursionlimit(10000)
from pyqtgraphCore.flowchart import Flowchart
from pyqtgraphCore.Qt import QtGui, QtCore
import pyqtgraphCore as pg
import numpy as np
import pyqtgraphCore.metaarray as metaarray
import pickle
from analyser.DataTypes import Transmission
from MesmerizeCore import configuration

app = QtGui.QApplication([])

configuration.configpath = '/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/config.cfg'
configuration.openConfig()

## Create main window with grid layout
win = QtGui.QMainWindow()
win.setWindowTitle('pyqtgraph example: Flowchart')
cw = QtGui.QWidget()
win.setCentralWidget(cw)
layout = QtGui.QGridLayout()
cw.setLayout(layout)

## Create flowchart, define input/output terminals
fc = Flowchart(terminals={
    'dataIn': {'io': 'in'},
    'dataOut': {'io': 'out'}    
})
w = fc.widget()

## Add flowchart control panel to the main window
layout.addWidget(fc.widget(), 0, 0, 2, 1)

## Add two plot widgets
pw1 = pg.PlotWidget()
pw2 = pg.PlotWidget()
layout.addWidget(pw1, 0, 1)
layout.addWidget(pw2, 1, 1)

win.show()

## generate signal data to pass through the flow

r, data = Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/testprojects/feb6-test-10/raw_transmission_test.trn')

data.data_column = {'curve': 'curve'}

## Feed data into the input terminal of the flowchart
fc.setInput(dataIn=data)

## populate the flowchart with a basic set of processing nodes. 
## (usually we let the user do this)
plotList = {'Top Plot': pw1, 'Bottom Plot': pw2}

pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
pw1Node.setPlotList(plotList)
pw1Node.setPlot(pw1)

pw2Node = fc.createNode('PlotWidget', pos=(150, -150))
pw2Node.setPlot(pw2)
pw2Node.setPlotList(plotList)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
#    sys.exit(app.exec_())
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
