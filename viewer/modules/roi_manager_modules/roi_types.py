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
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from typing import Type, TypeVar
from functools import partial


ROIClasses = TypeVar('T', bound='AbstractBaseROI')


class AbstractBaseROI(metaclass=abc.ABCMeta):
    def __init__(self, curve_plot_item: pg.PlotDataItem):
        assert isinstance(curve_plot_item, pg.PlotDataItem)

        self._tags = {}

        self.curve_plot_item = curve_plot_item
        self.roi_graphics_object = QtWidgets.QGraphicsObject()

    @property
    def curve_data(self):
        return self.curve_plot_item.getData()

    @curve_data.setter
    def curve_data(self, xs: np.ndarray, ys: np.ndarray):
        self.curve_plot_item.setData(x=xs, y=ys)

    @property
    def zValue(self):
        return self._zValue

    @zValue.setter
    def zValue(self, val: int):
        self._zValue = val

    @abc.abstractmethod
    def get_roi_graphics_object(self) -> QtWidgets.QGraphicsObject:
        pass

    @abc.abstractmethod
    def set_roi_graphics_object(self, *args, **kwargs):
        pass

    def set_tag(self, roi_def, tag):
        self._tags[roi_def] = tag

    def get_tag(self, roi_def):
        return self._tags[roi_def]

    def get_all_tags(self):
        return self._tags

    def add_to_viewer(self, view: pg.ViewBox):
        view.addItem(self.get_roi_graphics_object())

    def remove_from_viewer(self, view):
        pass

    @abc.abstractmethod
    def to_state(self):
        pass

    @abc.abstractmethod
    @classmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, state: dict):
        pass


class ManualROI(AbstractBaseROI):
    def __init__(self, roi_graphics_object: pg.ROI, curve_plot_item: pg.PlotDataItem, state=None):
        """
        :type state: dict
        """
        assert isinstance(roi_graphics_object, pg.ROI)

        super(ManualROI, self).__init__(curve_plot_item)

        self.set_roi_graphics_object(roi_graphics_object)

        if state is not None:
            self._set_roi_graphics_object_state(state['roi_graphics_object_state'])

    def get_roi_graphics_object(self) -> pg.ROI:
        return self.roi_graphics_object

    def set_roi_graphics_object(self, graphics_object):
        self.roi_graphics_object = graphics_object

    def _set_roi_graphics_object_state(self, state):
        self.roi_graphics_object.setState(state)

    def to_state(self):
        curve_data = self.curve_data
        curve_xs = curve_data[0]
        curve_ys = curve_data[1]

        roi_state = self.roi_graphics_object.saveState()

        state = {'curve_xs': curve_xs,
                 'curve_ys': curve_ys,
                 'roi_state': roi_state
                 }

    @classmethod
    def from_state(cls, curve_plot_item, state):
        roi_graphics_object = pg.ROI.PolyLineROI([[0, 0], [10, 10], [30, 10]], closed=True, pos=[0, 0], removable=True)
        return cls(curve_plot_item, roi_graphics_object, state)


class CNMFROI(AbstractBaseROI):
    def __init__(self, curve_plot_item: pg.PlotDataItem, curve_data=None, contour=None, state=None):
        """
        :type: curve_data: np.ndarray
        :type: contour: np.ndarray
        :type  state: dict
        """
        super(CNMFROI, self).__init__(curve_plot_item)

        self.roi_xs = np.empty(0)
        self.roi_ys = np.empty(0)

        if state is not None:
            self._restore_state(state)

    def set_curve_data(self, y_vals):
        xs = np.arange(len(y_vals))
        self.curve_data = (xs, y_vals)

    def _restore_state(self, state):
        self.roi_xs = state['roi_xs']
        self.roi_ys = state['roi_ys']

        self._create_scatter_plot()
        self.curve_data = (state['curve_xs'], state['curve_ys'])

    def get_roi_graphics_object(self) -> pg.ScatterPlotItem:
        if self.roi_graphics_object is QtWidgets.QGraphicsObject():
            raise AttributeError('Must call roi_graphics_object() first')

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
        self.roi_graphics_object = pg.ScatterPlotItem(self.roi_xs, self.roi_ys)

    def to_state(self):
        curve_data = self.curve_data
        curve_xs = curve_data[0]
        curve_ys = curve_data[1]

        state = {'roi_xs':   self.roi_xs,
                 'roi_ys':   self.roi_ys,
                 'curve_xs': curve_xs,
                 'curve_ys': curve_ys
                 }

    @classmethod
    def from_state(cls, curve_plot_item, state):
        return cls(curve_plot_item, state)


class ROIList(list):
    def __init__(self, roi_types: AbstractBaseROI):
        super(ROIList, self).__init__()

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self.highlight_roi_and_curve)
        self.roi_types = roi_types

    def set_parent_viewer(self, viewer: pg.ImageView):
        self.viewer = viewer

    def append(self, roi: AbstractBaseROI):
        assert issubclass(roi, AbstractBaseROI)
        self.list_widget.addItem(str(self.__len__()))
        roi.add_to_viewer(self.viewer)

        roi_graphics_object = roi.get_roi_graphics_object()

        if isinstance(roi_graphics_object, pg.ROI):
            roi_graphics_object.sigHoverEvent.connect(partial(self.highlight_roi_and_curve, self.index(roi)))
            roi_graphics_object.sigHoverEnd.connect(partial(self.reset_plot_colors, self.index(roi)))
            roi_graphics_object.sigRemoveRequested.connect(partial(self.__delitem__, self.index(roi)))

        super(ROIList, self).append(roi)

    def __delitem__(self, key):
        roi = self.__getitem__(key)

    def __getitem__(self, item) -> AbstractBaseROI:
        return super(ROIList, self).__getitem__(item)

    def highlight_roi_and_curve(self, ix):
        if self.roi_types is ManualROI:
            self.highlight_roi()
            self.highlight_curve()

        elif self.roi_types is CNMFROI:
            self.highlight_curve()

    def highlight_roi(self):
        pass

    def highlight_curve(self):
        pass

    def reset_plot_colors(self):
        pass

    def live_update_plot(self):
        pass

    def del_roi(self):
        pass
