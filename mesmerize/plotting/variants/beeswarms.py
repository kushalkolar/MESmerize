# -*- coding: utf-8 -*-
"""
Example beeswarm / bar chart
"""

from ...pyqtgraphCore import ScatterPlotItem, SpotItem, pseudoScatter, GraphicsLayoutWidget
from ...pyqtgraphCore.Qt import QtCore, QtGui, QtWidgets
import pandas as pd
from uuid import UUID


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
# TODO: ERROR BARS
class BeeswarmPlot(QtCore.QObject):
    signal_spot_clicked = QtCore.pyqtSignal(UUID)

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
        self.pseudo_plots = []

        # self.legend = self.graphics_view
        # self.legend.setParentItem(self.plots)

        self.color_legend_items = []

    def add_plot(self, title: str):
        if len(self.scatter_plots) % 4 == 0:
            self.graphics_view.nextRow()
        plot = self.graphics_view.addPlot(title=title)
        scatter_plot = ScatterPlotItem(title=title)
        scatter_plot.sigClicked.connect(self._clicked)

        plot.addItem(scatter_plot)
        self.scatter_plots.append({'scatter_plot': scatter_plot, 'i': 0})
        self.plots.append(plot)

    def add_data_to_plot(self, ix: int, data_series: pd.Series, uuid_series: pd.Series, name, color):
        if ix > len(self.plots) - 1:
            raise IndexError('Plot index out of range.')

        not_nan = data_series.notna()
        yvals = data_series[not_nan].values
        xvals = pseudoScatter(yvals, spacing=0.025, bidir=True) * 0.4
        scatter_plot = self.scatter_plots[ix]['scatter_plot']
        self.scatter_plots[ix]['i'] += 1
        i = self.scatter_plots[ix]['i']
        scatter_plot.addPoints(x=xvals + i, y=yvals, uuid=uuid_series[not_nan], name=name, brush=color, pen='k', symbol='o', size=10)

    def _clicked(self, plot, points):
        for i, p in enumerate(self.lastClicked):
            assert isinstance(p, SpotItem)
            p.setPen('w')
            # p.setBrush(p._data['orig_brush'])

        if len(points) == 1:
            p = points[0]
            assert isinstance(p, SpotItem)
            self.signal_spot_clicked.emit(p.uuid)

        for p in points:
            assert isinstance(p, SpotItem)
            p.setPen('k')
            # p.setBrush('w')

        self.lastClicked = points

    def set_legend(self, colors: dict, shapes: dict = None):
        """
        :param colors: {'group_name': QtGui.QColor}
        :param shapes: {'group_name': <shape>}
        :return:
        """
        return
        self.clear_legend()

        for k in colors.keys():
            p = ScatterPlotItem()
            p.setData(x=[0], y=[0], brush=colors[k])
            self.color_legend_items.append(k)
            self.legend.addItem(p, k)
            self.pseudo_plots.append(p)

    def clear_legend(self):
        for i in range(len(self.pseudo_plots)):
            del self.pseudo_plots[0]

        for name in self.color_legend_items:
            self.legend.removeItem(name)
        self.color_legend_items.clear()


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
    
    def clear_plots(self):
        for plot in self.plots:
            self.graphics_view.removeItem(plot)
            plot.deleteLater()
        del self.plots
        self.plots = []
        del self.scatter_plots
        self.scatter_plots = []

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