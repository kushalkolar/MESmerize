# -*- coding: utf-8 -*-
from ... import PlotDataItem, ComboBox
from analysis import simple_plot_window
from .common import *
import numpy as np
import pandas as pd
from plotting.widgets import HeatmapTracerWidget
from plotting.widgets import ScatterPlotWidget
from plotting.widgets import BeeswarmPlotWindow
from plotting.variants.timeseries import TimeseriesPlot


class Plot(CtrlNode):
    """Plot curves and/or scatter points"""
    nodeName = 'Plot'
    uiTemplate = [('Show', 'check', {'checked': True}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('data_column', 'combo', {})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})#, 'Out': {'io': 'out'}})
        self.trans_ids = []
        self.pwin = simple_plot_window.PlotWindow()
        self.ctrls['Apply'].clicked.connect(self.update)
        self.ctrls['Show'].clicked.connect(self.pwin.setVisible)

    def process(self, **kwargs):
        transmissions = kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        transmissions = merge_transmissions(transmissions)

        columns = pd.concat([t.df for t in transmissions]).columns
        self.ctrls['data_column'].setItems(columns.to_list())

        if self.ctrls['Apply'].isChecked() is False:
            return
        data_column = self.ctrls['data_column'].currentText()
        self.pwin.graphicsView.clear()

        srcs = []
        plots = []
        colors = ['m', 'r', 'y', 'g', 'c', 'b']
        ci = 0
        for t in transmissions:
            if t is None:
                srcs.append(str(type(None)))
                continue

            if id(t) in self.trans_ids:
                continue

            for ix, r in t.df.iterrows():

                if data_column in r.index:
                    data = r[data_column]
                # elif 'peak_curve' in r.index:
                #     data = r['peak_curve']
                else:
                    srcs.append('No data found in chosen column!')
                    continue
                if data is None:
                    srcs.append('No data found in chosen column!')
                    continue

                plot = PlotDataItem()
                try:
                    plot.setData(data)
                    # plot.setData(data / np.maximum(np.min(data), 0.0000000001))
                    plot.setPen(colors[ci])
                except Exception as e:
                    srcs.append('Plotting error: ' + str(e))
                    continue

                self.pwin.graphicsView.addItem(plot)

            ci += 1

        self.pwin.set_history_widget(srcs)


class FrequencyDomainMagnitude(CtrlNode):
    """Plot Frequency vs. Frequency Domain Magnitude"""
    nodeName = 'FDM Plot'
    uiTemplate = [('Show', 'check', {'checked': True}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})
                  ]


