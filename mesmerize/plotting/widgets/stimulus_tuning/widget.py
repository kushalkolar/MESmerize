# -*- coding: utf-8 -*-
# from . import functions
import numpy as np
import pandas as pd
from ..base import BasePlotWidget
from ...utils import WidgetRegistry
from ....analysis import Transmission
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ..datapoint_tracer import DatapointTracerWidget
from matplotlib.axes import Axes
from .control_widget import *
from ....pyqtgraphCore.widgets.ComboBox import ComboBox
from math import ceil
from itertools import product as iter_product
from typing import *
from tqdm import tqdm_pandas
from ....common.qdialogs import *


def get_tuning_curves(
        curve: np.ndarray,
        stim_maps: dict,
        method: str = 'mean',
        start_offset: int = 0,
        end_offset: int = 0
) -> pd.Series:
    """
    Returns a pandas series with tuning curves for all stimuli for a single curve

    :param curve: curve to create tuning curves from
    :param stim_maps: dict of stimulus maps
    :param method: stats method, such as "mean", "max", "median", etc.
    :param method_assign_stim: assign the "TUNE_<stim_name>" label according to min or max
    :param start_offset: start offset (in frames) for stimulus period extraction
    :param end_offset: end offset (in frames) for stimulus period extraction
    :return: pandas series:
                Tuning curves for each stimulus type are: "_TUNE_CURVE_<stim_name>" entries.
                "TUNE_<stim_name>" is assigned as the stimulus with the
                min or max value in the tuning curve

    """
    # empty output dict
    d = dict.fromkeys(
        [f"_TUNE_CURVE_{k}" for k in stim_maps.keys()] +   # used for the tuning curve
        [f"TUNE_MAX_{k}" for k in stim_maps.keys()] + # used for stimulus at argmax(tuning_curve)
        [f"TUNE_MIN_{k}" for k in stim_maps.keys()]   # used for stimulus at argmin(tuning_curve)
    )

    # each stimulus datafame
    for stim_type in stim_maps.keys():
        stim_df = stim_maps[stim_type]  # get the stimulus dataframe

        # stimulus names will be stored as str with max length 32 char
        stim_array = np.empty(curve.size, dtype=np.dtype('<U32'))
        stim_array[:] = "None"

        # fill stim_array
        # stim_array is used for fancy indexing of `curve`
        # to extract the curve values during the various
        # stimuli
        for ix, r in stim_df.iterrows():  # iterate through the stimulus periods
            # apply any offsets
            start_ix = r['start'] + start_offset
            end_ix = r['end'] + end_offset

            # add this stimulus period to the stim_array
            stim_array[int(start_ix):int(end_ix)] = str(r['name'])  # store stim name as str

        # instantiate lists for the tuning curves
        all_stimuli = np.unique(stim_array)  # [stim_array != ''])
        xs = np.empty(all_stimuli.size, dtype=np.dtype('<U32'))
        #         xs = []
        ys = np.empty(all_stimuli.size)

        # create the tuning curves
        for i, stimulus in enumerate(all_stimuli):
            xs[i] = stimulus  # stimulus name

            # get ALL the y values from the curve where
            # this specific stimulus is present
            y = curve[stim_array == stimulus]

            # get the mean, or max, etc. for the stimulus period
            ys[i] = getattr(np, method)(y)

        #         xs.append("None")
        #         ys.append(curve[np.isnan(stim_array)].mean())

        # the tuning curve
        d[f"_TUNE_CURVE_{stim_type}"] = np.hstack([xs, ys])

        # stimulus name at argmax() and argmin() of tuning curve
        d[f"TUNE_MAX_{stim_type}"] = xs[np.argmax(ys)]
        d[f"TUNE_MIN_{stim_type}"] = xs[np.argmin(ys)]

    return pd.Series(d)


