#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu March 1 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .... import pyqtgraphCore as pg
import numpy as np
import pandas as pd
from .template import *
from ....analysis.data_types import Transmission
from ....analysis.history_widget import HistoryTreeWidget
import traceback
from functools import partial
from ....common import get_window_manager


class PeaksItemGraph(pg.GraphItem):
    """
    Scatter plot to display the peaks and bases as dots which are editable.
    """
    def __init__(self):
        pg.GraphItem.__init__(self)
        self.dragPoint = None
        self.dragOffset = None
        self.scatter.sigClicked.connect(self.clicked)
        self.orig_data = None
        self.mode = 'view'
        self._brush_size = 15
        
        self.changed = False
    
    def set_mode(self, mode: str):
        self.mode = mode
        
    def setData(self, **kwds):
        self.text = kwds.pop('text', [])
        if 'curve_data' in kwds.keys():
            self.curve_data = kwds.pop('curve_data')
        self.data = kwds

        if 'events' in kwds.keys():
            self.events = kwds.pop('events')
        
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
#        self.setTexts(self.text)
        self.updateGraph()


    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)
        
    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        if hasattr(self, '_brush_size'):
            self.scatter.setSize(self._brush_size)
#        for i,item in enumerate(self.textItems):
#            item.setPos(*self.data['pos'][i])
    
    def drag(self, ev):
        if ev.button() != QtCore.Qt.LeftButton:
            ev.ignore()
            return
        
        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first 
            # pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            self.dragOffset = self.data['pos'][ind] - pos
            
#            print(self.data)
#            print(self.dragPoint.data()[0])
            
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return
        
        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset

        x_pos = int(self.data['pos'][ind][0])
        
        if x_pos < 0:
            x_pos = 1
            self.data['pos'][ind][0] = float(x_pos)

        elif x_pos > self.curve_data.shape[0]:
            x_pos = self.curve_data.shape[0] - 1
            self.data['pos'][ind][0] = float(x_pos)

        self.data['pos'][ind][1] = self.curve_data[x_pos]
        self.updateGraph()
        ev.accept()
        
        self.changed = True
    
    def get_edited_dataframe(self) -> pd.DataFrame:
        d = {'event': self.data['pos'][:, 0].astype(np.int64), 'label': self.events}
        df = pd.DataFrame(d).sort_values(by=['event']).reset_index(drop=True)
        return df
    
    def delete_item(self, pt):
        ix = pt.data()[0]
        data = self.data.copy()
        data['pos'] = np.delete(self.data['pos'], ix, axis=0)
        del data['symbolBrush'][ix]
        del self.events[ix]
#        print(self.data)
#        self.updateGraph()
        self.setData(**data)
        self.changed = True

    def delete_all_items(self):
        # while self.scatter.points().size > 1:
        #     self.delete_item(self.scatter.points()[0])
        self.scatter.clear()
        for ix in range(len(self.events)):
            del self.events[0]
    
    def add_item(self, pos):
        x_pos = pos[0]
        y_pos = self.curve_data[x_pos]
        
        item_pos = np.array([x_pos, y_pos])
        
        data = self.data.copy()
        data['pos'] = np.vstack((data['pos'], item_pos))
        
        if self.mode == 'add_peaks':
            event = 'peak'
            brush = pg.fn.mkBrush(255, 0, 0, 150)
            
        elif self.mode == 'add_bases':
            event = 'base'
            brush = pg.fn.mkBrush(0, 255, 0, 150)
        
        self.events.append(event)
        data['symbolBrush'] += [brush]
        
        self.setData(**data)
        self.changed = True
    
    def mouseDragEvent(self, ev):
        if self.mode == 'drag':
            self.drag(ev)
        else:
            ev.ignore()
            return
#        elif self.mode == 'add':
#            print(ev.buttonDownPos())
#        else:
#            ev.ignore()
#    def mouseClickEvent(self, ev):
#        
    
    def clicked(self, scatter_plot, spot_items):
#        print("clicked: %s" % spot_items)
        
        if self.mode == 'delete':
#            print(spot_items)
            if not len(spot_items) == 1:
                return
            self.delete_item(spot_items[0])
    
    def set_brush_size(self, size: int):
        self._brush_size = size
        self.scatter.setSize(size)
            

class PeakEditorWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig_disconnect_flowchart = QtCore.pyqtSignal()
    sig_reconnect_flowchart = QtCore.pyqtSignal()
    sig_send_data = QtCore.pyqtSignal(Transmission)
    
    def __init__(self, trans_curves, trans_peaks_bases):
        # super().__init__()
        super(PeakEditorWindow, self).__init__()
        # Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.tpb = None

        self.connected = True
        self.current_curve = None
        self.btnDisconnectFromFlowchart.setStyleSheet("background-color: yellow")
#        self.current_scatter_plots = None
        self.current_peak_scatter_plot = None
        
        self.mode_buttons = {'view': self.btnModeView, 
                             'drag': self.btnModeDrag,
                             'add_peaks': self.btnModeAddPeaks,
                             'add_bases': self.btnModeAddBases,
                             'delete': self.btnModeDelete
                             }
        
        for btn in self.mode_buttons.values():
            btn.setStyleSheet("background-color: red")
        
        self.current_mode = 'view'
        self.mode_buttons['view'].setStyleSheet("background-color: green")
        self.btnModeView.setChecked(True)
        
        self.connect_mode_buttons()
        
        self.brush_size = 15

        self.history_tree = HistoryTreeWidget()
        self.history_tree.fill_widget(trans_peaks_bases.history_trace.get_all_data_blocks_history)
        self.update_transmission(trans_curves, trans_peaks_bases)
        self._reset_listw()
        self.listwIndices.currentItemChanged.connect(self._set_row)
        self.listwIndices.setCurrentRow(0)
