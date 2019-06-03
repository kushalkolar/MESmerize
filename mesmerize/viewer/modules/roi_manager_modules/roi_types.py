# -*- coding: utf-8 -*-
"""
Created on June 20 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import abc
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraphCore as pg
# from typing import Type, TypeVar
from common import get_proj_config
from copy import deepcopy


class AbstractBaseROI(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state: dict):
        pass

    @property
    @abc.abstractmethod
    def curve_data(self) -> list:
        pass

    @curve_data.setter
    @abc.abstractmethod
    def curve_data(self, data: list):
        """
        :param data: [x, y], [np.ndarray, np.ndarray]
        """
        pass

    @abc.abstractmethod
    def get_roi_graphics_object(self) -> QtWidgets.QGraphicsObject:
        pass

    @abc.abstractmethod
    def set_roi_graphics_object(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def reset_color(self):
        pass

    @abc.abstractmethod
    def set_original_color(self, color):
        pass

    @abc.abstractmethod
    def get_color(self):
        pass

    @abc.abstractmethod
    def set_color(self, color: np.ndarray, *args, **kwargs):
        pass

    @abc.abstractmethod
    def set_text(self, text: str):
        pass

    @abc.abstractmethod
    def set_tag(self, roi_def: str, tag: str):
        pass

    @abc.abstractmethod
    def get_tag(self, roi_def) -> str:
        pass

    @abc.abstractmethod
    def get_all_tags(self) -> dict:
        pass

    @abc.abstractmethod
    def add_to_viewer(self):
        pass

    @abc.abstractmethod
    def remove_from_viewer(self):
        pass

    @abc.abstractmethod
    def to_state(self):
        pass

    @classmethod
    @abc.abstractmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state: dict):
        pass


class BaseROI(AbstractBaseROI):
    def __init__(self, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state: dict = None):
        # super().__init__(curve_plot_item, view_box, state)
        if isinstance(curve_plot_item, pg.PlotDataItem):
            self.curve_plot_item = curve_plot_item
            self.curve_plot_item.setZValue(1)
        else:
            self.curve_plot_item = None

        if state is None:
            self._tags = dict.fromkeys(get_proj_config().options('ROI_DEFS'))
        else:
            self._tags = state['tags']
            self.curve_data = state['curve_data']

        self.view_box = view_box
        self.roi_graphics_object = None
        self._color = None
        self._original_color = None

    @property
    def curve_data(self):
        return self.curve_plot_item.getData()

    @curve_data.setter
    def curve_data(self, data: list):
        """
        :param data: [x, y], [np.ndarray, np.ndarray]
        """

        if self.curve_plot_item is None:
            return
        self.curve_plot_item.setData(x=data[0], y=data[1])

    @property
    def zValue(self):
        return self._zValue

    @zValue.setter
    def zValue(self, val: int):
        self._zValue = val

    def get_roi_graphics_object(self) -> QtWidgets.QGraphicsObject:
        pass

    def set_roi_graphics_object(self, *args, **kwargs):
        pass

    def reset_color(self):
        self.set_color(self._original_color)

    def set_original_color(self, color):
        self._original_color = color
        self.reset_color()

    def get_color(self):
        return self._color

    def set_color(self, color: np.ndarray, *args, **kwargs):
        pen = pg.mkPen(color, *args, **kwargs)
        self.roi_graphics_object.setPen(pen)
        self.curve_plot_item.setPen(pen)
        if isinstance(self.roi_graphics_object, pg.ScatterPlotItem):
            self.roi_graphics_object.setBrush(pg.mkBrush(color, *args, **kwargs))

    def set_text(self, text: str):
        text_item = pg.TextItem(text)
        # self.view_box.addItem()

    def set_tag(self, roi_def: str, tag: str):
        self._tags[roi_def] = tag

    def get_tag(self, roi_def) -> str:
        if self._tags[roi_def] is None:
            return ''
        return self._tags[roi_def]

    def get_all_tags(self) -> dict:
        d = deepcopy(self._tags)
        for key in d.keys():
            if d[key] is None:
                d[key] = ''
        return d

    def add_to_viewer(self):
        self.view_box.addItem(self.get_roi_graphics_object())

    def remove_from_viewer(self):
        roi = self.get_roi_graphics_object()
        self.view_box.removeItem(roi)
        if self.curve_plot_item is not None:
            self.curve_plot_item.clear()
        del self.curve_plot_item
        del roi


class ManualROI(BaseROI):
    def __init__(self, curve_plot_item: pg.PlotDataItem,
                 roi_graphics_object: pg.ROI,
                 view_box: pg.ViewBox, state=None):
        """
        :type state: dict
        """
        assert isinstance(roi_graphics_object, pg.ROI)

        super(ManualROI, self).__init__(curve_plot_item, view_box, state)

        self.set_roi_graphics_object(roi_graphics_object)

        if state is not None:
            self._set_roi_graphics_object_state(state['roi_graphics_object_state'])

    def get_roi_graphics_object(self) -> pg.ROI:
        return self.roi_graphics_object

    def set_roi_graphics_object(self, graphics_object: pg.ROI):
        self.roi_graphics_object = graphics_object

    def _set_roi_graphics_object_state(self, state):
        self.roi_graphics_object.setState(state)

    def to_state(self):
        if isinstance(self.roi_graphics_object, pg.PolyLineROI):
            shape = 'PolyLineROI'
        elif isinstance(self.roi_graphics_object, pg.EllipseROI):
            shape = 'EllipseROI'

        state = {'curve_data': self.curve_data,
                 'shape': shape,
                 'roi_graphics_object_state': self.roi_graphics_object.saveState(),
                 'tags': self.get_all_tags(),
                 'roi_type': 'ManualROI'
                 }
        return state

    @staticmethod
    def get_generic_roi_graphics_object(shape: str, dims: tuple) -> pg.ROI:
        x = dims[0]
        y = dims[1]

        if shape == 'PolyLineROI':
            roi_graphics_object = pg.PolyLineROI([[0, 0],
                                                  [int(0.1 * x), 0],
                                                  [int(0.1 * x), int(0.1 * y)],
                                                  [0, int(0.1 * y)]],
                                                 closed=True, pos=[0, 0], removable=True)
            return roi_graphics_object
        elif shape == 'EllipseROI':
            roi_graphics_object = pg.EllipseROI(pos=[0, 0], size=[x, y], removable=True)
            return roi_graphics_object

    @classmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state: dict):
        roi_graphics_object = ManualROI.get_generic_roi_graphics_object(state['shape'], (10, 10))
        return cls(curve_plot_item=curve_plot_item, roi_graphics_object=roi_graphics_object, view_box=view_box, state=state)

    @classmethod
    def from_positions(cls, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, positions: list):
        """
        :param positions: list of (x, y) tuples; [(x1, y1), (x2, y2), ... (xn, yn)]
        """
        roi_graphics_object = pg.PolyLineROI(positions=positions, closed=True, removable=True)
        return cls(curve_plot_item=curve_plot_item, roi_graphics_object=roi_graphics_object, view_box=view_box)


class CNMFROI(BaseROI):
    def __init__(self, curve_plot_item: pg.PlotDataItem,
                 view_box: pg.ViewBox, cnmf_idx: int = None,
                 curve_data=None, contour=None, state=None):
        """
        :type: curve_data:  np.ndarray
        :param curve_data:  1D numpy array of y values
        :type  contour:     np.ndarray
        :type  state:       dict
        :param cnmf_idx:    original index of the ROI from cnmf idx_components
        """
        super(CNMFROI, self).__init__(curve_plot_item, view_box, state)

        self.roi_xs = np.empty(0)
        self.roi_ys = np.empty(0)

        if state is None:
            self.set_roi_graphics_object(contour)
            self.set_curve_data(curve_data)
            self.cnmf_idx = cnmf_idx
        else:
            self._restore_state(state)
            #self.cnmf_idx = cnmf_idx

    def set_curve_data(self, y_vals):
        xs = np.arange(len(y_vals))
        self.curve_data = [xs, y_vals]

    def _restore_state(self, state):
        self.roi_xs = state['roi_xs']
        self.roi_ys = state['roi_ys']

        self._create_scatter_plot()
        # self.curve_data = state['curve_data']
        self.cnmf_idx = state['cnmf_idx']
        
    def get_roi_graphics_object(self) -> pg.ScatterPlotItem:
        if self.roi_graphics_object is None:
            raise AttributeError('Must call set_roi_graphics_object() first')

        return self.roi_graphics_object

    def set_roi_graphics_object(self, contour: dict):
        cors = contour['coordinates']
        cors = cors[~np.isnan(cors).any(axis=1)]

        xs = cors[:, 0].flatten()
        ys = cors[:, 1].flatten()

        self.roi_xs = xs.astype(int)
        self.roi_ys = ys.astype(int)

        self._create_scatter_plot()

    def _create_scatter_plot(self):
        self.roi_graphics_object = pg.ScatterPlotItem(self.roi_xs, self.roi_ys, symbol='s')

    def to_state(self) -> dict:
        state = {'roi_xs':      self.roi_xs,
                 'roi_ys':      self.roi_ys,
                 'curve_data':  self.curve_data,
                 'tags':        self.get_all_tags(),
                 'roi_type':    'CNMFROI',
                 'cnmf_idx':    self.cnmf_idx
                 }
        return state

    @classmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state: dict):
        return cls(curve_plot_item=curve_plot_item, view_box=view_box, state=state)
