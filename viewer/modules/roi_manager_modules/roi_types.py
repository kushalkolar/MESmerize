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
import pyqtgraphCore as pg
from typing import Type, TypeVar
from functools import partial


ROIClasses = TypeVar('T', bound='AbstractBaseROI')


class AbstractBaseROI(metaclass=abc.ABCMeta):
    def __init__(self, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox):
        assert isinstance(curve_plot_item, pg.PlotDataItem)

        self._tags = {}

        self.curve_plot_item = curve_plot_item
        self.view_box = view_box
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

    def add_to_viewer(self):
        self.view_box.addItem(self.get_roi_graphics_object())

    def remove_from_viewer(self):
        self.view_box.removeItem(self.get_roi_graphics_object())
        del self.curve_plot_item

    def __del__(self):
        self.remove_from_viewer()

    @abc.abstractmethod
    def to_state(self):
        pass

    @abc.abstractmethod
    @classmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, state: dict):
        pass


class ManualROI(AbstractBaseROI):
    def __init__(self, roi_graphics_object: pg.ROI, curve_plot_item: pg.PlotDataItem,
                 view_box: pg.ViewBox, state=None):
        """
        :type state: dict
        """
        assert isinstance(roi_graphics_object, pg.ROI)

        super(ManualROI, self).__init__(curve_plot_item, view_box)

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
    def __init__(self, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox,
                 curve_data=None, contour=None, state=None):
        """
        :type: curve_data: np.ndarray
        :type: contour: np.ndarray
        :type  state: dict
        """
        super(CNMFROI, self).__init__(curve_plot_item, view_box)

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
    def __init__(self, roi_types: AbstractBaseROI, viewer: pg.ImageView):
        super(ROIList, self).__init__()

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentItemChanged.connect(self._get_list_widget_index)
        self.roi_types = roi_types

        if self.roi_types is ManualROI:
            self.live_plot_checkbox = QtWidgets.QCheckBox()
            self.live_plot_checkbox.setChecked(False)

        self.viewer = viewer

    def append(self, roi: AbstractBaseROI):
        assert issubclass(roi, AbstractBaseROI)
        self.list_widget.addItem(str(self.__len__()))
        roi.add_to_viewer()

        roi_graphics_object = roi.get_roi_graphics_object()

        if isinstance(roi_graphics_object, pg.ROI):
            roi_graphics_object.sigHoverEvent.connect(partial(self.highlight_roi_and_curve, self.index(roi)))
            roi_graphics_object.sigHoverEnd.connect(partial(self.unhighlight_curve, self.index(roi)))
            roi_graphics_object.sigRemoveRequested.connect(partial(self.__delitem__, self.index(roi)))
            roi_graphics_object.sigRegionChanged.connect(partial(self._live_update_requested, self.index(roi)))

        super(ROIList, self).append(roi)

    def __delitem__(self, key):
        self.list_widget.takeItem(key)
        super(ROIList, self).__delitem__(key)

    def __getitem__(self, item) -> AbstractBaseROI:
        return super(ROIList, self).__getitem__(item)

    def _get_list_widget_index(self, item: QtWidgets.QListWidgetItem):
        i = int(item.data(0))
        self.highlight_roi_and_curve(i)

    def highlight_roi_and_curve(self, ix: int):
        if self.roi_types is ManualROI:
            # self.highlight_roi(ix)
            self.highlight_curve(ix)

        elif self.roi_types is CNMFROI:
            self.highlight_curve(ix)

    def highlight_roi(self, ix: int):
        self.list_widget.setCurrentRow(ix)

    def highlight_curve(self, ix: int):
        roi = self.__getitem__(ix)
        roi.curve_plot_item.setPen(width=2)

    def unhighlight_curve(self, ix):
        roi = self.__getitem__(ix)
        roi.curve_plot_item.setPen(width=1)

    def _live_update_requested(self, ix: int):
        if self.roi_types is CNMFROI:
            raise TypeError

        if not self.live_plot_checkbox.isChecked():
            return

        roi = self.__getitem__(ix)
        pg_roi = roi.get_roi_graphics_object

        self.get_roi_region(pg_roi, ix)

    def get_roi_region(self, pg_roi: pg.ROI, ix: int):
        image = self.viewer.getProcessedImage()

        if image.ndim == 2:
            axes = (0, 1)
        elif image.ndim == 3:
            axes = (1, 2)
        else:
            return

        # Get the ROI region
        data = pg_roi.getArrayRegion((image.view(np.ndarray)), self.viewer.imageItem, axes)

        if data is not None:
            while data.ndim > 1:
                data = data.mean(axis=1)
            if image.ndim == 3:
                # Set the curve
                roi = self.__getitem__(ix)

                roi.curve_plot_item.setData(y=data, x=self.viewer.tVals)
                roi.curve_plot_item.setPen('w')
                roi.curve_plot_item.show()
            # else:
            #     while coords.ndim > 2:
            #         coords = coords[:,:,0]
            #     coords = coords - coords[:,0,np.newaxis]
            #     xvals = (coords**2).sum(axis=0) ** 0.5
            #     self.workEnv.CurvesList[ID].setData(y=data, x=xvals)
