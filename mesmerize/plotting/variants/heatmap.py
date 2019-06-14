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
from seaborn import heatmap as seaborn_heatmap
from matplotlib.patches import Rectangle as RectangularPatch
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from matplotlib.patches import Patch as MPatch
from matplotlib import rcParams
from matplotlib.widgets import RectangleSelector
from pandas import Series


class Heatmap(MatplotlibWidget):
    # signal_row_selection_changed = QtCore.pyqtSignal(tuple)
    sig_selection_changed = QtCore.pyqtSignal(tuple)

    def __init__(self, highlight_mode='row'):
        MatplotlibWidget.__init__(self)
        rcParams['image.interpolation'] = None
        self.ax_heatmap = self.fig.add_subplot(111)
        self.ax_heatmap.get_yaxis().set_visible(False)

#        self.ax_ylabel_bar = self.ax_heatmap.twiny()
        [[x1, y1], [x2, y2]] = self.ax_heatmap.get_position().get_points()
        bb = Bbox.from_extents([[0.1, y1], [0.11, y2]])
        self.ax_ylabel_bar = self.fig.add_axes(bb.bounds)
#        self.ax_ylabel_bar.axis('off')

        self.fig.subplots_adjust(right=0.8)
        self.cbar_ax = self.fig.add_axes([0.85, 0.15, 0.05, 0.7])
        self.data = None
        # self._highlight = None
        # self.highlighted_index = None
        self.selector = Selection()
        self.selector.sig_selection_changed.connect(self.sig_selection_changed.emit)


        self.stimulus_indicators = []
        self.highlight_mode = highlight_mode

        self.plot = None
        
    def set(self, data: np.ndarray, *args, ylabels_bar: Series = None, cmap_ylabels_bar: str = 'tab20', **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.ax_heatmap.cla()
        # self._highlight = None
        self.cbar_ax.cla()
        self.data = data

        # labels = kwargs.pop('ylabels_bar')
        # cmap_ylabels_bar = kwargs.pop('cmap_ylabels_bar')

        self.plot = seaborn_heatmap(data, *args, ax=self.ax_heatmap, cbar_ax=self.cbar_ax, **kwargs)

        self.selector.set(self, mode=self.highlight_mode)
        # if isinstance(self.selector, Selection):
        #     self.selector.sig_selection_changed.disconnect(self.sig_selection_changed.emit)
        #     del self.selector

        # self.selector = Selection(self, mode=self.highlight_mode)

        if ylabels_bar is not None:
            self._set_ylabel_bar(ylabels_bar, cmap=cmap_ylabels_bar)

        self.draw()

    def _set_ylabel_bar(self, labels : Series, cmap: str = 'tab20'):
        assert isinstance(labels, Series)

        self.ax_ylabel_bar.cla()

        [[x1, y1], [x2, y2]] = self.ax_heatmap.get_position().get_points()
        bb = Bbox.from_extents([[0.123, y1], [0.11, y2]])
        self.ax_ylabel_bar.set_position(bb)

        # self.ax_ylabel_bar.get_xaxis().set_visible(False)s
        # self.ax_ylabel_bar.get_yaxis().set_visible(False)
        self.ax_ylabel_bar.axis('off')

        labels_unique = labels.unique()
        colors_map = {}

        for ix, c in enumerate(labels_unique):
            colors_map.update({labels_unique[ix]: ix})

        colors = labels.map(colors_map)
        color_labels_array = np.expand_dims(colors.values, axis=1)

        ylabel_bar = self.ax_ylabel_bar.imshow(color_labels_array, aspect='auto', cmap=cmap)

        cs = np.unique(color_labels_array.ravel())
        colors = [ylabel_bar.cmap(ylabel_bar.norm(c)) for c in cs]
        ps = [MPatch(color=colors[i], label=labels_unique[i]) for i in range(len(cs))]
        self.ax_ylabel_bar.legend(handles=ps, bbox_to_anchor=(1,1))

    # def highlight_row(self, ev):
    #     if type(ev) is int:
    #         ix = ev
    #     else:
    #         ix = ev.ydata
    #         ix = int(ix)
    #         if ix is None:
    #             return
    #     self.highlighted_index = ix
    #     self.signal_row_selection_changed.emit((0, ix))
    #     if self._highlight is not None:
    #         self._highlight.remove()
    #     self._highlight = self.plot.add_patch(RectangularPatch((0, ix), self.data.shape[1], 1, facecolor='w', edgecolor='k', lw=3, alpha=0.5))
    #     self.draw()

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

        self.canvas = heatmap_obj.canvas
        self.plot = heatmap_obj.plot
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
        elif mode == 'span':
            rp = dict(facecolor='w', edgecolor='k', lw=1, alpha=0.5)
            self.RS = RectangleSelector(self.heatmap.plot, self.line_select_callback,
                                        drawtype='box', useblit=True,
                                        button=[1, 3],  # don't use middle button
                                        minspanx=1, minspany=1,
                                        spancoords='data',
                                        interactive=True, rectprops=rp)
            self.RS.set_active(True)
        else:
            raise ValueError("Invalid selection mode: '" + str(mode) + "' Valid modes are: 'row', 'item' or 'span'.")

    def _clear_highlight(self):
        if self._highlight is not None:
            self._highlight.remove()
    
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
            y = ev.ydata
            
            if y is None:
                return
            
            y = int(y)
            
        ix = (0, y)
        self.update_selection(ix)
        self._draw_row_selection(y)
    
    def _draw_row_selection(self, y):
        self._highlight = self.plot.add_patch(RectangularPatch((0, y), self.heatmap.data.shape[1], 1, facecolor='w', edgecolor='k', lw=3, alpha=0.5))
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
        print('bah')

        print('Key pressed.')
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
            

class Clustermap(Heatmap):
    def __init__(self):
        Heatmap.__init__(self)

    def set(self, data: np.ndarray, *args, **kwargs):
        """
        :param data:    2D numpy array
        :param args:    Additional args that are passed to sns.heatmap()
        :param kwargs:  Additional kwargs that are passed to sns.heatmap()
        """
        self.ax_heatmap.cla()
        self.cbar_ax.cla()
        self.data = data
        self.plot = sns.clustermap(data, *args, ax=self.ax_heatmap, cbar_ax=self.cbar_ax, **kwargs)
        self.draw()

if __name__ == '__main__':
    import pickle
    from sklearn.metrics import pairwise_distances
    t = pickle.load(open('/home/daniel/Documents/jupyter notebooks/Getting units from Transmission object/cell_types_rfft_spliced_500_test_units.trn', 'rb'))
    df = t['df']
    
    data = np.vstack(df._SPLICE_ARRAYS)
    
#    dists = pairwise_distances(data)
    
    app = QtWidgets.QApplication([])
    w = Heatmap(highlight_mode='row')
    w.set(data, cmap='jet', ylabels_bar=df.promoter)
    
    w.show()
    app.exec_()
