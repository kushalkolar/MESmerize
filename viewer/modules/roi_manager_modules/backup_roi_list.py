class ROIList(list):
    def __init__(self, ui, roi_types: str, viewer_interface: ViewerInterface):
        super(ROIList, self).__init__()

        self._size = 0
        self.highlighted_curve = -1

        assert isinstance(ui.listWidgetROIs, QtWidgets.QListWidget)
        self.list_widget = ui.listWidgetROIs
        self.list_widget.clear()
        self.list_widget.currentRowChanged.connect(self.set_index)
        # self.list_widget.currentItemChanged.connect(partial(self._list_widget__call_func_with_ix, self.set_tags_list_widget))

        assert isinstance(ui.listWidgetROITags, QtWidgets.QListWidget)
        self.list_widget_tags = ui.listWidgetROITags
        self.list_widget_tags.clear()

        self.roi_types = roi_types

        assert isinstance(ui.checkBoxLivePlot, QtWidgets.QCheckBox)
        self.live_plot_checkbox = ui.checkBoxLivePlot
        self.live_plot_checkbox.setChecked(False)
        if self.roi_types == 'ManualROI':
            self.live_plot_checkbox.setEnabled(True)
        elif self.roi_types == 'CNMFROI':
            self.live_plot_checkbox.setEnabled(False)

        assert isinstance(ui.checkBoxShowAll, QtWidgets.QCheckBox)
        self.show_all_checkbox = ui.checkBoxShowAll
        self.show_all_checkbox.setChecked(True)
        self.show_all_checkbox.clicked.connect(self.slot_show_all_clicked)

        self.vi = viewer_interface
        configuration.proj_cfg_changed.register(self.update_roi_defs_from_configuration)

    def append(self, roi: AbstractBaseROI):
        ix = int(self.__len__())
        self.list_widget.addItem(str(ix))
        roi.add_to_viewer()

        roi_graphics_object = roi.get_roi_graphics_object()

        if isinstance(roi_graphics_object, pg.ROI):
            roi_graphics_object.sigHoverEvent.connect(partial(self.set_index, ix))
            # roi_graphics_object.sigHoverEvent.connect(partial(self.highlight_roi, ix))
            # roi_graphics_object.sigHoverEvent.connect(partial(self.set_tags_list_widget, ix))
            roi_graphics_object.sigHoverEnd.connect(partial(self.unhighlight_curve, ix))
            roi_graphics_object.sigRemoveRequested.connect(partial(self.__delitem__, ix))
            roi_graphics_object.sigRegionChanged.connect(partial(self._live_update_requested, ix))

        self.vi.workEnv_changed('ROI Added')
        super(ROIList, self).append(roi)
        self._size += 1
        self.list_widget.setCurrentRow(self.__len__() - 1)

    def __delitem__(self, key):
        self.vi.workEnv_changed('ROI Removed')
        self.list_widget.takeItem(key)
        super(ROIList, self).__delitem__(key)

    def __len__(self):
        return self._size

    # def __getitem__(self, item) -> AbstractBaseROI:
    #     return super(ROIList, self).__getitem__(item)

    def set_index(self, ix):
        print('ix is: ' + str(ix) + ' type: ' + str(type(ix)))
        print('__len___ is :' + str(self.__len__()) + ' type: ' + str(type(self.__len__())))
        print('len(self) is: ' + str(len(self)) + ' type: ' + str(type(len(self))))
        if ix != self.list_widget.currentRow():
            self.list_widget.setCurrentRow(ix)
        self.highlight_curve(ix)
        self.highlight_roi(ix)

    def highlight_roi(self, ix: int):
        pass

    def highlight_curve(self, ix: int):
        roi = self[ix]
        roi.curve_plot_item.setPen(width=2)
        # self.unhighlight_curve(self.highlighted_curve)
        self.highlighted_curve = ix

    # def unhighlight_curve(self, ix):
    #     if ix == -1:
    #         return
    #     roi = self.__getitem__(ix)
    #     roi.curve_plot_item.setPen(width=1)

    def slot_show_all_clicked(self):
        if self.show_all_checkbox.isChecked:
            self._show_all_roi_and_curve_graphics_objects()
        else:
            self._hide_all_roi_and_curve_graphics_objects()
            ix = int(self.list_widget.currentItem().data(0))
            self._show_roi_and_curve_graphics_object(ix)

    def _show_roi_and_curve_graphics_object(self, ix):
        roi = self.__getitem__(ix)
        roi_graphics_object = roi.get_roi_graphics_object()
        roi_graphics_object.show()
        roi.curve_plot_item.show()

    def _show_all_roi_and_curve_graphics_objects(self):
        for roi in self:
            roi_graphics_object = roi.get_roi_graphics_object()
            roi_graphics_object.hide()
            roi.curve_plot_item.hide()

    def _hide_all_roi_and_curve_graphics_objects(self):
        for roi in self:
            roi_graphics_object = roi.get_roi_graphics_object()
            roi_graphics_object.show()
            roi.curve_plot_item.show()

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

    def set_tag(self, tag):
        ix = self.list_widget.currentRow()
        roi_def = self.list_widget_tags.curentItem.text().split[0]
        roi = self.__getitem__(ix)
        roi.set_tag(roi_def, tag)

    def get_tag(self, roi_def):
        ix = self.list_widget.currentRow()
        roi_def = self.list_widget_tags.curentItem.text().split[0]
        roi = self.__getitem__(ix)
        return roi.get_tag(roi_def)

    def get_all_tags(self, ix):
        if isinstance(ix, QtWidgets.QListWidgetItem):
            ix = int(ix.data(0))
        roi = self.__getitem__(ix)
        return roi.get_all_tags()

    # def set_tags_list_widget(self, ix):
    #     print(ix)
    #     print(type(ix))
    #     roi = self.__getitem__(ix)
    #     tags_dict = roi.get_all_tags()
        # for key in

    # def __iter__(self):


    def update_roi_defs_from_configuration(self):
        pass
    #     roi_defs = configuration.proj_cfg.options('ROI_DEFS')
    #     for roi in self:
    #         tags_dict = roi.get_all_tags