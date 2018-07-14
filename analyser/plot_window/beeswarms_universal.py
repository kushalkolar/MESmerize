# -*- coding: utf-8 -*-
"""
Example beeswarm / bar chart
"""
import sys
sys.path.append('..')
from pyqtgraphCore import ScatterPlotItem, SpotItem, pseudoScatter, mkColor, GraphicsLayoutWidget
from pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import numpy as np
import pandas as pd
from uuid import uuid4, UUID
from matplotlib import cm as matplotlib_color_map


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

class BeeswarmPlot(QtCore.QObject):
    def __init__(self, graphics_view: GraphicsLayoutWidget, parent=None):
        # QtWidgets.QWidget.__init__(self)
        QtCore.QObject.__init__(self, parent)
        # layout = QtWidgets.QVBoxLayout(self)
        self.graphics_view = graphics_view
        self.plots = []
        self.scatter_plots = []
        # layout.addWidget(self.plot_widget)
        
        self.infinite_lines = []
        self.title = ''
        self.current_datapoint = None
        self.lastClicked = []
    
    def set_plot_data(self, ix: int, dataframe: pd.DataFrame, plot_columns: list, plot_column_colors: list = None):
        if ix > len(self.plots) - 1:
            raise IndexError('Plot index out of range.')

        self.dataframe = dataframe
        self.plot_columns = plot_columns

        if plot_column_colors is None:
            plot_column_colors = self._auto_colormap(len(plot_columns))

        self._plot(ix, dataframe, plot_columns, plot_column_colors)

    def _auto_colormap(self, number_of_colors: int) -> list:
        cm = matplotlib_color_map.get_cmap('hsv')
        cm._init()
        lut = (cm._lut * 255).view(np.ndarray)
        cm_ixs = np.linspace(0, 210, number_of_colors, dtype=int)

        colors = []
        for ix in range(number_of_colors):
            c = lut[cm_ixs[ix]]
            colors.append(mkColor(c))

        return colors

    def add_plot(self, title: str):
        plot = self.graphics_view.addPlot(title=title)
        scatter_plot = ScatterPlotItem(title=title)
        plot.addItem(scatter_plot)
        self.scatter_plots.append(scatter_plot)
        self.plots.append(plot)

    def _plot(self, ix: int, dataframe: pd.DataFrame, plot_columns: list, plot_column_colors: list):
        for i, column in enumerate(plot_columns):
            color = plot_column_colors[i]
            yvals = dataframe[column]
            xvals = pseudoScatter(yvals, spacing=0.4, bidir=True) * 0.2
            scatter_plot = self.scatter_plots[ix]
            scatter_plot.addPoints(x=xvals + i, y=yvals, uuid=self.dataframe['uuid'], name=column, brush=color, pen='k', symbol='o', size=10)
        scatter_plot.sigClicked.connect(self._clicked)

    def _clicked(self, plot, points):
        for i, p in enumerate(self.lastClicked):
            assert isinstance(p, SpotItem)
            print(p._data)
            p.setPen(p._data['orig_pen'])
            p.setBrush(p._data['orig_brush'])

        if len(points) == 1:
            p = points[0]
            assert isinstance(p, SpotItem)
            print(p.uuid)

        for p in points:
            assert isinstance(p, SpotItem)
            p.setPen('w')
            p.setBrush('w')

        self.lastClicked = points

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