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
from ...core.common import ViewerInterface
from common import configuration
from copy import deepcopy


ROIClasses = TypeVar('T', bound='AbstractBaseROI')


class AbstractBaseROI(metaclass=abc.ABCMeta):
    def __init__(self, curve_plot_item: pg.PlotDataItem, view_box: pg.ViewBox, state=None):
        assert isinstance(curve_plot_item, pg.PlotDataItem)

        if state is None:
            self._tags = dict.fromkeys(configuration.proj_cfg.options('ROI_DEFS'))
        else:
            self._tags = state['tags']

        self.curve_plot_item = curve_plot_item
        self.view_box = view_box
        self.roi_graphics_object = None

    @property
    def curve_data(self):
        return self.curve_plot_item.getData()

    @curve_data.setter
    def curve_data(self, data: list):

        """
        :param data: [x, y], [np.ndarray, np.ndarray]
        """
        self.curve_plot_item.setData(x=data[0], y=data[1])

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
        self.view_box.removeItem(self.get_roi_graphics_object())
        del self.curve_plot_item

    def __del__(self):
        self.remove_from_viewer()

    @abc.abstractmethod
    def to_state(self):
        pass

    @classmethod
    @abc.abstractmethod
    def from_state(cls, curve_plot_item: pg.PlotDataItem, state: dict):
        pass


