#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#@author: kushal

#Chatzigeorgiou Group
#Sars International Centre for Marine Molecular Biology

#GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

from ..base import BasePlotWidget
from ...utils import *
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.console import ConsoleWidget
from ....common.configuration import console_history_path
from ....common.qdialogs import *
from matplotlib.axes import Axes
from matplotlib.patches import Polygon, Patch
from typing import *
import tifffile
import os
import pandas as pd
from ....analysis import Transmission
from .control_widget import Ui_Controls


class ControlDock(QtWidgets.QDockWidget):
    sig_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_Controls()
        self.ui.setupUi(self)

        self.widget_registry = WidgetRegistry()

        self.ui.cmap_img.set_cmap('inferno')
        self.ui.cmap_patches.set_cmap('tab10')

        self.widget_registry.register(self.ui.combo_categorical_column,
                                      setter=self.ui.combo_categorical_column.setText,
                                      getter=self.ui.combo_categorical_column.currentText,
                                      name='categorical_column')

        self.widget_registry.register(self.ui.cmap_img,
                                      setter=self.ui.cmap_img.set_cmap,
                                      getter=self.ui.cmap_img.get_cmap,
                                      name='cmap_img')

        self.widget_registry.register(self.ui.cmap_patches,
                                      setter=self.ui.cmap_patches.set_cmap,
                                      getter=self.ui.cmap_patches.get_cmap,
                                      name='cmap_patches')

        self.widget_registry.register(self.ui.radioButtonMax,
                                      setter=self.ui.radioButtonMax.setChecked,
                                      getter=self.ui.radioButtonMax.isChecked,
                                      name='max_projection')

        self.widget_registry.register(self.ui.radioButtonStd,
                                      setter=self.ui.radioButtonStd.setChecked,
                                      getter=self.ui.radioButtonStd.isChecked,
                                      name='std_projection')

        self.widget_registry.register(self.ui.list_widget_samples,
                                      setter=lambda l: self.ui.list_widget_samples.setSelectedItems(l),
                                      getter=lambda: [self.ui.list_widget_samples.currentItem().text()],
                                      name='selected_sample')

        self.widget_registry.register(self.ui.checkBoxFill,
                                      setter=self.ui.checkBoxFill.setChecked,
                                      getter=self.ui.checkBoxFill.isChecked,
                                      name='fill_patches')

        self.widget_registry.register(self.ui.doubleSpinBoxLineWidth,
                                      setter=self.ui.doubleSpinBoxLineWidth.setValue,
                                      getter=self.ui.doubleSpinBoxLineWidth.value,
                                      name='line_width')

        self.widget_registry.register(self.ui.doubleSpinBoxAlpha,
                                      setter=self.ui.doubleSpinBoxAlpha.setValue,
                                      getter=self.ui.doubleSpinBoxAlpha.value,
                                      name='alpha')

        self.ui.combo_categorical_column.currentTextChanged.connect(self.sig_changed)
        self.ui.cmap_img.currentItemChanged.connect(self.sig_changed)
        self.ui.cmap_patches.currentItemChanged.connect(self.sig_changed)
        self.ui.radioButtonMax.clicked.connect(self.sig_changed)
        self.ui.radioButtonStd.clicked.connect(self.sig_changed)
        self.ui.checkBoxFill.clicked.connect(self.sig_changed)
        self.ui.doubleSpinBoxLineWidth.valueChanged.connect(self.sig_changed)
        self.ui.doubleSpinBoxAlpha.valueChanged.connect(self.sig_changed)
        self.ui.list_widget_samples.currentItemChanged.connect(self.sig_changed)

    def fill_widget(self, samples: list, categorical_columns: list):
        self.ui.combo_categorical_column.setItems(categorical_columns)
        self.ui.list_widget_samples.setItems(samples)

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
        self.control_widget.sig_changed.connect(lambda: self.update_plot())

        self.update_live = self.control_widget.ui.checkBoxLiveUpdate.isChecked()
        self.control_widget.ui.checkBoxLiveUpdate.toggled.connect(self.set_update_live)

        self.control_widget.ui.pushButtonUpdatePlot.clicked.connect(self.update_plot)

        self.control_widget.ui.pushButtonSave.clicked.connect(self.save_plot_dialog)
        self.control_widget.ui.pushButtonLoad.clicked.connect(self.open_plot_dialog)

        self.control_widget.ui.groupBox.setVisible(False)

        cmd_history_file = os.path.join(console_history_path, 'space_map.pik')

        ns = {'this': self,
              'get_plot': lambda: self.plot,
              }

        txt = ["Namespaces",
               "self as 'this'",
               "Useful callable: get_plot()"
               ]

        txt = "\n".join(txt)

        self.console = ConsoleWidget(parent=self, namespace=ns, text=txt, historyFile=cmd_history_file)

        self.dockConsole = QtWidgets.QDockWidget(self)
        self.dockConsole.setWindowTitle('Console')
        self.dockConsole.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.dockConsole)

        self.block_signals_list = [self.control_widget]

        self.error_label = self.plot.error_label
        self.exception_holder = None
        self.error_label.mousePressEvent = self.show_exception_info

        self.sample_df = None  #: sub-dataframe of the current sample

        self.img: np.ndarray = np.empty(0)
        self.control_widget.ui.verticalSliderZLevel.valueChanged.connect(self._update_img)
        self.previous_sample_id: str = None

    def set_update_live(self, b: bool):
        self.control_widget.ui.checkBoxLiveUpdate.setChecked(b)
        self.update_live = b

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        """Set the input transmission"""
        if (self._transmission is None) or self.update_live:
            super(SpaceMapWidget, self).set_input(transmission)
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        samples = list(self.transmission.df['SampleID'].unique())
        self.control_widget.fill_widget(samples=samples, categorical_columns=categorical_columns)

    @exceptions_label('error_label', 'exception_holder', 'Error while setting data', 'Make sure you have selected appropriate columns')
    def update_plot(self, *args, **kwargs):
        self.plot.clear()
        self.error_label.clear()

        plot_opts = self.control_widget.widget_registry.get_state()

        if plot_opts['max_projection']:
            projection = 'max'
        elif plot_opts['std_projection']:
            projection = 'std'

        sample_id = plot_opts['selected_sample'][0]

        self.plot.ax.set_title(sample_id)

        self.sample_df = self.transmission.df[self.transmission.df['SampleID'] == sample_id]

        self.img = self.load_image(projection)

        if self.img.ndim > 2:
            self.control_widget.ui.groupBox.setVisible(True)
            self.control_widget.ui.verticalSliderZLevel.setMaximum(self.img.shape[0])
            self.control_widget.ui.spinBoxZLevel.setMaximum(self.img.shape[0])
            # self.control_widget.ui.spinBoxZLevel.setValue(0)
            if self.previous_sample_id == sample_id:
                self._update_img(
                    self.control_widget.ui.verticalSliderZLevel.value()
                )
            else:
                self.control_widget.ui.verticalSliderZLevel.setValue(0)
                self._update_img(0)
                self.previous_sample_id = sample_id
        else:
            self.control_widget.ui.groupBox.setVisible(False)
            self._update_img()

    def _update_img(self, zlevel: int = 0):
        self.plot.ax.cla()
        plot_opts = self.control_widget.widget_registry.get_state()

        categorical_column = plot_opts['categorical_column']

        if len(plot_opts['selected_sample']) < 1:
            raise ValueError('No Sample selected')

        cmap_img = plot_opts['cmap_img']
        cmap_patches = plot_opts['cmap_patches']
        fill_patches = plot_opts['fill_patches']
        line_width = plot_opts['line_width']
        alpha = plot_opts['alpha']

        labels = self.sample_df[categorical_column]
        cmap_labels = get_colormap(labels=labels.unique(), cmap=cmap_patches)

        if self.img.ndim > 2:
            vmax = np.nanmedian(self.img[zlevel, :, :]) + (10 * np.nanstd(self.img))
            self.plot.ax.imshow(
                self.img[zlevel, :, :].transpose(1, 0),
                origin='lower',cmap
                =cmap_img,
                vmax=vmax
            )
        else:
            vmax = np.nanmedian(self.img) + (10 * np.nanstd(self.img))
            self.plot.ax.imshow(self.img.transpose(1, 0), origin='lower', cmap=cmap_img, vmax=vmax)

        for ix, r in self.sample_df.iterrows():
            roi = r['ROI_State']

            if roi['roi_type'] == 'VolMultiCNMFROI':
                if not roi['zcenter'] == zlevel:
                    continue

            if roi['roi_type'] == 'VolCNMF':
                coors3d = roi['coors'][zlevel]
                current_coors = coors3d[~np.isnan(coors3d).any(axis=1)]
                if not current_coors.size > 0:  # roi not visible in current plane
                    continue

                xs = current_coors[:, 1].flatten().astype(int)
                ys = current_coors[:, 0].flatten().astype(int)
            else:
                xs = roi['roi_xs']
                ys = roi['roi_ys']

            cors = np.dstack([xs, ys])[0]
            label = r[categorical_column]

            poly = Polygon(cors, fill=fill_patches, color=cmap_labels[label], linewidth=line_width, alpha=alpha)

            self.plot.ax.add_patch(poly)

        handles = [Patch(color=cmap_labels[k], label=k) for k in cmap_labels.keys()]
        self.plot.ax.legend(handles=handles, ncol=int(np.sqrt(len(handles))), loc='lower right', title=categorical_column)

        self.plot.fig.tight_layout()

        self.plot.draw()

    def load_image(self, projection: str):
        img_uuid = self.sample_df['ImgUUID'].iloc[0]
        sample_id = self.sample_df['SampleID'].iloc[0]

        if isinstance(img_uuid, pd.Series):
            img_uuid = img_uuid.item()

        if not isinstance(img_uuid, str):
            raise ValueError('Datatype for Projection Path must be pandas.Series or str, it is currently : ' + str(
                type(img_uuid)))

        # see if data are 3D
        if os.path.isfile(
            os.path.join(self.transmission.get_proj_path(), 'images', f'{sample_id}-_-{img_uuid}_max_proj-0.tiff')
        ):
            z = 0
            imgs = []
            while True:
                img_path = os.path.join(self.transmission.get_proj_path(), 'images', f'{sample_id}-_-{img_uuid}_{projection}_proj-{z}.tiff')
                if os.path.isfile(img_path):
                    imgs.append(tifffile.TiffFile(img_path).asarray())
                    z += 1
                else:
                    break

            img = np.stack(imgs)
        else:
            img_path = os.path.join(self.transmission.get_proj_path(), 'images', f'{sample_id}-_-{img_uuid}_{projection}_proj.tiff')
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
