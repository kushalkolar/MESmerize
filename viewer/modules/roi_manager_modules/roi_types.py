# -*- coding: utf-8 -*-
"""
Created on April 23 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import abc
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from typing import Type, TypeVar


ROIClasses = TypeVar('T', bound='AbstractBaseROI')


class ROIList(list):
    def __init__(self):
        super(ROIList, self).__init__()

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self.highlight_roi_and_curve)

        self.roi_types = None

    def set_parent_viewer(self, viewer: pg.ImageView):
        self.parent_viewer = viewer

    def append(self, roi: AbstractBaseROI):
        roi.add_to_viewer(self.parent_viewer)
        super(ROIList, self).append(roi)

    def __delitem__(self, key):
        roi = self.__getitem__(key)

    def __getitem__(self, item) -> AbstractBaseROI:
        return super(ROIList, self).__getitem__(item)

    def highlight_roi_and_curve(self):
        if self.roi_types is ManualROI:
            self.highlight_roi()
            self.highlight_curve()

        elif self.roi_types is CNMFROI:
            self.highlight_curve()

    def highlight_roi(self):
        pass

    def highlight_curve(self):
        pass


class AbstractBaseROI(metaclass=abc.ABCMeta):
    def __init__(self, curve_plot_item: pg.PlotItem):
        self._curve_data = np.empty(0)
        self._tags = {}

        self.curve_plot_item = curve_plot_item
        self.roi_graphics_object = QtWidgets.QGraphicsObject()

    @property
    def zValue(self):
        return self._zValue

    @zValue.setter
    def zValue(self, val: int):
        self._zValue = val

    @abc.abstractmethod
    def set_curve_data(self, data: np.ndarray):
        pass

    @abc.abstractmethod
    def get_curve_data(self) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_roi_graphics_object(self) -> QtWidgets.QGraphicsObject:
        pass

    @abc.abstractmethod
    def set_roi_graphics_object(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def set_tag(self, roi_def, tag):
        pass

    @abc.abstractmethod
    def get_tag(self, roi_def):
        pass

    @abc.abstractmethod
    def get_all_tags(self):
        pass

    def add_to_viewer(self, view: pg.ViewBox):
        view.addItem(self.get_roi_graphics_object())

    def remove_from_viewer(self, view):
        pass

    @abc.abstractmethod
    def to_state(self):
        pass

    @abc.abstractmethod
    @classmethod
    def from_state(cls, curve_plot_item: pg.PlotItem, state: dict):
        pass


class ManualROI(AbstractBaseROI):
    def __init__(self, roi_graphics_object: pg.ROI, curve_plot_item: pg.PlotItem, **kwargs):
        super(ManualROI, self).__init__(curve_plot_item)

        self.set_roi_graphics_object(roi_graphics_object)

        for key in kwargs.keys():
            if key =='roi_graphics_object_state':
                self.set_roi_graphics_object_state(kwargs['roi_graphics_object_state'])
                continue

            setattr(self, key, kwargs[key])

    def set_curve_data(self, data: np.ndarray):
        return self._curve_data

    def get_curve_data(self):
        pass

    def get_roi_graphics_object(self):
        pass

    def set_roi_graphics_object(self, graphics_object):
        self.roi_graphics_object = graphics_object

    def set_roi_graphics_object_state(self, state):
        self.roi_graphics_object.setState(state)

    def set_tag(self, roi_def, tag):
        pass

    def get_tag(self, roi_def):
        pass

    def get_all_tags(self):
        pass

    def to_state(self):
        pass

    @classmethod
    def from_state(cls, curve_plot_item, state):
        roi_graphics_object = pg.ROI.PolyLineROI([[0,0], [10,10], [30,10]], closed=True, pos=[0,0], removable=True)
        return cls(roi_graphics_object=roi_graphics_object, curve_plot_item=curve_plot_item, **state)


class CNMFROI(AbstractBaseROI):
    def __init__(self, curve_plot_item: pg.PlotItem, **kwargs):
        super(CNMFROI, self).__init__(curve_plot_item)
    
    def set_curve_data(self, data: np.ndarray):
        return self._curve_data

    def get_curve_data(self) -> np.ndarray:
        return self._curve_data

    def get_roi_graphics_object(self) -> pg.ScatterPlotItem:
        if self.roi_graphics_object is QtWidgets.QGraphicsObject():
            raise AttributeError('Must call roi_graphics_object() first')

        return self.roi_graphics_object

    def set_roi_graphics_object(self, contour: dict):
        cors = contour['coordinates']
        cors = cors[~np.isnan(cors).any(axis=1)]

        xs = cors[:, 0].flatten()
        ys = cors[:, 1].flatten()

        xs = xs.astype(int)
        ys = ys.astype(int)

        self.roi_graphics_object = pg.ScatterPlotItem(xs, ys)

    def set_tag(self, roi_def, tag):
        pass

    def get_tag(self, roi_def):
        pass

    def get_all_tags(self):
        pass

    def to_state(self):
        pass

    @classmethod
    def from_state(cls, curve_plot_item, state):
        return cls(curve_plot_item=curve_plot_item, **state)
