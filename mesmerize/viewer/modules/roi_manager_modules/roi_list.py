from functools import partial

import numpy as np
from PyQt5 import QtWidgets, QtGui
from matplotlib import cm as matplotlib_color_map

import pyqtgraphCore as pg
from viewer.core.common import ViewerInterface
from viewer.modules.roi_manager_modules.roi_types import BaseROI, ManualROI
from common import configuration

class ROIList(list):
    def __init__(self, ui, roi_types: str, viewer_interface: ViewerInterface):
        super(ROIList, self).__init__()

        assert isinstance(ui.listWidgetROIs, QtWidgets.QListWidget)
        self.list_widget = ui.listWidgetROIs
        self.list_widget.clear()
        self.list_widget.currentRowChanged.connect(self.set_current_index)

        # self.action_delete_roi = QtWidgets.QWidgetAction(ui.dockWidgetContents)
        # self.action_delete_roi.setText('Delete')
        # self.action_delete_roi.triggered.connect(partial(self.__delitem__, None))
        #
        # self._list_widget_context_menu = QtWidgets.QMenu(ui.dockWidgetContents)
        # self._list_widget_context_menu.addAction(self.action_delete_roi)
        #
        # self.list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.list_widget.customContextMenuRequested.connect(self._list_widget_context_menu_requested)

        assert isinstance(ui.listWidgetROITags, QtWidgets.QListWidget)
        self.list_widget_tags = ui.listWidgetROITags
        self.list_widget_tags.clear()

        self.roi_types = roi_types

        assert isinstance(ui.btnPlot, QtWidgets.QPushButton)
        self.btn_plot = ui.btnPlot
        self.btn_plot.clicked.connect(self.plot_manual_roi_regions)

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

        self.current_index = -1
        self.previous_index = -1

        configuration.project_manager.signal_project_config_changed.connect(self.update_roi_defs_from_configuration)

        # configuration.proj_cfg_changed.register(self.update_roi_defs_from_configuration)

    def append(self, roi: BaseROI):
        roi.add_to_viewer()

        roi_graphics_object = roi.get_roi_graphics_object()

        if isinstance(roi_graphics_object, tuple(pg.ROI.__subclasses__())):
            roi_graphics_object.sigHoverEvent.connect(partial(self.highlight_roi, roi))
            roi_graphics_object.sigHoverEnd.connect(roi.reset_color)
            roi_graphics_object.sigRemoveRequested.connect(partial(self.__delitem__, roi))
            roi_graphics_object.sigRegionChanged.connect(partial(self._live_update_requested, roi))

        self.vi.workEnv_changed('ROI Added')
        # item = QtWidgets.QListWidgetItem(self.list_widget)
        # item.setData(QtCore.Qt.UserRole, "<b>{0}</b>".format((self.__len__())))
        self.list_widget.addItem(str(self.__len__()))
        super(ROIList, self).append(roi)

    # def clear_all(self):
    #     self.list_widget.clear()
    #     self.list_widget_tags.clear()
    #     for ix in range(self.__len__()):
    #         roi = self.__getitem__(ix)
    #         roi.remove_from_viewer()

    # def set_pg_roi_graphics_state(self, ix, state):
    #     try:
    #         roi = self.__getitem__(ix)
    #     except IndexError:
    #         return
    #     pg_roi = roi.get_roi_graphics_object()
    #     pg_roi.setState(state)

    def clear_(self):
        self.list_widget.clear()
        self.list_widget_tags.clear()
        self.disconnect_all()
        for i in range(self.__len__()):
            self.vi.viewer.status_bar_label.showMessage('Removing ROIs #:' + str(i))
            self.__delitem__(0)

    def __delitem__(self, key):
        if isinstance(key, ManualROI):
            key = self.index(key)
        elif key is None:
            key = self.current_index
        if key == -1:
            return
        self.vi.workEnv_changed('ROI Removed')
        roi = self.__getitem__(key)
        roi.remove_from_viewer()
        super(ROIList, self).__delitem__(key)
        if self.__len__() == 0:
            self.list_widget.clear()
            self.list_widget_tags.clear()
            return

        self.list_widget.takeItem(key)
        self._reindex_list_widget()
        self.reindex_colormap()

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)


        # self.list_widget.setCurrentRow(-1)

            # self.list_widget.setCurrentRow(min(0, key - 1))
            # self._reindex_list_widget()
            # self.reindex_colormap()
            # self.set_list_widget_tags()

    # def __del__(self):
    #     pass

    def disconnect_all(self):
        self.list_widget.currentRowChanged.disconnect(self.set_current_index)
        # self.list_widget.customContextMenuRequested.disconnect(self._list_widget_context_menu_requested)
        # self.action_delete_roi.triggered.disconnect(self.__delitem__)
        self.btn_plot.clicked.disconnect(self.plot_manual_roi_regions)
        self.show_all_checkbox.toggled.disconnect(self.slot_show_all_checkbox_clicked)
        self.btn_set_tag.clicked.disconnect(self.slot_btn_set_tag)

    def _reindex_list_widget(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setText(str(i))

    def reindex_colormap(self):
        cm = matplotlib_color_map.get_cmap('hsv')
        cm._init()
        lut = (cm._lut * 255).view(np.ndarray)

        cm_ixs = np.linspace(0, 210, self.__len__(), dtype=int)

        for ix in range(self.__len__()):
            c = lut[cm_ixs[ix]]
            try:
                roi = self.__getitem__(ix)
            except IndexError:
                return
            item = self.list_widget.item(ix)
            if item is not None:
                item.setBackground(QtGui.QBrush(pg.mkBrush(c)))

            roi.set_original_color(c)
            roi.set_color(c)

    def __getitem__(self, item) -> BaseROI:
        return super(ROIList, self).__getitem__(item)

    def set_current_index(self, ix):
        if ix < 0:
            return
        if ix > self.__len__():
            return
        try:
            self.__getitem__(ix)
        except IndexError:
            return
        self.current_index = ix
        self.highlight_curve(ix)
        self.set_previous_index()
        if not self.show_all_checkbox.isChecked():
            self._hide_all_graphics_objects()
        self._show_graphics_object(ix)
        self.set_list_widget_tags()

    def highlight_roi(self, roi: QtWidgets.QGraphicsObject):
        ix = self.index(roi)
        self.highlight_curve(ix)
        self.list_widget.setCurrentRow(ix)

    def highlight_curve(self, ix: int):
        roi = self.__getitem__(ix)
        roi.set_color('w', width=2)

    def set_previous_index(self):
        if self.previous_index == -1:
            self.previous_index = self.current_index
            return
        if self.previous_index > self.__len__() - 1:
            self.previous_index = self.current_index
            return

        roi = self.__getitem__(self.previous_index)
        self.previous_index = self.current_index
        roi.reset_color()

    def slot_show_all_checkbox_clicked(self, b: bool):
        if b:
            self._show_all_graphics_objects()
        else:
            self._hide_all_graphics_objects()
            ix = self.list_widget.currentRow()
            self._show_graphics_object(ix)

    def _show_graphics_object(self, ix: int):
        try:
            roi = self.__getitem__(ix)
        except IndexError:
            return
        roi_graphics_object = roi.get_roi_graphics_object()
        roi_graphics_object.show()
        roi.curve_plot_item.show()

    def _hide_graphics_object(self, ix: int):
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

    def _live_update_requested(self, roi: BaseROI):
        ix = self.index(roi)
        if self.roi_types == 'CNMFROI':
            raise TypeError('Can only live update Manually drawn ROIs when they are moved')

        self.vi.workEnv_changed('ROI Region')

        if not self.live_plot_checkbox.isChecked():
            return

        self.set_pg_roi_plot(ix)

    def plot_manual_roi_regions(self):
        for ix in range(self.__len__()):
            roi = self.__getitem__(ix)
            pg_roi = roi.get_roi_graphics_object()
            self.set_pg_roi_plot(ix)
            roi.reset_color()
        if not self.show_all_checkbox.isChecked():
            self._hide_all_graphics_objects()
            self._show_graphics_object(self.current_index)

    def set_pg_roi_plot(self, ix: int):
        image = self.vi.viewer.getProcessedImage()

        if image.ndim == 2:
            axes = (0, 1)
        elif image.ndim == 3:
            axes = (1, 2)
        else:
            return
        self.vi.viewer.status_bar_label.showMessage('Please wait, calculating intensity values for ROI: ' + str(ix))

        # Get the ROI region
        pg_roi = self.__getitem__(ix).get_roi_graphics_object()
        data = pg_roi.getArrayRegion((image.view(np.ndarray)), self.vi.viewer.imageItem, axes)

        if data is not None:
            while data.ndim > 1:
                data = data.mean(axis=1)
            if image.ndim == 3:
                # Set the curve
                roi = self.__getitem__(ix)

                roi.curve_plot_item.setData(y=data, x=self.vi.viewer.tVals)
                roi.set_color('w', width=2)
                roi.curve_plot_item.show()
        self.vi.viewer.status_bar_label.clearMessage()

    def slot_btn_set_tag(self):
        ix = self.current_index
        try:
            roi = self.__getitem__(ix)
        except IndexError:
            return

        roi_def = self.list_widget_tags.currentItem().text().split(': ')[0]
        tag = self.line_edit_tag.text()

        roi.set_tag(roi_def, tag)

        self.list_widget_tags.currentItem().setText(roi_def + ': ' + tag)
        self.line_edit_tag.clear()

        n = self.list_widget_tags.count() - 1
        i = self.list_widget_tags.currentRow() + 1
        self.list_widget_tags.setCurrentRow(min(i, n))

    def get_tag(self, ix: int, roi_def: str) -> str:
        roi_def = self.list_widget_tags.currentItem().text().split[0]
        roi = self.__getitem__(ix)
        return roi.get_tag(roi_def)

    def get_all_tags(self, ix: int) -> dict:
        roi = self.__getitem__(ix)
        return roi.get_all_tags()

    def set_list_widget_tags(self):
        self.list_widget_tags.clear()
        ix = self.current_index
        try:
            roi = self.__getitem__(ix)
        except IndexError:
            return

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