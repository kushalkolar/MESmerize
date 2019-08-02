#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from PyQt5 import QtCore, QtWidgets
from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np
# from seaborn import clustermap as sns_clustermap
from seaborn.matrix import ClusterGrid, _matrix_mask
from matplotlib.patches import Rectangle as RectangularPatch
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.patches import Patch as MPatch
from matplotlib import rcParams
from matplotlib import pyplot as plt
from matplotlib.widgets import RectangleSelector
from pandas import Series
from ..utils import get_colormap, map_labels_to_colors
from typing import *
import pandas as pd
from matplotlib import gridspec
from functools import partial


class CustomClusterGrid(ClusterGrid):
    """Slightly modified from Seaborn ClusterGrid so that an existing figure instance can be used"""
    def __init__(self, data, fig, pivot_kws=None, z_score=None, standard_scale=None,
                 figsize=None, row_colors=None, col_colors=None, mask=None):
        """Grid object for organizing clustered heatmap input on to axes"""

        if isinstance(data, pd.DataFrame):
            self.data = data
        else:
            self.data = pd.DataFrame(data)

        self.data2d = self.format_data(self.data, pivot_kws, z_score,
                                       standard_scale)

        self.mask = _matrix_mask(self.data2d, mask)

        if figsize is None:
            width, height = 10, 10
            figsize = (width, height)
        if fig is None:
            self.fig = plt.figure(figsize=figsize)
        else:
            self.fig = fig

        self.row_colors, self.row_color_labels = \
            self._preprocess_colors(data, row_colors, axis=0)
        self.col_colors, self.col_color_labels = \
            self._preprocess_colors(data, col_colors, axis=1)

        width_ratios = self.dim_ratios(self.row_colors,
                                       figsize=figsize,
                                       axis=1)

        height_ratios = self.dim_ratios(self.col_colors,
                                        figsize=figsize,
                                        axis=0)
        nrows = 3 if self.col_colors is None else 4
        ncols = 3 if self.row_colors is None else 4

        self.gs = gridspec.GridSpec(nrows, ncols, wspace=0.01, hspace=0.01,
                                    width_ratios=width_ratios,
                                    height_ratios=height_ratios)

        self.ax_row_dendrogram = self.fig.add_subplot(self.gs[nrows - 1, 0:2])
        self.ax_col_dendrogram = self.fig.add_subplot(self.gs[0:2, ncols - 1])
        self.ax_row_dendrogram.set_axis_off()
        self.ax_col_dendrogram.set_axis_off()

        self.ax_row_colors = None
        self.ax_col_colors = None

        if self.row_colors is not None:
            self.ax_row_colors = self.fig.add_subplot(
                self.gs[nrows - 1, ncols - 2])
        if self.col_colors is not None:
            self.ax_col_colors = self.fig.add_subplot(
                self.gs[nrows - 2, ncols - 1])

        self.ax_heatmap = self.fig.add_subplot(self.gs[nrows - 1, ncols - 1])

        # colorbar for scale to left corner
        self.cax = self.fig.add_subplot(self.gs[0, 0])

        self.dendrogram_row = None
        self.dendrogram_col = None


