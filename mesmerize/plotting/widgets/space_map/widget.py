#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#@author: kushal

#Chatzigeorgiou Group
#Sars International Centre for Marine Molecular Biology

#GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

from ..base import BasePlotWidget
from ...utils import *
from ....pyqtgraphCore.widgets.ComboBox import ComboBox
from ....pyqtgraphCore.widgets.ListWidget import ListWidget
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.console import ConsoleWidget
from ....common.configuration import console_history_path
from ....common.qdialogs import *
from matplotlib.axes import Axes
from matplotlib.patches import Polygon
from typing import *
import tifffile
import os
import pandas as pd
from ....analysis import Transmission, organize_dataframe_columns


class ControlDock(QtWidgets.QDockWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.vlayout = QtWidgets.QVBoxLayout()

        self.widget_registry = WidgetRegistry()

        label_categorical_column = QtWidgets.QLabel(self)
        label_categorical_column.setText('Categorical Label')
        label_categorical_column.setMaximumHeight(30)
        self.vlayout.addWidget(label_categorical_column)

        self.combo_categorical_column = ComboBox(self)
        self.combo_categorical_column.setMaximumHeight(30)
        self.combo_categorical_column.currentTextChanged.connect(self.sig_changed)
        self.widget_registry.register(self.combo_categorical_column,
                                      setter=self.combo_categorical_column.setText,
                                      getter=self.combo_categorical_column.currentText,
                                      name='categorical_column')
        self.vlayout.addWidget(self.combo_categorical_column)

        self.cmap_img_label = QtWidgets.QLabel(self)
        self.cmap_img_label.setText('Colormap ')
        self.cmap_img_label.setMaximumHeight(30)
        self.vlayout.addWidget(self.cmap_img_label)

        self.cmap_img = ColormapListWidget(self)
        self.cmap_img.set_cmap('jet')
        self.cmap_img.currentRowChanged.connect(self.sig_changed)
        self.cmap_img.setMaximumHeight(150)
        self.widget_registry.register(self.cmap_img,
                                      setter=self.cmap_img.set_cmap,
                                      getter=self.cmap_img.get_cmap,
                                      name='cmap_img')
        self.vlayout.addWidget(self.cmap_img)

        self.cmap_patches_label = QtWidgets.QLabel(self)
        self.cmap_patches_label.setText('Colormap ')
        self.cmap_patches_label.setMaximumHeight(30)
        self.vlayout.addWidget(self.cmap_patches_label)

        self.cmap_patches = ColormapListWidget(self)
        self.cmap_patches.set_cmap('tab10')
        self.cmap_patches.currentRowChanged.connect(self.sig_changed)
        self.cmap_patches.setMaximumHeight(150)
        self.widget_registry.register(self.cmap_patches,
                                      setter=self.cmap_patches.set_cmap,
                                      getter=self.cmap_patches.get_cmap,
                                      name='cmap_patches')
        self.vlayout.addWidget(self.cmap_patches)

        label_projection = QtWidgets.QLabel(self)
        label_projection.setText('Projection')
        label_projection.setMaximumHeight(30)
        self.vlayout.addWidget(label_projection)

        self.combo_projection = ComboBox(self)
        self.combo_projection.setMaximumHeight(30)
        self.combo_projection.currentTextChanged.connect(self.sig_changed)
        self.combo_projection.setItems(['max', 'std'])
        self.widget_registry.register(self.combo_projection,
                                      setter=self.combo_projection.setText,
                                      getter=self.combo_projection.currentText,
                                      name='projection')
        self.vlayout.addWidget(self.combo_projection)

        self.btn_update_plot = QtWidgets.QPushButton(self)
        self.btn_update_plot.setText('Update Plot')
        self.btn_update_plot.setMaximumHeight(30)
        self.btn_update_plot.clicked.connect(self.sig_changed)
        self.vlayout.addWidget(self.btn_update_plot)

        label_samples_list = QtWidgets.QLabel(self)
        label_samples_list.setText('Samples')
        label_samples_list.setMaximumHeight(30)
        self.vlayout.addWidget(label_samples_list)

        self.list_widget_samples = ListWidget(self)
        self.list_widget_samples.currentItemChanged.connect(self.sig_changed)
        self.widget_registry.register(self.list_widget_samples,
                                      setter=self.list_widget_samples.setSelectedItems,
                                      getter=self.list_widget_samples.getSelectedItems,
                                      name='selected_sample')
        self.vlayout.addWidget(self.list_widget_samples)

    def get_state(self) -> dict:
        return self.widget_registry.get_state()

    def set_state(self, state: dict):
        self.widget_registry.set_state(state)


class PlotArea(MatplotlibWidget):
    def __init__(self):
        MatplotlibWidget.__init__(self)
        self.error_label = QtWidgets.QLabel(self)
        self.error_label.setMaximumHeight(32)
        self.vbox.addWidget(self.error_label)
        self._ax = None

    @property
    def ax(self) -> Axes:
        if self._ax is None:
            raise ValueError('Axes not set')

        return self._ax

    def clear(self):
        self.fig.clear()
        self._ax = self.fig.add_subplot(111)


class SpaceMapWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)

        self.setWindowTitle('Space Map Plot')

        self.plot = PlotArea()
        self.setCentralWidget(self.plot)

        self.control_widget = ControlDock(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.control_widget)
        self.control_widget.sig_changed.connect(self.update_plot)
        self.control_widget.ui.pushButtonUpdatePlot.clicked.connect(lambda: self.update_plot())

        cmd_history_file = os.path.join(console_history_path, 'space_map.pik')

        ns = {'this': self,
              'plot': self.plot,
              }

        txt = ["Namespaces",
               "self as 'this'",
               ]

        txt = "\n".join(txt)

        self.console = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)

        self.block_signals_list = [self.control_widget]

        self.error_label = self.plot.error_label
        self.exception_holder = None
        self.error_label.mousePressEvent.connect(self.show_exception_info)

        self.sample_df = None

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        pass

    @exceptions_label('error_label', 'exception_holder', 'Error while setting data', 'Make sure you have selected appropriate columns')
    def update_plot(self, *args, **kwargs):
        opts = self.get_plot_opts()

        categorical_column = opts['categorical_column']
        sample_id = opts['selected_sample'][0]
        projection = opts['projection']
        cmap_img = opts['cmap_img']
        cmap_patches = opts['cmap_patches']

        self.sample_df = self.transmission.df[self.transmission.df['SampleID'] == sample_id]
        labels = self.sample_df[categorical_column]
        cmap = get_colormap(labels=labels.unique(), cmap=cmap_patches)

        img = self.load_image(projection)

        self.plot.clear()
        self.plot.ax.imshow(img.transpose(1, 0), origin='lower', cmap=cmap_img)

        for ix, r in self.sample_df.iterrows():
            roi = r['ROI_State']
            xs = roi['roi_xs']
            ys = roi['roi_ys']

            cors = np.dstack([xs, ys])[0]
            label = r[categorical_column]

            poly = Polygon(cors, fill=False, color=cmap[label], alpha=0.6)

            self.plot.ax.add_patch(poly)

    def load_image(self, projection: str):
        img_uuid = self.sample_df['ImgUUID'].iloc[0]

        if isinstance(img_uuid, pd.Series):
            img_uuid = img_uuid.item()

        if not isinstance(img_uuid, str):
            raise ValueError('Datatype for Projection Path must be pandas.Series or str, it is currently : ' + str(
                type(img_uuid)))

        if projection == 'max':
            suffix = '_max_proj.tiff'
        elif projection == 'std':
            suffix = '_std_proj.tiff'
        else:
            raise ValueError('Can only accept "max" and "std" arguments')

        img_path = os.path.join(self.proj_path, 'images', f'{self.sample_id}-_-{img_uuid}{suffix}')

        img = tifffile.TiffFile(img_path).asarray()
        return img

    @BasePlotWidget.signal_blocker
    def set_update_live(self, b: bool):
        pass

    def get_plot_opts(self, drop: bool = False) -> dict:
        return self.control_widget.get_state()

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        self.control_widget.set_state(opts)

    def show_exception_info(self, mouse_press_ev):
        if self.exception_holder is not None:
            QtWidgets.QMessageBox.warning(self, *self.exception_holder)