class ControlDock(QtWidgets.QDockWidget):
    sig_sample_changed = QtCore.pyqtSignal(str)
    sig_roi_changed = QtCore.pyqtSignal(str)
    sig_params_changed = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_ControlsDock()
        self.ui.setupUi(self)

        self.widget_registry = WidgetRegistry()

        self.widget_registry.register(
            self.ui.comboBox_data_column,
            setter=self.ui.comboBox_data_column.setText,
            getter=self.ui.comboBox_data_column.currentText,
            name='data_column'
        )

        self.widget_registry.register(
            self.ui.comboBox_method,
            setter=self.ui.comboBox_method.setText,
            getter=self.ui.comboBox_method.currentText,
            name='method'
        )

        self.widget_registry.register(
            self.ui.spinBox_start_offset,
            setter=self.ui.spinBox_start_offset.setValue,
            getter=self.ui.spinBox_start_offset.value,
            name='start_offset',
        )

        self.widget_registry.register(
            self.ui.spinBox_end_offset,
            setter=self.ui.spinBox_end_offset.setValue,
            getter=self.ui.spinBox_end_offset.value,
            name='end_offset',
        )

        self.widget_registry.register(
            self.ui.comboBox_DPT_column,
            setter=self.ui.comboBox_DPT_column.setText,
            getter=self.ui.comboBox_DPT_column.currentText,
            name='dpt_column'
        )

        self.widget_registry.register(
            self.ui.listWidget_samples,
            setter=lambda l: self.ui.listWidget_samples.setSelectedItems(l),
            getter=lambda: [self.ui.listWidget_samples.currentItem().text()],
            name='sample_id'
        )

        self.widget_registry.register(
            self.ui.listWidget_rois,
            setter=lambda l: self.ui.listWidget_rois.setSelectedItems(l),
            getter=lambda: [self.ui.listWidget_rois.currentItem().text()],
            name='roi_ix'
        )

        self.ui.pushButton_set.clicked.connect(self._emit_data)

        self.ui.listWidget_samples.currentTextChanged.connect(self.sig_sample_changed.emit)
        self.ui.listWidget_rois.currentTextChanged.connect(self.sig_roi_changed.emit)

    def _emit_data(self):
        self.sig_params_changed.emit(
            self.widget_registry.get_state()
        )

    def fill_widget(self, samples: list, data_columns: list):
        self.ui.comboBox_data_column.setItems(data_columns)
        self.ui.listWidget_samples.setItems(samples)

    def get_state(self) -> dict:
        return self.widget_registry.get_state()

    def set_state(self, state: dict):
        self.widget_registry.set_state(state)


class PlotArea(MatplotlibWidget):
    def __init__(self, parent):
        MatplotlibWidget.__init__(self)
        self.axs = None  #: array of axis objects used for drawing the means plots, shape is [nrows, ncols]
        self.setParent(parent)
        self.ncols = 2
        self.nrows = None

    def set_plots(
            self,
            tuning_curves: Dict[str, np.ndarray],
            y_units: List[str]
    ):
        """
        Set the subplots

        :param input_arrays: padded input arrays (2D),  shape is [num_samples, padded_peak_curve_length]
        :param n_clusters: number of clusters
        :param y_pred: cluster predictions (labels)
        :param xzero_pos: set the zero position as the 'zero' position of the input array or the 'maxima' of the input array
        :param error_band: Type of error band to show, one of either 'ci' or 'std'
        """
        self.clear()
        self.nrows = ceil(len(tuning_curves.keys()) / self.ncols)

        self.axs = self.fig.subplots(self.nrows, self.ncols)
        self.fig.tight_layout()

        for stim_type, plot_ix in zip(
                tuning_curves.keys(),
                iter_product(range(self.nrows), range(self.ncols))
        ):
            data = tuning_curves[stim_type]
            self.axs[plot_ix].plot(data[0], data[1])
            #         axs[plot_ix].

            self.axs[plot_ix].set_xlabel(stim_type)
            self.axs[plot_ix].set_ylabel(f"{y_units} response")

        self.draw()

    def clear(self):
        self.fig.clear()
        self._ax = self.fig.add_subplot(111)


class TuningCurvesWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []
    sig_output_changed = QtCore.pyqtSignal(Transmission)  #: Emits output Transmission containing tuning curves data

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)

        self.setWindowTitle('Tuning Curve Plots')

        self.plot = PlotArea()
        self.setCentralWidget(self.plot)

        self.control_widget = ControlDock(self)
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self.control_widget
        )

        self.control_widget.sig_sample_changed.connect(self.update_plot)
        self.control_widget.sig_params_changed.connect(self.update_tuning_curves)

        self.sample_id = None
        self.roi_uuid = None

        self.roi_uuid_map = None

        self.control_widget.sig_sample_changed.connect(self.set_rois_widget)
        self.control_widget.sig_roi_changed.connect(self.update_plot)

        self.control_widget.ui.pushButton_save.clicked.connect(self.save_plot_dialog)

    def update_tuning_curves(self, params: dict):
        data_column = params['data_column']
        method = params['method']
        start_offset = params['start_offset']
        end_offset = params['end_offset']

        tqdm_pandas()

        self.t.df[
                    [f"_TUNE_CURVE_{s}" for s in self.transmission.STIM_DEFS] + \
                    [f"TUNE_MAX_{s}" for s in self.transmission.STIM_DEFS] + \
                    [f"TUNE_MIN_{s}" for s in self.transmission.STIM_DEFS]
                 ] = \
            self.t.df.progress_apply(
                lambda r: get_tuning_curves(
                    curve=r[data_column],
                    stim_maps=r['stim_maps'][0][0],
                    method=method,
                    start_offset=start_offset,
                    end_offset=end_offset
                ), axis=1
            )

        self.send_output_transmission()

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        """Set the input transmission"""
        if (self._transmission is None) or self.update_live:
            super(TuningCurvesWidget, self).set_input(transmission)
            self.update_plot()

    @BasePlotWidget.signal_blocker
    def set_rois_widget(self, sample_id):
        self.plot.clear()

        self.sample_id = sample_id
        roi_uuids = self.transmission.df[self.sample_id].uuid_curve.unique().tolist()

        # user friendly integer map to the ROIs
        self.roi_uuid_map = dict(
            zip(
                map(str, range(len(roi_uuids))),
                roi_uuids
            )
        )

        self.control_widget.ui.listWidget_rois.clear()
        self.control_widget.ui.listWidget_rois.setItems(self.roi_uuid_map.keys())

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        samples = list(self.transmission.df['SampleID'].unique())
        self.control_widget.fill_widget(samples=samples, data_columns=data_columns)

    @present_exceptions(
        'Plot error',
        'Plot error. Make sure you have selected appropriate data columns and parameters'
    )
    def update_plot(self, *args, **kwargs):
        roi_ix = self.get_plot_opts()['roi_ix']
        uuid_curve = self.roi_uuid_map[roi_ix]

        r = self.transmission[self.transmission['uuid_curve'] == uuid_curve]

        # get the tuning curves for all stims
        tuning_curves = \
            {
                s: r[f"_TUNE_CURVE_{s}"] for s in self.transmission.STIM_DEFS
            }

        # curve made using mean response, or max response etc.
        y_units = self.get_plot_opts()['method']

        self.plot.set_plots(tuning_curves, y_units)

    def send_output_transmission(self):
        """Send output Transmission containing cluster labels"""
        params = self.get_plot_opts()

        t = self.transmission.copy()
        t.history_trace.add_operation('all', operation='tuning_curves', parameters=params)

        self.sig_output_changed.emit(t)

    def set_update_live(self, b: bool):
        pass

    def get_plot_opts(self, drop: bool = False) -> dict:
        return self.control_widget.get_state()

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        self.control_widget.set_state(opts)