class Heatmap(MatplotlibWidget):
    """Heatmap plot variant"""
    sig_selection_changed = QtCore.pyqtSignal(tuple)  #: Emits indices of data coordinates (x, y) from mouse-click events on the heatmap

    def __init__(self, highlight_mode='row'):
        """

        :param highlight_mode: The selection mode for the heatmap. One of either 'row' or 'item'
        """
        MatplotlibWidget.__init__(self)
        rcParams['image.interpolation'] = None

        self.data = None  #: 2D numpy array of the heatmap data

        self.selector = Selection()  #: Selection instance that organizes mouse click events on the heatmap
        self.selector.sig_selection_changed.connect(self.sig_selection_changed.emit)
        self.selector.sig_selection_changed.connect(self.scroll_selector)

        self.stimulus_indicators = []
        self.highlight_mode = highlight_mode  #: selection mode, either 'row' or 'item

        self.plot = None  #: ClusterGrid object instance containing the plot Axes

        self.cid_heatmap = None
        self.cid_ax_row_colors = None
        self.cid_ax_row_dendrogram = None

        self.xcid_heatmap = None
        self.xcid_ax_row_colors = None
        self.xcid_ax_row_dendrogram = None

        self._previous_ylims = None
        self.max_ylim = None
        self.min_ylim = None
        self.xlims = None

    def set(self, data: np.ndarray, *args, ylabels: Union[Series, np.ndarray, list] = None, ylabels_cmap: str = 'tab20',
            cluster_kwargs: dict = None, **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param ylabels: Labels used to create the ylabels bar
        :param ylabels_cmap: colormap for the ylabels bar
        :param cluster_kwargs: keywoard arguments for visualizing hierarchical clustering
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.data = data

        if isinstance(ylabels, Series):
            ylabels = ylabels.values
        if ylabels is not None:
            mapper = get_colormap(ylabels, ylabels_cmap)
            row_colors = list(map(mapper.get, ylabels))
        else:
            row_colors = None

        if 'xlabels' in kwargs.keys():
            xlabels = kwargs.pop('xlabels')

            if isinstance(xlabels, Series):
                xlabels = xlabels.values

            xlabels_mapper = get_colormap(xlabels, ylabels_cmap)
            col_colors = list(map(xlabels_mapper.get, xlabels))
        else:
            col_colors = None

        cluster_kwarg_keys = ['row_cluster', 'row_linkage', 'col_cluster', 'col_linkage', 'colorbar_kws', 'metric', 'method']

        if cluster_kwargs is None:
            cluster_kwargs = dict.fromkeys(cluster_kwarg_keys)
            self.cluster_color_mapper = None
        else:
            if 'cluster_labels' in cluster_kwargs.keys():
                cluster_labels = cluster_kwargs.pop('cluster_labels')

                self.cluster_color_mapper = get_colormap(cluster_labels, cmap='tab10')
                clus_colors = list(map(self.cluster_color_mapper.get, cluster_labels))

                row_colors = [clus_colors, row_colors]
            else:
                self.cluster_color_mapper = None

            for key in cluster_kwarg_keys:
                if key not in cluster_kwargs.keys():
                    cluster_kwargs[key] = None

        if self.fig is not None:
            self.fig.clear()

        self.plot = CustomClusterGrid(data=data, fig=self.fig, figsize=None, row_colors=row_colors, col_colors=col_colors,
                                      z_score=None, standard_scale=None, mask=None)
        self.plot.plot(*args, **cluster_kwargs, **kwargs)

        if ylabels is not None:
            self.create_ylabels_legend(mapper, self.cluster_color_mapper)

        self._previous_ylims = self.plot.ax_heatmap.get_ylim()

        self.xlims = {self.plot.ax_heatmap: self.plot.ax_heatmap.get_xlim(),
                      self.plot.ax_row_colors: self.plot.ax_row_colors.get_xlim(),
                      self.plot.ax_row_dendrogram: self.plot.ax_row_dendrogram.get_xlim()
                      }

        self.max_ylim = self.plot.ax_heatmap.get_ylim()[0]
        self.min_ylim = self.plot.ax_heatmap.get_ylim()[1]

        self.draw()
        self.toolbar.update()

        self.connect_ylim_callbacks()
        self.connect_xlim_callbacks()

        self.selector.set(self, mode=self.highlight_mode)
        # if isinstance(self.selector, Selection):
        #     self.selector.sig_selection_changed.disconnect(self.sig_selection_changed.emit)
        #     del self.selector

        # self.selector = Selection(self, mode=self.highlight_mode)

    def block_callbacks(func):
        """Block callbacks, used when the plot x and y limits change due to user interaction"""
        def fn(self, *args, **kwargs):
            self.disconnect_xlim_callbacks()
            self.disconnect_ylim_callbacks()
            try:
                ret = func(self, *args, **kwargs)
            finally:
                self.connect_xlim_callbacks()
                self.connect_ylim_callbacks()
            return ret
        return fn

    def connect_xlim_callbacks(self):
        self.xcid_heatmap = self.plot.ax_heatmap.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.xcid_ax_row_colors = self.plot.ax_row_colors.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.xcid_ax_row_dendrogram = self.plot.ax_row_dendrogram.callbacks.connect('xlim_changed', self.on_xlim_changed)

    def disconnect_xlim_callbacks(self):
        self.plot.ax_heatmap.callbacks.disconnect(self.xcid_heatmap)
        self.plot.ax_row_colors.callbacks.disconnect(self.xcid_ax_row_colors)
        self.plot.ax_row_dendrogram.callbacks.disconnect(self.xcid_ax_row_dendrogram)

    def connect_ylim_callbacks(self):
        self.cid_heatmap = self.plot.ax_heatmap.callbacks.connect('ylim_changed', self.on_ylim_changed)
        self.cid_ax_row_colors = self.plot.ax_row_colors.callbacks.connect('ylim_changed', self.on_ylim_changed)
        self.cid_ax_row_dendrogram = self.plot.ax_row_dendrogram.callbacks.connect('ylim_changed', self.on_ylim_changed)

    def disconnect_ylim_callbacks(self):
        self.plot.ax_heatmap.callbacks.disconnect(self.cid_heatmap)
        self.plot.ax_row_colors.callbacks.disconnect(self.cid_ax_row_colors)
        self.plot.ax_row_dendrogram.callbacks.disconnect(self.cid_ax_row_dendrogram)

    @block_callbacks
    def on_xlim_changed(self, ax):
        """Reset the x limits"""
        ax.set_xlim(self.xlims[ax])

    @block_callbacks
    def on_ylim_changed(self, ax):
        if ax is self.plot.ax_row_dendrogram:
            # divide by 10
            lims = tuple(map(lambda x: x / 10, ax.get_ylim()))
        else:
            lims = ax.get_ylim()

        if lims[0] > self.max_ylim or lims[1] < self.min_ylim:
            self.y_lims_exceeded()
            return

        self.set_y_lims(lims, skip_axes=ax)


        self._previous_ylims = lims

    @block_callbacks
    def y_lims_exceeded(self):
        lims = self._previous_ylims
        self.plot.ax_heatmap.set_ylim(lims)
        self.plot.ax_row_colors.set_ylim(lims)
        self.plot.ax_row_dendrogram.set_ylim(tuple(map(lambda x: x*10, lims)))

    def create_ylabels_legend(self, ylabels_mapper, cluster_mapper):
        self.plot.ax_col_dendrogram.cla()
        handles = [MPatch(color=ylabels_mapper[k], label=k) for k in ylabels_mapper.keys()]

        if cluster_mapper is not None:
            handles = [MPatch(color=cluster_mapper[k], label=k) for k in cluster_mapper.keys()] + handles

        self.plot.ax_col_dendrogram.legend(handles=handles, ncol=int(np.sqrt(len(handles))))
        self.plot.ax_col_dendrogram.get_xaxis().set_visible(False)
        self.plot.ax_col_dendrogram.get_yaxis().set_visible(False)

    def add_stimulus_indicator(self, start: int, end: int, color: str):
        """
        Add lines to indicate the start and end of a stimulus or behavioral period

        :param start: start index
        :param end: end index
        :param color: line color
        """
        for t in [start, end]:
            x = np.array([t, t])
            y = np.array([0, self.data.shape[0]])
            line = Line2D(x, y, lw=3, color=color)
            self.stimulus_indicators.append(line)
            self.plot.add_line(line)

    def set_y_lims(self, lims: Tuple[int, int], skip_axes = None):
        if skip_axes is not self.plot.ax_heatmap:
            self.plot.ax_heatmap.set_ylim(lims)

        if skip_axes is not self.plot.ax_row_colors:
            self.plot.ax_row_colors.set_ylim(lims)

        if skip_axes is not self.plot.ax_row_dendrogram:
            # scale up by 10 for this ax
            lims_ = tuple(map(lambda x: x * 10, lims))
            self.plot.ax_row_dendrogram.set_ylim(lims_)

    def get_y_lims(self) -> Tuple[int, int]:
        if not self.plot.ax_heatmap.get_ylim() == self.plot.ax_row_colors.get_ylim():
            raise ValueError('Axes y_lims not in sync, something wrong')

        return self.plot.ax_heatmap.get_ylim()

    @QtCore.pyqtSlot(tuple)
    def scroll_selector(self, ixs: Tuple[int, int]):
        upper, lower = self.get_y_lims()
        if self.highlight_mode == 'row':
            if ixs[1] + 2 > upper:
                if ixs[1] + 2 > self.max_ylim:
                    return

                new_upper = min(ixs[1] + 10, self.max_ylim)
                new_lower = max(self.min_ylim, lower + 10)

            elif ixs[1] - 2 < lower:
                if ixs[1] - 2 < self.min_ylim:
                    return

                new_lower = max(self.min_ylim, ixs[1] - 10)
                new_upper = min(upper - 10, self.max_ylim)

            else:
                return

            lims = (new_upper, new_lower)

            self.set_y_lims(lims)


class Selection(QtCore.QObject):
    sig_selection_changed = QtCore.pyqtSignal(tuple)
    sig_multi_selection_changed = QtCore.pyqtSignal(list)

    def __init__(self): #, heatmap_obj, mode: str = 'row'):
        QtCore.QObject.__init__(self)
        self.canvas = None #heatmap_obj.canvas
        self.plot = None #heatmap_obj.plot
        self.heatmap = None #heatmap_obj

        self.RS = None
        self.current_ix = None
        self._highlight = None
        self._start_ixs = None
        self.multi_select_mode = False

        self._multiselect = False
        self.multi_selection_list = list()
        self.mode = None

    def set(self, heatmap_obj, mode: str = 'row'):
        self._highlight = None
        self.current_ix = None

        self.canvas = heatmap_obj.plot.fig.canvas
        self.plot = heatmap_obj.plot.ax_heatmap
        self.heatmap = heatmap_obj

        self.mode = mode

        if mode == 'row':
            self.canvas.mpl_connect('button_press_event', self.select_row)
            self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.canvas.setFocus()
            self.canvas.mpl_connect('key_press_event', self.on_key_press_event)

        elif mode == 'item':
            self.canvas.mpl_connect('button_press_event', self.select_item)
            self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.canvas.setFocus()
            self.canvas.mpl_connect('key_press_event', self.set_multi_select_mode_on)
            self.canvas.mpl_connect('key_release_event', self.set_multi_select_mode_off)
        else:
            raise ValueError("Invalid selection mode: '" + str(mode) + "' Valid modes are: 'row', 'item' or 'span'.")

    def _clear_highlight(self):
        if self._highlight is not None:
            self._highlight.remove()
        self._highlight = None

    def update_selection(self, ix: tuple):
        if not self.multi_select_mode:
            self._clear_highlight()
            self.multi_selection_list.clear()

        self.current_ix = ix
        self.sig_selection_changed.emit(self.current_ix)

        if self.multi_select_mode:
            self.multi_selection_list.append(ix)
            self.sig_multi_selection_changed.emit(self.multi_selection_list)

    def select_row(self, ev):
        if type(ev) is int:
            y = ev
        else:
            if ev.button == 3:
                self._clear_highlight()
                self.canvas.draw()
                return

            y = ev.ydata

            if y is None:
                return

            y = int(y)

        ix = (0, y)
        self.update_selection(ix)
        self._draw_row_selection(y)

    def _draw_row_selection(self, y):
        self._highlight = self.plot.add_patch(RectangularPatch((0, y), self.heatmap.data.shape[1], 1,
                                                               facecolor='w', edgecolor='k', lw=3, alpha=0.2))
        self.canvas.draw()

    def on_key_press_event(self, ev):
        if ev.key == 'up':
            ixs = max(self.current_ix[1] - 1, self.heatmap.min_ylim)

        elif ev.key == 'down':
            ixs = min(self.current_ix[1] + 1, self.heatmap.max_ylim)

        else:

            return
        # elif ev.key == 'left':
        #     pass
        # elif ev.key == 'right':
        #     pass

        self.select_row(int(ixs))

    def set_multi_select_mode_on(self, ev):
        if ev.key == 'control':
            self.multi_select_mode = True

    def set_multi_select_mode_off(self, ev):
        if ev.key == 'control':
            self.multi_select_mode = False

    def select_item(self, ev):
        if type(ev) is not tuple:
            ix = (int(ev.xdata), int(ev.ydata))

            self.update_selection(ix)
            self._draw_item_selection(ix)

    def _draw_item_selection(self, ix: tuple):
        self._highlight = self.plot.add_patch(RectangularPatch(ix, 1, 1, facecolor='w', edgecolor='k', lw=3, alpha=0.2))
        self.canvas.draw()

    # def toggle_selector(self, event):
    #     if event.key in ['Q', 'q'] and self.RS.active:
    #         print('RectangleSelector deactivated.')
    #         self.RS.set_active(False)
    #     if event.key in ['A', 'a'] and not self.RS.active:
    #         print('RectangleSelector activated.')
    #         self.RS.set_active(True)

    # def line_select_callback(self, eclick, erelease):
    #     'eclick and erelease are the press and release events'
    #     x1, y1 = int(eclick.xdata), int(eclick.ydata)
    #     x2, y2 = int(erelease.xdata), int(erelease.ydata)
    #     self.signal_selection_changed.emit((x1, y1, x2, y2))
    #     print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    #     print(" The button you used were: %s %s" % (eclick.button, erelease.button))
            

if __name__ == '__main__':
    import pickle
    from sklearn.metrics import pairwise_distances
    t = pickle.load(open('/home/kushal/Sars_stuff/mesmerize_toy_datasets/cesa_hnk1_raw_data.trn', 'rb'))
    df = t['df']
    
    data = np.vstack(df._RAW_CURVE.apply(lambda x: x[:2998]).values)
    
    dists = pairwise_distances(data)
    
    app = QtWidgets.QApplication([])
    w = Heatmap(highlight_mode='item')
    w.set(dists, cmap='jet', ylabels=df.promoter)
    
    w.show()
    app.exec_()
