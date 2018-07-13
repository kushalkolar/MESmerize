# -*- coding: utf-8 -*-
"""
Example beeswarm / bar chart
"""
import sys
sys.path.append('..')
from pyqtgraphCore import ScatterPlotItem, PlotWidget, pseudoScatter
from pyqtgraphCore import GraphicsLayoutWidget
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import numpy as np
import pandas as pd
from uuid import uuid4, UUID

#win = pg.plot()
#win.setWindowTitle('pyqtgraph example: beeswarm')

data = np.random.normal(size=(4,20))
data[0] += 5
data[1] += 7
data[2] += 5
data[3] = 10 + data[3] * 2
df = pd.DataFrame(data.T, columns=['a', 'b', 'c', 'd'])
uuids = [uuid4() for i in range(20)]
dfuuid = pd.DataFrame(uuids, columns=['uuid'])
df = pd.concat([df, dfuuid], axis=1)

## Make bar graph
#bar = pg.BarGraphItem(x=range(4), height=data.mean(axis=1), width=0.5, brush=0.4)
#win.addItem(bar)

## add scatter plots on top
#for i in range(4):
#    xvals = pg.pseudoScatter(data[i], spacing=0.4, bidir=True) * 0.2
#    win.plot(x=xvals+i, y=data[i], pen=None, symbol='o', symbolBrush=pg.intColor(i,6,maxValue=128))

## Make error bars
#err = pg.ErrorBarItem(x=np.arange(4), y=data.mean(axis=1), height=data.std(axis=1), beam=0.5, pen={'color':'w', 'width':2})
#win.addItem(err)

class BeeswarmPlot(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = PlotWidget(self)
        self.scatter_plot = None
        self.plot = None
        layout.addWidget(self.plot_widget)        
        
        self.infinite_lines = []
        self.dataframe = pd.DataFrame()
        self.title = ''
        self.plot_columns = []
        self.current_datapoint = None
        self.lastClicked= []
    
    def set_data(self, dataframe: pd.DataFrame, title: str, plot_columns: list):
        self.dataframe = dataframe
        self.plot_columns = plot_columns
        self.title = title
        self._plot()
    
    def _plot(self):
        for i, column in enumerate(self.plot_columns):
            yvals = self.dataframe[column]
            xvals = pseudoScatter(yvals, spacing=0.4, bidir=True) * 0.2
            self.scatter_plot = ScatterPlotItem(title='baaaaaaah')
            self.scatter_plot.setData(x=xvals + i, y=yvals, uuid=self.dataframe['uuid'], name=column, pen=None, symbol='o', size=10)
            self.scatter_plot.sigClicked.connect(self._clicked)
            self.plot = self.plot_widget.addItem(self.scatter_plot)
    
    def _clicked(self, plot, points):
        print('yay')
        print(plot)
        print(points)
        self.lastClicked.append(points)
        if len(points) == 1:
            print(points[0].uuid)
#        return
#        i = 0
#        for item in self.inflines:
#            self.inflplots[i].removeItem(item)
#            i += 1
#
#        self.inflplots = []
#        self.inflines = []
#        for ii, p in enumerate(self.lastClicked):
#            p.resetPen()
#            p.setBrush(self.lastClickedColors[i])
#            ii += 1
#        self.lastClickedColors = []
#        for p in points:
#            self.lastClickedColors.append(p.brush())
#            p.setPen('w', width=4)
#        self.lastClicked = points
#        if len(self.lastClicked) == 1:
#            yval = self.lastClicked[0].pos()[1]
#
##            fcolvals = self.df[plot.name()].values
#
#            ix = np.where(fcolvals == yval)[0][0]
#
#            #            ix = self.df[self.df[plot.name()] == yval].index[0]
#
#            #            print(self.df.iloc[ix])
#            for f in self.fcols:
#                try:
#                    val = self.df.iloc[ix][f]
#                    il = pg.InfiniteLine(pos=val, angle=0, pen='w')
#
#                    print(self.df.iloc[ix])
#                    self.plots[f].addItem(il)
#                    self.inflines.append(il)
#                    self.inflplots.append(self.plots[f])
#                except ValueError as e:
#                    continue
    @property
    def spot_color(self, group: str):
        pass

    @spot_color.setter
    def spot_color(self, d: dict):
        pass
    
    @property
    def spot_outline(self):
        pass
    
    @spot_outline.setter
    def spot_outline(self, color):
        pass
            
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, title: str):
        pass
    
    @property
    def spot_size(self) -> int:
        pass
    
    @spot_size.setter
    def spot_size(self, size: int):
        pass
    
    def clear_plot(self):
        pass
    
    def export_all_plots(self):
        pass
    
    def export_plot(self, column: str, filetype: str = 'svg', title: str = None, error_bars: str = 'mean', spots_color=None, spots_outline='black', background_color='black', axis_color='white'):
        pass
   

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bp = BeeswarmPlot()
    bp.set_data(df, 'bah_title', ['a', 'b', 'c'])
    bp.show()
    app.exec()