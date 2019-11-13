# -*- coding: utf-8 -*-
from ... import PlotDataItem, ComboBox
from ....analysis import simple_plot_window
from .common import *
import numpy as np
import pandas as pd
from ....plotting.widgets import HeatmapTracerWidget, ScatterPlotWidget, \
    BeeswarmPlotWindow, ProportionsWidget, CrossCorrelationWidget, SpaceMapWidget
from ....plotting.variants.timeseries import TimeseriesPlot
from graphviz import Digraph
from ....common.utils import make_workdir
import os
import subprocess
from random import randrange


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
        self.plot_widget = simple_plot_window.PlotWindow()
        self.ctrls['Apply'].clicked.connect(self.update)
        self.ctrls['Show'].clicked.connect(self.plot_widget.setVisible)

    def process(self, **kwargs):
        transmissions = kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        transmissions = merge_transmissions(transmissions)

        columns = pd.concat([t.df for t in transmissions]).columns
        dcols = organize_dataframe_columns(columns)[0]
        self.ctrls['data_column'].setItems(dcols)

        if self.ctrls['Apply'].isChecked() is False:
            return
        data_column = self.ctrls['data_column'].currentText()
        self.plot_widget.graphicsView.clear()

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

                self.plot_widget.graphicsView.addItem(plot)

            ci += 1

        self.plot_widget.set_history_widget(srcs)


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
        self.plot_widget = TimeseriesPlot()
        self.ctrls['Show'].clicked.connect(self.plot_widget.show)

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

        self.plot_widget.set(data=data, err_style=es)


class Heatmap(CtrlNode):
    """Stack 1-D arrays and plot visually like a heatmap"""
    nodeName = "Heatmap"
    uiTemplate = [('Show', 'button', {'text': 'Show GUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})#, 'Out': {'io': 'out'}})
        self.plot_widget = HeatmapTracerWidget()
        self.ctrls['Show'].clicked.connect(self.plot_widget.show)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)
        if len(self.transmissions_list) == 1:
            self.t = self.transmissions_list[0]
        else:
            self.t = Transmission.merge(self.transmissions_list)

        self.plot_widget.set_input(self.t)


class ScatterPlot(CtrlNode):
    """Scatter Plot, useful for visualizing transformed data and clusters"""
    nodeName = "ScatterPlot"
    uiTemplate = [('Show', 'button', {'text': 'Show'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_widget = ScatterPlotWidget()
        self.ctrls['Show'].clicked.connect(self.plot_widget.show)

    def process(self, **kwargs):
        transmissions = kwargs['In']

        tran_list = merge_transmissions(transmissions)
        merged = Transmission.merge(tran_list)

        self.plot_widget.set_input(merged)


class BeeswarmPlots(CtrlNode):
    """Beeswarm and Violin plots"""
    nodeName = 'BeeswarmPlots'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_widget = None
        self.ctrls['ShowGUI'].clicked.connect(self._open_plot_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_widget is None:
            return

        transmissions = kwargs['In']
        transmissions_list = merge_transmissions(transmissions)

        self.plot_widget.update_input_transmissions(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_widget is None:
            self.plot_widget = BeeswarmPlotWindow(parent=None)
        self.plot_widget.show()


class Proportions(CtrlNode):
    """Plot proportions of one categorical column vs another"""
    nodeName = 'Proportions'
    uiTemplate = [('show gui', 'button', {'text': 'Show Gui'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_widget = ProportionsWidget()
        self.ctrls['show gui'].clicked.connect(self.plot_widget.show)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        self.plot_widget.set_input(self.t)


class CrossCorr(CtrlNode):
    """Cross Correlation"""
    nodeName = 'CrossCorr'
    uiTemplate = [('ShowGUI', 'button', {'text': 'Show Gui'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_widget = CrossCorrelationWidget()
        self.ctrls['ShowGUI'].clicked.connect(self.plot_widget.show)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        self.plot_widget.set_input(self.t)


class SpaceMap(CtrlNode):
    """Visualize spatial maps of a categorical variable"""
    nodeName = 'SpaceMap'
    uiTemplate = [('ShowGUI', 'button', {'text': 'Show GUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_widget =SpaceMapWidget()
        self.ctrls['ShowGUI'].clicked.connect(self.plot_widget.show)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions)

        self.plot_widget.set_input(self.t)


class AnalysisGraph(CtrlNode):
    """Graph of the analysis log"""
    nodeName = 'AnalysisGraph'
    uiTemplate = [('data_blocks', 'list_widget', {'toolTip': 'Double click a data block to open the pdf'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.ctrls['data_blocks'].itemDoubleClicked.connect(self.open_file)

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        workdir = make_workdir(f'analysis_graphs{randrange(1000, 9999)}')

        self.fnames = []

        for db in self.t.history_trace.data_blocks:
            fname = os.path.join(workdir, f"{db}")
            g = Digraph('G', filename=fname, format='pdf', node_attr={'shape': 'record'})

            db_history = self.t.history_trace.get_data_block_history(db)

            o_encounters = []
            o_n_l = []

            for op in db_history:
                o = list(op.keys())[0]
                params = op[o]
                params = cleanup_params(o, params)
                s = []
                for k in params.keys():
                    p = str(params[k]).replace("{", "\\n   --\> ").replace("}", "").replace("|", "\|")  # .replace("[", " ").replace("(", " ").replace(")", " ")
                    s.append(f"{k}: {p}")

                o_n = f"{o}.{o_encounters.count(o)}"
                o_n_l.append(o_n)
                s = '{ ' + o_n + ' | ' + '\\n'.join(s) + ' }'

                g.node(o_n, s)
                o_encounters.append(o)

            es = []
            for i in range(1, len(o_n_l)):
                es.append((o_n_l[i - 1], o_n_l[i]))

            g.edges(es)
            g.render(view=False)

            self.fnames.append(fname + '.pdf')

        self.ctrls['data_blocks'].setItems(list(map(str, range(len(self.fnames)))))

    def open_file(self, item):
        ix = self.ctrls['data_blocks'].currentRow()
        subprocess.call(["xdg-open", self.fnames[ix]])


def cleanup_params(operation, params):
    log = params.copy()
    if operation == 'rfft':
        log.pop('frequencies')
    elif operation =='fcluster':
        log.pop('linkage_matrix')

    return log