class ManualROI(AbstractBaseROI):
    def __init__(self, roi_graphics_object: pg.ROI, curve_plot_item: pg.PlotDataItem,
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
                 'roi_state': roi_state,
                 'tags': self.get_all_tags(),
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
        super(CNMFROI, self).__init__(curve_plot_item, view_box, state)

        self.roi_xs = np.empty(0)
        self.roi_ys = np.empty(0)

        if state is not None:
            self._restore_state(state)
        else:
            self.set_roi_graphics_object(contour)
            self.set_curve_data(curve_data)

    def set_curve_data(self, y_vals):
        xs = np.arange(len(y_vals))
        self.curve_data = [xs, y_vals]

    def _restore_state(self, state):
        self.roi_xs = state['roi_xs']
        self.roi_ys = state['roi_ys']

        self._create_scatter_plot()
        self.curve_data = (state['curve_xs'], state['curve_ys'])

    def get_roi_graphics_object(self) -> pg.ScatterPlotItem:
        if self.roi_graphics_object is None:
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
        self.roi_graphics_object = pg.ScatterPlotItem(self.roi_xs, self.roi_ys, symbol='s')

    def to_state(self) -> dict:
        curve_data = self.curve_data
        curve_xs = curve_data[0]
        curve_ys = curve_data[1]

        state = {'roi_xs':   self.roi_xs,
                 'roi_ys':   self.roi_ys,
                 'curve_xs': curve_xs,
                 'curve_ys': curve_ys,
                 'tags':     self.get_all_tags()
                 }
        return state

    @classmethod
    def from_state(cls, curve_plot_item, state):
        return cls(curve_plot_item, state)


class ROIList(list):
    def __init__(self, ui, roi_types: str, viewer_interface: ViewerInterface):
        super(ROIList, self).__init__()

        assert isinstance(ui.listWidgetROIs, QtWidgets.QListWidget)
        self.list_widget = ui.listWidgetROIs
        self.list_widget.clear()
        self.list_widget.currentRowChanged.connect(self.set_current_index)

        assert isinstance(ui.listWidgetROITags, QtWidgets.QListWidget)
        self.list_widget_tags = ui.listWidgetROITags
        self.list_widget_tags.clear()

        self.roi_types = roi_types

        assert isinstance(ui.checkBoxLivePlot, QtWidgets.QCheckBox)
        self.live_plot_checkbox = ui.checkBoxLivePlot
        self.live_plot_checkbox.setChecked(False)
        if self.roi_types == 'ManualROI':
            self.live_plot_checkbox.setEnabled(True)
        else:
            self.live_plot_checkbox.setEnabled(False)

        assert isinstance(ui.checkBoxShowAll, QtWidgets.QCheckBox)
        self.show_all_checkbox = ui.checkBoxShowAll
        self.show_all_checkbox.setChecked(True)
        self.show_all_checkbox.toggled.connect(self.slot_show_all_checkbox_clicked)

        assert isinstance(ui.btnSetROITag, QtWidgets.QPushButton)
        self.btn_set_tag = ui.btnSetROITag
        self.btn_set_tag.clicked.connect(self.slot_btn_set_tag)

        assert isinstance(ui.lineEditROITag, QtWidgets.QLineEdit)
        self.line_edit_tag = ui.lineEditROITag

        self.vi = viewer_interface

        self.previous_index = -1

        configuration.project_manager.signal_project_config_changed.connect(self.update_roi_defs_from_configuration)

        # configuration.proj_cfg_changed.register(self.update_roi_defs_from_configuration)

    def append(self, roi: AbstractBaseROI):
        self.list_widget.addItem(str(self.__len__()))
        ix = self.__len__()
        roi.add_to_viewer()

        roi_graphics_object = roi.get_roi_graphics_object()

        if isinstance(roi_graphics_object, pg.ROI):
            roi_graphics_object.sigHoverEvent.connect(partial(self.highlight_curve, self.index(roi)))
            roi_graphics_object.sigHoverEnd.connect(partial(self.highlight_roi, self.index(roi)))
            roi_graphics_object.sigHoverEnd.connect(partial(self.unhighlight_curve, self.index(roi)))
            roi_graphics_object.sigRemoveRequested.connect(partial(self.__delitem__, self.index(roi)))
            roi_graphics_object.sigRegionChanged.connect(partial(self._live_update_requested, self.index(roi)))

        self.vi.workEnv_changed('ROI Added')
        super(ROIList, self).append(roi)

    def __delitem__(self, key):
        self.vi.workEnv_changed('ROI Removed')
        self.list_widget.takeItem(key)
        super(ROIList, self).__delitem__(key)

    def __getitem__(self, item) -> AbstractBaseROI:
        return super(ROIList, self).__getitem__(item)

    def set_current_index(self, ix):
        if ix == -1:
            return
        self.current_index = ix
        self.highlight_curve(ix)
        self.highlight_roi(ix)
        if not self.show_all_checkbox.isChecked():
            self._hide_all_graphics_objects()
        self._show_graphics_object(ix)
        self.set_list_widget_tags()

    def highlight_roi(self, ix: int):
        self.list_widget.setCurrentRow(ix)

    def highlight_curve(self, ix: int):
        roi = self.__getitem__(ix)
        roi.curve_plot_item.setPen(width=2)
        self.unhighlight_curve(self.previous_index)
        self.previous_index = ix

    def unhighlight_curve(self, ix):
        if ix == -1:
            return
        roi = self.__getitem__(ix)
        roi.curve_plot_item.setPen(width=1)

    def slot_show_all_checkbox_clicked(self, b):
        if b:
            self._show_all_graphics_objects()
        else:
            self._hide_all_graphics_objects()
            ix = self.list_widget.currentRow()
            self._show_graphics_object(ix)

    def _show_graphics_object(self, ix):
        roi = self.__getitem__(ix)
        roi_graphics_object = roi.get_roi_graphics_object()
        roi_graphics_object.show()
        roi.curve_plot_item.show()

    def _hide_graphics_object(self, ix):
        roi = self.__getitem__(ix)
        roi_graphics_object = roi.get_roi_graphics_object()
        roi_graphics_object.hide()
        roi.curve_plot_item.hide()

    def _show_all_graphics_objects(self):
        for ix in range(self.__len__()):
            self._show_graphics_object(ix)

    def _hide_all_graphics_objects(self):
        for ix in range(self.__len__()):
            self._hide_graphics_object(ix)

    def _live_update_requested(self, ix: int):
        if self.roi_types == 'CNMFROI':
            raise TypeError

        self.vi.workEnv_changed('ROI Region')

        if not self.live_plot_checkbox.isChecked():
            return

        roi = self.__getitem__(ix)
        pg_roi = roi.get_roi_graphics_object

        self.set_pg_roi_plot(pg_roi, ix)

    def set_pg_roi_plot(self, pg_roi: pg.ROI, ix: int):
        image = self.vi.viewer.getProcessedImage()

        if image.ndim == 2:
            axes = (0, 1)
        elif image.ndim == 3:
            axes = (1, 2)
        else:
            return

        # Get the ROI region
        data = pg_roi.getArrayRegion((image.view(np.ndarray)), self.vi.viewer.imageItem, axes)

        if data is not None:
            while data.ndim > 1:
                data = data.mean(axis=1)
            if image.ndim == 3:
                # Set the curve
                roi = self.__getitem__(ix)

                roi.curve_plot_item.setData(y=data, x=self.vi.viewer.tVals)
                roi.curve_plot_item.setPen('w')
                roi.curve_plot_item.show()

    def slot_btn_set_tag(self):
        ix = self.current_index
        roi = self.__getitem__(ix)

        roi_def = self.list_widget_tags.currentItem().text().split(': ')[0]
        tag = self.line_edit_tag.text()

        roi.set_tag(roi_def, tag)

        self.list_widget_tags.currentItem().setText(roi_def + ': ' + tag)
        self.line_edit_tag.clear()

        n = self.list_widget_tags.count() - 1
        i = self.list_widget_tags.currentRow() + 1
        self.list_widget_tags.setCurrentRow(min(i, n))

    def get_tag(self, ix, roi_def):
        roi_def = self.list_widget_tags.currentItem().text().split[0]
        roi = self.__getitem__(ix)
        return roi.get_tag(roi_def)

    def get_all_tags(self, ix):
        roi = self.__getitem__(ix)
        return roi.get_all_tags()

    def set_list_widget_tags(self):
        self.list_widget_tags.clear()
        roi = self.__getitem__(self.current_index)
        tags_dict = roi.get_all_tags()

        roi_defs = sorted(tags_dict.keys())

        for roi_def in roi_defs:
            item = roi_def + ': ' + roi.get_tag(roi_def)
            self.list_widget_tags.addItem(item)

        if self.list_widget_tags.count() > 0:
            self.list_widget_tags.setCurrentRow(0)

    def update_roi_defs_from_configuration(self):
        roi_defs = configuration.proj_cfg.options('ROI_DEFS')

        for roi in self:
            tags_dict = roi.get_all_tags()
            for roi_def in roi_defs:
                if roi_def not in tags_dict.keys():
                    roi.set_tag(roi_def, tag='untagged')
        self.set_list_widget_tags()