class Timeseries(CtrlNode):
    """Seaborn Timeseries plot"""
    nodeName = 'Timeseries'
    uiTemplate = [('data_column', 'combo', {}),
                  ('err_style', 'combo', {'items': ['band', 'bars']}),
                  ('Show', 'button', {'text': 'Show'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.ctrls['Apply'].clicked.connect(self.update)
        self.timeseries_widget = TimeseriesPlot()
        self.ctrls['Show'].clicked.connect(self.timeseries_widget.show)

    def process(self, **kwargs):
        transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        columns = self.t.df.columns.to_list()

        self.ctrls['data_column'].setItems(columns)

        if not self.ctrls['Apply'].isChecked():
            return

        data_column = self.ctrls['data_column'].currentText()
        data = np.vstack(self.t.df[data_column].values)

        es = self.ctrls['err_style'].currentText()

        self.timeseries_widget.set(data=data, err_style=es)


class Heatmap(CtrlNode):
    """Stack 1-D arrays and plot visually like a heatmap"""
    nodeName = "Heatmap"
    uiTemplate = [('Show', 'button', {'text': 'Show'}),
                  ('data_column', 'combo', {}),
                  ('labels', 'combo', {}),
                  ('colormap', 'cmaplist', {}),
                  ('DPT_curve', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})#, 'Out': {'io': 'out'}})
        self.trans_ids = []
        self.ctrls['Apply'].clicked.connect(self.update)
        self.heatmap_widget = HeatmapTracerWidget()
        self.ctrls['Show'].clicked.connect(self.heatmap_widget.show)
        self.ctrls['colormap'].signal_colormap_changed.connect(self.set_cmap)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        # self.dfs = [t.df for t in self.transmissions_list]

        # columns = pd.concat(self.dfs).columns

        columns = self.t.df.columns

        self.ctrls['data_column'].setItems(columns.to_list())
        self.ctrls['labels'].setItems(columns.to_list())
        self.ctrls['DPT_curve'].setItems(columns.to_list())

        self.labels_column = self.ctrls['labels'].currentText()

        self.dpt_curve_curve = self.ctrls['DPT_curve'].currentText()

        cmap = self.ctrls['colormap'].current_cmap

        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.heatmap_widget.set_data(dataframes=self.t.df, data_column=self.data_column,
                                     labels_column=self.labels_column,
                                     datapoint_tracer_curve_column=self.dpt_curve_curve,
                                     cmap=cmap, transmission=self.t)
        
    def set_cmap(self, cmap: str):
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.heatmap_widget.set_data(dataframes=self.t.df, data_column=self.data_column,
                                     labels_column=self.labels_column,
                                     datapoint_tracer_curve_column=self.dpt_curve_curve,
                                     cmap=cmap, transmission=self.t, reset_data=False)


class ScatterPlot(CtrlNode):
    """Scatter Plot, useful for visualizing transformed data and clusters"""
    nodeName = "ScatterPlot"
    uiTemplate = [('Show', 'button', {'text': 'Show'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_gui = None
        self.ctrls['Show'].clicked.connect(self._open_plot_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_gui is None:
            return

        transmissions = kwargs['In']

        transmissions_list = merge_transmissions(transmissions)

        self.plot_gui.update_input_transmissions(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_gui is None:
            self.plot_gui = ScatterPlotWidget(parent=self.parent())
        self.plot_gui.show()


class BeeswarmPlots(CtrlNode):
    """Beeswarm and Violin plots"""
    nodeName = 'BeeswarmPlots'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_gui = None
        self.ctrls['ShowGUI'].clicked.connect(self._open_plot_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_gui is None:
            return

        transmissions = kwargs['In']
        transmissions_list = merge_transmissions(transmissions)

        # transmissions = kwargs['In']
        #
        # if not len(transmissions) > 0:
        #     raise Exception('No incoming transmissions')
        #
        # transmissions_list = []
        #
        # for t in transmissions.items():
        #     t = t[1]
        #     if t is None:
        #         QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
        #         continue
        #     if type(t) is list:
        #         for i in range(len(t)):
        #             if t[i] is None:
        #                 QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
        #                 continue
        #             transmissions_list.append(t[i].copy())
        #         continue
        #
        #     transmissions_list.append(t.copy())

        self.plot_gui.update_input_transmissions(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_gui is None:
            self.plot_gui = BeeswarmPlotWindow(parent=self.parent())
        self.plot_gui.show()



# class PlotWidgetNode(Node):
#     """Connection to PlotWidget. Will plot arrays, metaarrays, and display event lists."""
#     nodeName = 'PlotWidget'
#     sigPlotChanged = QtCore.Signal(object)
#
#     def __init__(self, name):
#         Node.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
#         self.plot = None  # currently selected plot
#         self.plots = {}   # list of available plots user may select from
#         self.ui = None
#         self.items = {}
#
#     def disconnected(self, localTerm, remoteTerm):
#         if localTerm is self['In'] and remoteTerm in self.items:
#             self.plot.removeItem(self.items[remoteTerm])
#             del self.items[remoteTerm]
#
#     def setPlot(self, plot):
#         #print "======set plot"
#         if plot == self.plot:
#             return
#
#         # clear data from previous plot
#         if self.plot is not None:
#             for vid in list(self.items.keys()):
#                 self.plot.removeItem(self.items[vid])
#                 del self.items[vid]
#
#         self.plot = plot
#         self.updateUi()
#         self.update()
#         self.sigPlotChanged.emit(self)
#
#     def getPlot(self):
#         return self.plot
#
#     def _plot_pbs(self):
#         pass
#
#     def process(self, **kwargs):
#         In = kwargs['In']
#         self.plot.clear()
#         curves = []
#
#         # if kwargs['display'] and self.plot is not None:
#         if self.plot is not None:
#
#             for transmission in In.items():
#
#                 if len(transmission) < 2:
#                     continue
#
#                 transmission = transmission[1]
#                 src = transmission.src
#
#                 print('SOURCE IS: ' + str(src))
#
#                 if not isinstance(transmission, Transmission):
#                     continue
#                 df = transmission.df
#                 plot_this = transmission.plot_this
#
#                 if plot_this not in df:
#                     continue
#                 for data in df[plot_this]:
#                     if data is None:
#                         continue
#
#                     data = metaarray.MetaArray(data,
#                                                info=[{'name': 'Time',
#                                                       'values': np.linspace(0, len(data), len(data))}, {}])
#                     curves.append(data)
#
#             items = set()
#             for val in curves:
#                 vid = id(val)
#                 # print(id(val))
#                 if vid in self.items and self.items[vid].scene() is self.plot.scene():
#                     # Item is already added to the correct scene
#                     #   possible bug: what if two plots occupy the same scene? (should
#                     #   rarely be a problem because items are removed from a plot before
#                     #   switching).
#                     items.add(vid)
#                 else:
#                     # Add the item to the plot, or generate a new item if needed.
#                     if isinstance(val, QtGui.QGraphicsItem):
#                         self.plot.addItem(val)
#                         item = val
#                     else:
#                         # print('adding to plot')
#                         # print(val)
#                         item = self.plot.plot(val/val.min())
#                         # print('added')
#                     self.items[vid] = item
#                     items.add(vid)
#
#                 #
#                 # if 'Peaks' in kwargs:
#                 #     peaks_inputs = kwargs['Peaks']
#                 #     for peaks_transmission in peaks_inputs.items():
#                 #         peaks_transmission = peaks_transmission[1]
#                 #
#                 #         for peaks_bases in peaks_transmission.df[peaks_transmission.data_column]:
#                 #
#                 #             peaks_plot = ScatterPlotItem(name='peaks', pen=None, symbol='o', size=10,
#                 #                                          brush=(255, 0, 0, 150))
#                 #             bases_plot = ScatterPlotItem(name='bases', pen=None, symbol='o', size=10,
#                 #                                          brush=(0, 255, 0, 150))
#                 #
#                 #             peaks_plot.setData(peaks_bases[0].index
#                 #
#                 #             self.plot.addItem(peaks_plot)
#                 #             self.plot.addItem(bases_plot)
#
#         # Any left-over items that did not appear in the input must be removed
#         for vid in list(self.items.keys()):
#             if vid not in items:
#                 self.plot.removeItem(self.items[vid])
#                 del self.items[vid]
#
#     def processBypassed(self, args):
#         if self.plot is None:
#             return
#         for item in list(self.items.values()):
#             self.plot.removeItem(item)
#         self.items = {}
#
#     def ctrlWidget(self):
#         if self.ui is None:
#             self.ui = ComboBox()
#             self.ui.currentIndexChanged.connect(self.plotSelected)
#             self.updateUi()
#         return self.ui
#
#     def plotSelected(self, index):
#         self.setPlot(self.ui.value())
#
#     def setPlotList(self, plots):
#         """
#         Specify the set of plots (PlotWidget or PlotItem) that the user may
#         select from.
#
#         *plots* must be a dictionary of {name: plot} pairs.
#         """
#         self.plots = plots
#         self.updateUi()
#
#     def updateUi(self):
#         # sets list and automatically preserves previous selection
#         self.ui.setItems(self.plots)
#         try:
#             self.ui.setValue(self.plot)
#         except ValueError:
#             pass
#
#
# class CanvasNode(Node):
#     """Connection to a Canvas widget."""
#     nodeName = 'CanvasWidget'
#
#     def __init__(self, name):
#         Node.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
#         self.canvas = None
#         self.items = {}
#
#     def disconnected(self, localTerm, remoteTerm):
#         if localTerm is self.In and remoteTerm in self.items:
#             self.canvas.removeItem(self.items[remoteTerm])
#             del self.items[remoteTerm]
#
#     def setCanvas(self, canvas):
#         self.canvas = canvas
#
#     def getCanvas(self):
#         return self.canvas
#
#     def process(self, In, display=True):
#         if display:
#             items = set()
#             for name, vals in In.items():
#                 if vals is None:
#                     continue
#                 if type(vals) is not list:
#                     vals = [vals]
#
#                 for val in vals:
#                     vid = id(val)
#                     if vid in self.items:
#                         items.add(vid)
#                     else:
#                         self.canvas.addItem(val)
#                         item = val
#                         self.items[vid] = item
#                         items.add(vid)
#             for vid in list(self.items.keys()):
#                 if vid not in items:
#                     #print "remove", self.items[vid]
#                     self.canvas.removeItem(self.items[vid])
#                     del self.items[vid]
#
#
# class PlotCurve(CtrlNode):
#     """Generates a plot curve from x/y data"""
#     nodeName = 'PlotCurve'
#     uiTemplate = [
#         ('color', 'color'),
#     ]
#
#     def __init__(self, name):
#         CtrlNode.__init__(self, name, terminals={
#             'x': {'io': 'in'},
#             'y': {'io': 'in'},
#             'plot': {'io': 'out'}
#         })
#         self.item = PlotDataItem()
#
#     def process(self, x, y, display=True):
#         #print "scatterplot process"
#         if not display:
#             return {'plot': None}
#
#         self.item.setData(x, y, pen=self.ctrls['color'].color())
#         return {'plot': self.item}
#
#
#
#
# class ScatterPlot(CtrlNode):
#     """Generates a scatter plot from a record array or nested dicts"""
#     nodeName = 'ScatterPlot'
#     uiTemplate = [
#         ('x', 'combo', {'values': [], 'index': 0}),
#         ('y', 'combo', {'values': [], 'index': 0}),
#         ('sizeEnabled', 'check', {'value': False}),
#         ('size', 'combo', {'values': [], 'index': 0}),
#         ('absoluteSize', 'check', {'value': False}),
#         ('colorEnabled', 'check', {'value': False}),
#         ('color', 'colormap', {}),
#         ('borderEnabled', 'check', {'value': False}),
#         ('border', 'colormap', {}),
#     ]
#
#     def __init__(self, name):
#         CtrlNode.__init__(self, name, terminals={
#             'input': {'io': 'in'},
#             'plot': {'io': 'out'}
#         })
#         self.item = ScatterPlotItem()
#         self.keys = []
#
#         #self.ui = QtGui.QWidget()
#         #self.layout = QtGui.QGridLayout()
#         #self.ui.setLayout(self.layout)
#
#         #self.xCombo = QtGui.QComboBox()
#         #self.yCombo = QtGui.QComboBox()
#
#
#
#     def process(self, input, display=True):
#         #print "scatterplot process"
#         if not display:
#             return {'plot': None}
#
#         self.updateKeys(input[0])
#
#         x = str(self.ctrls['x'].currentText())
#         y = str(self.ctrls['y'].currentText())
#         size = str(self.ctrls['size'].currentText())
#         pen = QtGui.QPen(QtGui.QColor(0,0,0,0))
#         points = []
#         for i in input:
#             pt = {'pos': (i[x], i[y])}
#             if self.ctrls['sizeEnabled'].isChecked():
#                 pt['size'] = i[size]
#             if self.ctrls['borderEnabled'].isChecked():
#                 pt['pen'] = QtGui.QPen(self.ctrls['border'].getColor(i))
#             else:
#                 pt['pen'] = pen
#             if self.ctrls['colorEnabled'].isChecked():
#                 pt['brush'] = QtGui.QBrush(self.ctrls['color'].getColor(i))
#             points.append(pt)
#         self.item.setPxMode(not self.ctrls['absoluteSize'].isChecked())
#
#         self.item.setPoints(points)
#
#         return {'plot': self.item}
#
#
#
#     def updateKeys(self, data):
#         if isinstance(data, dict):
#             keys = list(data.keys())
#         elif isinstance(data, list) or isinstance(data, tuple):
#             keys = data
#         elif isinstance(data, np.ndarray) or isinstance(data, np.void):
#             keys = data.dtype.names
#         else:
#             print("Unknown data type:", type(data), data)
#             return
#
#         for c in self.ctrls.values():
#             c.blockSignals(True)
#         for c in [self.ctrls['x'], self.ctrls['y'], self.ctrls['size']]:
#             cur = str(c.currentText())
#             c.clear()
#             for k in keys:
#                 c.addItem(k)
#                 if k == cur:
#                     c.setCurrentIndex(c.count()-1)
#         for c in [self.ctrls['color'], self.ctrls['border']]:
#             c.setArgList(keys)
#         for c in self.ctrls.values():
#             c.blockSignals(False)
#
#         self.keys = keys
#
#
#     def saveState(self):
#         state = CtrlNode.saveState(self)
#         return {'keys': self.keys, 'ctrls': state}
#
#     def restoreState(self, state):
#         self.updateKeys(state['keys'])
#         CtrlNode.restoreState(self, state['ctrls'])
#
# #class ImageItem(Node):
#     #"""Creates an ImageItem for display in a canvas from a file handle."""
#     #nodeName = 'Image'
#
#     #def __init__(self, name):
#         #Node.__init__(self, name, terminals={
#             #'file': {'io': 'in'},
#             #'image': {'io': 'out'}
#         #})
#         #self.imageItem = graphicsItems.ImageItem()
#         #self.handle = None
#
#     #def process(self, file, display=True):
#         #if not display:
#             #return {'image': None}
#
#         #if file != self.handle:
#             #self.handle = file
#             #data = file.read()
#             #self.imageItem.updateImage(data)
#
#         #pos = file.
#
#
#
