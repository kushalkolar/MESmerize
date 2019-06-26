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
from typing import Union
import pandas as pd
from matplotlib import gridspec
from functools import partial


class CustomClusterGrid(ClusterGrid):
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
    # signal_row_selection_changed = QtCore.pyqtSignal(tuple)
    sig_selection_changed = QtCore.pyqtSignal(tuple)

    def __init__(self, highlight_mode='row'):
        # QtCore.QObject.__init__(self)
        MatplotlibWidget.__init__(self)
        rcParams['image.interpolation'] = None
        # self.ax_heatmap_ = self.fig.add_subplot(111)
        # self.ax_heatmap_.get_yaxis().set_visible(False)

        # [[x1, y1], [x2, y2]] = self.ax_heatmap_.get_position().get_points()
        # bb = Bbox.from_extents([[0.1, y1], [0.11, y2]])
        # self.ax_ylabel_bar = self.fig.add_axes(bb.bounds)

        # self.fig.subplots_adjust(right=0.8)
        # self.cbar_ax = self.fig.add_axes([0.85, 0.15, 0.05, 0.7])
        self.data = None

        self.selector = Selection()
        self.selector.sig_selection_changed.connect(self.sig_selection_changed.emit)


        self.stimulus_indicators = []
        self.highlight_mode = highlight_mode

        self.plot = None

        self.cid_heatmap = None
        self.cid_ax_row_colors = None
        self.cid_ax_row_dendrogram = None

        self._previous_ylims = None
        self.max_ylim = None
        self.min_ylim = None
        self.xlims = None

    def set(self, data: np.ndarray, *args, ylabels: iter = None, ylabels_cmap: str = 'tab20', cluster_kwargs = None,
            **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        # self.ax_heatmap_.cla()
        # self._highlight = None
        # self.cbar_ax.cla()
        self.data = data

        cluster_kwarg_keys = ['row_cluster', 'row_linkage', 'col_cluster', 'col_linkage', 'colorbar_kws', 'metric', 'method']

        if cluster_kwargs is None:
            cluster_kwargs = dict.fromkeys(cluster_kwarg_keys)
        else:
            for key in cluster_kwarg_keys:
                if key not in cluster_kwargs.keys():
                    cluster_kwargs[key] = None

        # labels = kwargs.pop('ylabels')
        # ylabels_cmap = kwargs.pop('ylabels_cmap')

        # self.plot = seaborn_heatmap(data, *args, ax=self.ax_heatmap_, cbar_ax=self.cbar_ax, **kwargs)

        if isinstance(ylabels, Series):
            ylabels = ylabels.values

        if ylabels is not None:
            mapper = get_colormap(ylabels, ylabels_cmap)
            row_colors = list(map(mapper.get, ylabels))

        else:
            row_colors = None

        if self.fig is not None:
            self.fig.clear()
        # self.plot = sns_clustermap(*args, data=data, row_colors=row_colors, row_cluster=None, col_cluster=None, **cluster_kwargs, **kwargs)
        self.plot = CustomClusterGrid(data=data, fig=self.fig, figsize=None, row_colors=row_colors, col_colors=None,
                                      z_score=None, standard_scale=None, mask=None)
        self.plot.plot(*args, **cluster_kwargs, **kwargs)

        if ylabels is not None:
            self.create_ylabels_legend(mapper)

        # self.ax_heatmap_xlim = self.plot.ax_heatmap.get_xlim()

        self._previous_ylims = self.plot.ax_heatmap.get_ylim()

        self.xlims = {self.plot.ax_heatmap: self.plot.ax_heatmap.get_xlim(),
                      self.plot.ax_row_colors: self.plot.ax_row_colors.get_xlim(),
                      self.plot.ax_row_dendrogram: self.plot.ax_row_dendrogram.get_xlim()
                      }

        self.max_ylim = self.plot.ax_heatmap.get_ylim()[0]
        self.min_ylim = self.plot.ax_heatmap.get_ylim()[1]

        self.draw()
        # self.toolbar._views.clear()
        # self.toolbar._positions.clear()
        self.toolbar.update()
        # self.toolbar._update_view()

        self._connect_ylim_callbacks()
        self._connect_xlim_callbacks()

        self.selector.set(self, mode=self.highlight_mode)
        # if isinstance(self.selector, Selection):
        #     self.selector.sig_selection_changed.disconnect(self.sig_selection_changed.emit)
        #     del self.selector

        # self.selector = Selection(self, mode=self.highlight_mode)

        # if ylabels is not None:
        #     self._set_ylabel_bar(ylabels, cmap=ylabels_cmap)

    def _connect_xlim_callbacks(self):
        self.xcid_heatmap = self.plot.ax_heatmap.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.xcid_ax_row_colors = self.plot.ax_row_colors.callbacks.connect('xlim_changed', self.on_xlim_changed)
        self.xcid_ax_row_dendrogram = self.plot.ax_row_dendrogram.callbacks.connect('xlim_changed', self.on_xlim_changed)

    def _disconnect_xlim_callbacks(self):
        self.plot.ax_heatmap.callbacks.disconnect(self.xcid_heatmap)
        self.plot.ax_row_colors.callbacks.disconnect(self.xcid_ax_row_colors)
        self.plot.ax_row_dendrogram.callbacks.disconnect(self.xcid_ax_row_dendrogram)

    def on_xlim_changed(self, ax):
        """Reset the x limits"""
        self._disconnect_xlim_callbacks()
        ax.set_xlim(self.xlims[ax])
        self._connect_xlim_callbacks()

    def _connect_ylim_callbacks(self):
        self.cid_heatmap = self.plot.ax_heatmap.callbacks.connect('ylim_changed', self.on_ylim_changed)
        self.cid_ax_row_colors = self.plot.ax_row_colors.callbacks.connect('ylim_changed', self.on_ylim_changed)
        self.cid_ax_row_dendrogram = self.plot.ax_row_dendrogram.callbacks.connect('ylim_changed', self.on_ylim_changed)

    def _disconnect_ylim_callbacks(self):
        self.plot.ax_heatmap.callbacks.disconnect(self.cid_heatmap)#, self.on_ylim_changed)
        self.plot.ax_row_colors.callbacks.disconnect(self.cid_ax_row_colors)#, self.on_ylim_changed)
        self.plot.ax_row_dendrogram.callbacks.disconnect(self.cid_ax_row_dendrogram)#, self.on_ylim_changed)

    def on_ylim_changed(self, ax):
        if ax is self.plot.ax_row_dendrogram:
            # divide by 10
            lims = tuple(map(lambda x: x / 10, ax.get_ylim()))
        else:
            lims = ax.get_ylim()

        if lims[0] > self.max_ylim or lims[1] < self.min_ylim:
            self.y_lims_exceeded()
            return

        self._disconnect_ylim_callbacks()

        if ax is not self.plot.ax_heatmap:
            self.plot.ax_heatmap.set_ylim(lims)

        if ax is not self.plot.ax_row_colors:
            self.plot.ax_row_colors.set_ylim(lims)

        if ax is not self.plot.ax_row_dendrogram:
            # scale up by 10 for this ax
            lims_ = tuple(map(lambda x: x * 10, lims))
            self.plot.ax_row_dendrogram.set_ylim(lims_)

        self._previous_ylims = lims

        self._connect_ylim_callbacks()

    def y_lims_exceeded(self):
        # if lims[0] > self.max_ylim:
        #     upper = self.max_ylim
        # else:
        #     upper = lims[0]
        #
        # if lims[1] < self.min_ylim:
        #     lower = self.min_ylim
        # else:
        #     lower = lims[1]

        lims = self._previous_ylims

        self._disconnect_ylim_callbacks()

        self.plot.ax_heatmap.set_ylim(lims)
        self.plot.ax_row_colors.set_ylim(lims)
        self.plot.ax_row_dendrogram.set_ylim(tuple(map(lambda x: x*10, lims)))

        self._connect_ylim_callbacks()

    def create_ylabels_legend(self, ylabels_mapper):
        self.plot.ax_col_dendrogram.cla()
        handles = [MPatch(color=ylabels_mapper[k], label=k) for k in ylabels_mapper.keys()]
        self.plot.ax_col_dendrogram.legend(handles=handles, ncol=int(np.sqrt(len(handles))))
        self.plot.ax_col_dendrogram.get_xaxis().set_visible(False)
        self.plot.ax_col_dendrogram.get_yaxis().set_visible(False)

    # def _set_ylabel_bar(self, labels : Series, cmap: str = 'tab20'):
    #     assert isinstance(labels, Series)
    #
    #     self.ax_ylabel_bar.cla()
    #
    #     [[x1, y1], [x2, y2]] = self.ax_heatmap_.get_position().get_points()
    #     bb = Bbox.from_extents([[0.123, y1], [0.11, y2]])
    #     self.ax_ylabel_bar.set_position(bb)
    #
    #     # self.ax_ylabel_bar.get_xaxis().set_visible(False)s
    #     # self.ax_ylabel_bar.get_yaxis().set_visible(False)
    #     self.ax_ylabel_bar.axis('off')
    #
    #     labels_unique = labels.unique()
    #     colors_map = {}
    #
    #     for ix, c in enumerate(labels_unique):
    #         colors_map.update({labels_unique[ix]: ix})
    #
    #     colors = labels.map(colors_map)
    #     color_labels_array = np.expand_dims(colors.values, axis=1)
    #
    #     ylabel_bar = self.ax_ylabel_bar.imshow(color_labels_array, aspect='auto', cmap=cmap)
    #
    #     cs = np.unique(color_labels_array.ravel())
    #     colors = [ylabel_bar.cmap(ylabel_bar.norm(c)) for c in cs]
    #     ps = [MPatch(color=colors[i], label=labels_unique[i]) for i in range(len(cs))]
    #     self.ax_ylabel_bar.legend(handles=ps, bbox_to_anchor=(1,1))

    def add_stimulus_indicator(self, start: int, end: int, color: str):
        for t in [start, end]:
            x = np.array([t, t])
            y = np.array([0, self.data.shape[0]])
            line = Line2D(x, y, lw=3, color=color)
            self.stimulus_indicators.append(line)
            self.plot.add_line(line)


class Selection(QtCore.QObject):
    sig_selection_changed = QtCore.pyqtSignal(tuple)
    sig_multi_selection_changed = QtCore.pyqtSignal(list)

    def __init__(self): #, heatmap_obj, mode: str = 'row'):
        QtCore.QObject.__init__(self)
        self.canvas = None #heatmap_obj.canvas
        self.plot = None #heatmap_obj.plot
        self.heatmap = None #heatmap_obj

        self.mode = None #mode
        # if mode == 'row':
        #     self.canvas.mpl_connect('button_press_event', self.select_row)
        # elif mode == 'item':
        #     rp = dict(facecolor='w', edgecolor='k', lw=1, alpha=0.5)
        #     self.RS = RectangleSelector(self.heatmap.plot, self.line_select_callback,
        #                                drawtype='box', useblit=True,
        #                                button=[1, 3],  # don't use middle button
        #                                minspanx=1, minspany=1,
        #                                spancoords='data',
        #                                interactive=True, rectprops=rp)
        #     self.RS.set_active(True)
        self.RS = None
        self.current_ix = None
        self._highlight = None
        self._start_ixs = None
        self.multi_select_mode = False

        self._multiselect = False
        self.multi_selection_list = list()

    def set(self, heatmap_obj, mode: str = 'row'):
        self._highlight = None
        self.current_ix = None

        self.canvas = heatmap_obj.plot.fig.canvas
        self.plot = heatmap_obj.plot.ax_heatmap
        self.heatmap = heatmap_obj

        self.mode = mode

        if mode == 'row':
            self.canvas.mpl_connect('button_press_event', self.select_row)
        elif mode == 'item':
            self.canvas.mpl_connect('button_press_event', self.select_item)
            self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.canvas.setFocus()
            self.canvas.mpl_connect('key_press_event', self.set_multi_select_mode_on)
            self.canvas.mpl_connect('key_release_event', self.set_multi_select_mode_off)
        # elif mode == 'span':
        #     rp = dict(facecolor='w', edgecolor='k', lw=1, alpha=0.5)
        #     self.RS = RectangleSelector(self.heatmap.plot, self.line_select_callback,
        #                                 drawtype='box', useblit=True,
        #                                 button=[1, 3],  # don't use middle button
        #                                 minspanx=1, minspany=1,
        #                                 spancoords='data',
        #                                 interactive=True, rectprops=rp)
        #     self.RS.set_active(True)
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
                                                               facecolor='w', edgecolor='k', lw=3, alpha=0.5))
        self.canvas.draw()

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
        self._highlight = self.plot.add_patch(RectangularPatch(ix, 1, 1, facecolor='w', edgecolor='k', lw=3, alpha=0.5))
        self.canvas.draw()

    def toggle_selector(self, event):
        if event.key in ['Q', 'q'] and self.RS.active:
            print('RectangleSelector deactivated.')
            self.RS.set_active(False)
        if event.key in ['A', 'a'] and not self.RS.active:
            print('RectangleSelector activated.')
            self.RS.set_active(True)
    
    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        self.signal_selection_changed.emit((x1, y1, x2, y2))
        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
        print(" The button you used were: %s %s" % (eclick.button, erelease.button))
            

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