#        self.listwIndices.itemClicked.connect(self._set_row)
        self.sliderDotSize.valueChanged.connect(self._set_pens)
        self.dockWidget.setWidget(self.history_tree)
        
        self.graphicsView.sigMouseClicked.connect(lambda gv, coors: self._add_event(self.current_curve.getViewBox().mapSceneToView(coors).toPoint()))
        
        self.btnSaveCurve.clicked.connect(self.save_current_curve)
        # self.btnClearCurve.clicked.connect(self.clear_current_curve)

        self.btnDisconnectFromFlowchart.clicked.connect(self._disconnect_flowchart)
        self.btnSendToFlowchart.clicked.connect(self._send_data_to_flowchart)

        self.pushButtonOpenInViewer.clicked.connect(self.open_current_curve_in_viewer)

    def _disconnect_flowchart(self):
        self.connected = False
        self.btnDisconnectFromFlowchart.setText('Re-connect to flowchart')
        self.btnDisconnectFromFlowchart.setStyleSheet("background-color: orange")
        self.btnDisconnectFromFlowchart.clicked.disconnect(self._disconnect_flowchart)
        self.btnDisconnectFromFlowchart.clicked.connect(self._reconnect_flowchart)
        self.sig_disconnect_flowchart.emit()
    
    def _reconnect_flowchart(self):
        if QtWidgets.QMessageBox.question(self, 'RECONNECT?', 'Are you sure you want to reconnect to the flowchart?\n'
                                                              'YOU WILL LOOSE ALL MODFICATIONS THAT YOU HAVE MADE!') == QtWidgets.QMessageBox.No:
            return
        # self.btnDisconnectFromFlowchart.setChecked(False)
        self.btnDisconnectFromFlowchart.clicked.disconnect(self._reconnect_flowchart)
        self.btnDisconnectFromFlowchart.clicked.connect(self._disconnect_flowchart)
        self.btnDisconnectFromFlowchart.setText('Disconnect from flowchart')
        self.btnDisconnectFromFlowchart.setStyleSheet("background-color: yellow")
        self.connected = True
        self.sig_reconnect_flowchart.emit()
    
    def _send_data_to_flowchart(self):
        if self.get_data() is None:
            QtWidgets.QMessageBox.warning(self, 'Nothing to send', 'No data has been loaded that can be transmitted')
            return

        self.save_current_curve()

        to_send = self.get_data().copy()
        to_send.df = to_send.df[~to_send.df.apply(lambda r: r.peaks_bases.empty, axis=1)]
        self.sig_send_data.emit(to_send)
        
    def connect_mode_buttons(self):
        for k in self.mode_buttons.keys():
            self.mode_buttons[k].clicked.connect(partial(self.set_mode, k))
        
    def set_mode(self, mode):
        self.mode_buttons[self.current_mode].setStyleSheet("background-color: red")
        self.mode_buttons[self.current_mode].setChecked(False)
        
        self.mode_buttons[mode].setStyleSheet("background-color: green")
        self.current_mode = mode
        
        self.current_peak_scatter_plot.set_mode(mode)

    
    def _add_event(self, qpoint: QtCore.QPoint):
        if self.current_mode not in ['add_peaks', 'add_bases']:
            return
        self.current_peak_scatter_plot.add_item((qpoint.x(), qpoint.y()))

    def update_transmission(self, trans_curves: Transmission, trans_peaks_bases: Transmission):
        if not self.connected:
            return
        
        if hasattr(self, 'tc'):
            if self.tc.df.index.size != trans_curves.df.index.size:
                self.tc = trans_curves
                self._reset_listw()

            elif self.tc != trans_curves:
                self.tc = trans_curves
                self._set_row()
        else:
            self.tc = trans_curves

        self.tpb = trans_peaks_bases.copy()
        self._set_row()
        self.history_tree.fill_widget(trans_peaks_bases.history_trace.get_all_data_blocks_history())

    def _reset_listw(self):
        self.listwIndices.clear()
        self.listwIndices.addItems(list(map(str, [*range(self.tc.df.index.size)])))
    
    def save_current_curve(self):
        ix = self.current_ix
        self.tpb.df.at[ix, 'peaks_bases'] = self.current_peak_scatter_plot.get_edited_dataframe()
        self.current_peak_scatter_plot.changed = False

    def clear_current_curve(self):
        self.current_peak_scatter_plot.delete_all_items()
        self.save_current_curve()

    def _set_row(self):
        if self.current_peak_scatter_plot is not None:
            if self.current_peak_scatter_plot.changed:
                self.save_current_curve()

        self.graphicsView.clear()

        ix = self.listwIndices.currentRow()
        self.current_ix = ix
        curve_plot = pg.PlotDataItem()
        self.current_curve = curve_plot

        curve = self.tc.df['curve'].iloc[ix]

        sample_id = self.tc.df['SampleID'].iloc[ix]
        if not isinstance(sample_id, str):
            try:
                sample_id = str(sample_id)
            except:
                print("Could not display SampleID for curve at index: " + str(ix))
        self.lineEditSampleID.setText(sample_id)

        curve_plot.setData(curve)

        self.graphicsView.addItem(curve_plot)


        try:
            bases = self.tpb.df['peaks_bases'].iloc[ix]['event'][self.tpb.df['peaks_bases'].iloc[ix]['label'] == 'base'].values
            peaks = self.tpb.df['peaks_bases'].iloc[ix]['event'][self.tpb.df['peaks_bases'].iloc[ix]['label'] == 'peak'].values#tolist()

        except Exception:
            QtWidgets.QMessageBox.warning(self, 'Warning', 'The curve probably contains no peaks.\n' +
                                          traceback.format_exc())
            peaks = np.array([], dtype=int)
            bases = np.array([], dtype=int)

        xs = peaks; ys = np.take(curve, peaks)
        peaks_data = np.column_stack((xs, ys))

        xs_b = bases; ys_b = np.take(curve, bases)
        bases_data = np.column_stack((xs_b, ys_b))


        events = ((['base'] * bases_data.shape[0] + ['peak'] * peaks_data.shape[0]))

        all_data = np.vstack((bases_data, peaks_data))
        red_brushes = [pg.fn.mkBrush(255, 0, 0, 150)] * peaks_data.shape[0]
        green_brushes = [pg.fn.mkBrush(0, 255, 0, 150)] * bases_data.shape[0]
        all_brushes = green_brushes + red_brushes


        peaks_plot = PeaksItemGraph()
        peaks_plot.set_mode(self.current_mode)

        peaks_plot.setData(pos=all_data, size=self.brush_size, symbolBrush=all_brushes, curve_data=curve, events=events)# / min_curve)

        self.graphicsView.addItem(peaks_plot)
        self.current_peak_scatter_plot =peaks_plot

    def open_current_curve_in_viewer(self):
        w = get_window_manager().get_new_viewer_window()

        row = self.tc.df.iloc[self.current_ix]
        proj_path = self.tc.get_proj_path()
        w.open_from_dataframe(proj_path, row=row)

    def _set_pens(self, n):
        self.current_peak_scatter_plot.set_brush_size(n)
        self.brush_size = n


    def get_data(self) -> Transmission:
        return self.tpb
