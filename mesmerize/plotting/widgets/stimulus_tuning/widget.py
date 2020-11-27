# -*- coding: utf-8 -*-
# from . import functions
import numpy as np
import pandas as pd
from ..base import BasePlotWidget
from ...utils import WidgetRegistry, get_colormap
from ....analysis import Transmission
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....pyqtgraphCore.graphicsItems.ScatterPlotItem import ScatterPlotItem
from ..datapoint_tracer import DatapointTracerWidget
from matplotlib.axes import Axes
from .control_widget import *
from ....pyqtgraphCore.widgets.ComboBox import ComboBox
from math import ceil
from itertools import product as iter_product
from tqdm import tqdm
from ....common.qdialogs import *
from uuid import UUID
from collections import OrderedDict


def tonumeric(s: str):
    try:
        if float(s).is_integer():
            return int(s)
        else:
            return float(s)
    except:
        return False


def get_tuning_curves(
        curve: np.ndarray,
        stim_maps: dict,
        method: str = 'mean',
        start_offset: int = 0,
        end_offset: int = 0,
        include_unlabelled: bool = False,
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
    d = OrderedDict.fromkeys(
        [f"TUNE_CURVE_{k}_xlabels" for k in stim_maps.keys()] +   # used for the tuning curve
        [f"_TUNE_CURVE_{k}_yvals" for k in stim_maps.keys()] +
        [f"TUNE_MAX_{k}" for k in stim_maps.keys()] +  # used for stimulus at argmax(tuning_curve)
        [f"TUNE_MIN_{k}" for k in stim_maps.keys()]    # used for stimulus at argmin(tuning_curve)
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
        if not include_unlabelled:
            all_stimuli = all_stimuli[all_stimuli != "None"]

        ln = [tonumeric(v) for v in all_stimuli if tonumeric(v) is not False]
        ls = [v for v in all_stimuli if tonumeric(v) is False]
        ln.sort()
        ls.sort()
        all_stimuli = np.array(ls + ln, dtype=np.dtype('<U32'))

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
        d[f"TUNE_CURVE_{stim_type}_xlabels"] = xs
        d[f"_TUNE_CURVE_{stim_type}_yvals"] = ys

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

        self.ui.comboBox_method.setItems(
            ['mean', 'median', 'max', 'min']
        )

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
            self.ui.checkBoxIncludeUnlabelled,
            setter=self.ui.checkBoxIncludeUnlabelled.setChecked,
            getter=self.ui.checkBoxIncludeUnlabelled.isChecked,
            name='include_unlabelled'
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
        self.ui.comboBox_DPT_column.setItems(data_columns)

    def get_state(self) -> dict:
        return self.widget_registry.get_state()

    def set_state(self, state: dict):
        self.widget_registry.set_state(state)


class PlotArea(MatplotlibWidget):
    def __init__(self, parent):
        MatplotlibWidget.__init__(self)
        self.axs: Axes = None  #: array of axis objects used for drawing the means plots, shape is [nrows, ncols]
        self.setParent(parent)
        self.ncols = 2
        self.nrows: int = None  # determined at plot time

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

        stim_types = list(tuning_curves.keys())

        if len(stim_types) == 1:
            self.ncols = 1
        elif len(stim_types) < 5:
            self.ncols = 2
        else:
            self.ncols = 3

        self.nrows = ceil(len(tuning_curves.keys()) / self.ncols)

        self.axs = self.fig.subplots(self.nrows, self.ncols)
        self.fig.tight_layout()

        for i, plot_ix in enumerate(
                iter_product(range(self.nrows), range(self.ncols))
        ):
            if not i < len(stim_types):
                break

            stim_type = stim_types[i]
            data = tuning_curves[stim_type]

            if len(stim_types) == 1:
                plot = self.axs
            else:
                plot = self.axs[plot_ix]

            plot.plot(data[0], data[1], c='k')
            plot.set_xlabel(stim_type)
            plot.set_ylabel(f"{y_units} response")

        self.draw()

    def clear(self):
        self.fig.clear()


class TuningCurvesWidget(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []
    sig_output_changed = QtCore.pyqtSignal(Transmission)  #: Emits output Transmission containing tuning curves data

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)

        self.setWindowTitle('Tuning Curve Plots')

        self.plot = PlotArea(parent=self)
        self.setCentralWidget(self.plot)

        self.control_widget = ControlDock(self)
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self.control_widget
        )

        self.control_widget.sig_params_changed.connect(self.update_tuning_curves)

        self.sample_id = None
        self.roi_uuid = None

        self.roi_uuid_map: dict = None

        self.control_widget.sig_sample_changed.connect(self.set_rois_widget)
        self.control_widget.sig_roi_changed.connect(self.update_plot)

        self.control_widget.ui.pushButton_save.clicked.connect(self.save_plot_dialog)

        self.datapoint_tracer = DatapointTracerWidget()

        self.datapoint_tracer_dockwidget = QtWidgets.QDockWidget(parent=self)
        self.datapoint_tracer_dockwidget.setWidget(self.datapoint_tracer)
        self.addDockWidget(
            QtCore.Qt.RightDockWidgetArea,
            self.datapoint_tracer_dockwidget
        )

        # combobox so user can choose which stims to display using colored regions

        # create hlayout
        hlayout_datapoint_tracer_stimulus_options = QtWidgets.QHBoxLayout()
        # qlabel
        datapoint_tracer_stimulus_options_qlabel = QtWidgets.QLabel(
            self.datapoint_tracer.ui.groupBoxImageViewAndCurve
        )
        datapoint_tracer_stimulus_options_qlabel.setText(
            'Illustrate stimulus type: '
        )

        # combobox
        self.datapoint_tracer_stimulus_options_combobox = ComboBox(
            self.datapoint_tracer.ui.groupBoxImageViewAndCurve
        )
        # add them to the hlayout
        hlayout_datapoint_tracer_stimulus_options.addWidget(
            datapoint_tracer_stimulus_options_qlabel
        )
        hlayout_datapoint_tracer_stimulus_options.addWidget(
            self.datapoint_tracer_stimulus_options_combobox
        )
        self.datapoint_tracer_stimulus_options_combobox.currentTextChanged.connect(
            self.set_datapoint_tracer_stimulus_regions
        )
        # add hlayout under the curve plot
        self.datapoint_tracer.ui.verticalLayout_groupBoxImageViewAndCurve.addLayout(
            hlayout_datapoint_tracer_stimulus_options
        )

        # datapoint tracer curve plot legend for stimulus region colors
        self.legend = self.datapoint_tracer.ui.graphicsViewPlot.plotItem.addLegend()
        self.legend.setParentItem(
            self.datapoint_tracer.ui.graphicsViewPlot.getPlotItem()
        )
        self.color_legend_items = []
        self.pseudo_plots = []

        self.current_stim_region_plot: str = None

        self.update_live = True

    def update_tuning_curves(self, params: dict):
        data_column = params['data_column']
        method = params['method']
        start_offset = params['start_offset']
        end_offset = params['end_offset']

        tqdm().pandas()

        self.transmission.df[
                    [f"TUNE_CURVE_{s}_xlabels" for s in self.transmission.STIM_DEFS] +
                    [f"_TUNE_CURVE_{s}_yvals" for s in self.transmission.STIM_DEFS] +
                    [f"TUNE_MAX_{s}" for s in self.transmission.STIM_DEFS] +
                    [f"TUNE_MIN_{s}" for s in self.transmission.STIM_DEFS]
                 ] = \
            self.transmission.df.progress_apply(
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
            self.plot.clear()

            # set the stimulus options for visualizing them as colored regions
            self.datapoint_tracer_stimulus_options_combobox.setItems(
                self.transmission.STIM_DEFS
            )

    @BasePlotWidget.signal_blocker
    def set_rois_widget(self, sample_id):
        self.plot.clear()

        self.sample_id = sample_id
        roi_uuids = \
            self.transmission.df[
                self.transmission.df['SampleID'] == self.sample_id
            ].uuid_curve.unique().tolist()

        # user friendly integer map to the ROIs
        self.roi_uuid_map = dict(
            zip(
                map(str, range(len(roi_uuids))),
                roi_uuids
            )
        )

        self.control_widget.ui.listWidget_rois.clear()
        self.control_widget.ui.listWidget_rois.setItems(self.roi_uuid_map.keys())
        self.current_stim_region_plot = None

    @BasePlotWidget.signal_blocker
    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        samples = list(self.transmission.df['SampleID'].unique())
        self.control_widget.fill_widget(samples=samples, data_columns=data_columns)

    @present_exceptions(
        'Plot error',
        'Plot error. Make sure you have selected appropriate data columns and parameters'
    )
    def update_plot(self, *args, **kwargs):
        roi_ix = self.control_widget.ui.listWidget_rois.currentItem().text()
        uuid_curve = self.roi_uuid_map[roi_ix]

        r = self.transmission.df[
            self.transmission.df['uuid_curve'] == uuid_curve
        ]

        # get the tuning curves for all stims
        # pass it as a x-y list
        tuning_curves = \
            {
                s: [
                    r[f"TUNE_CURVE_{s}_xlabels"].item(),
                    r[f"_TUNE_CURVE_{s}_yvals"].item()
                ] for s in self.transmission.STIM_DEFS
            }

        # curve made using mean response, or max response etc.
        y_units = self.get_plot_opts()['method']

        self.plot.set_plots(tuning_curves, y_units)

        block_id = r._BLOCK_
        if isinstance(block_id, pd.Series):
            block_id = block_id.item()
        h = self.transmission.history_trace.get_data_block_history(block_id)

        dpt_column = self.control_widget.ui.comboBox_DPT_column.currentText()

        # self.datapoint_tracer.peak_region.clear_all()

        # TODO: Use the TimelineLinearRegion.add_linear_region to add
        #       stimulus period illustrations for all stimuli types
        #       Have some way to get a legend for the colors

        self.datapoint_tracer.set_widget(
            datapoint_uuid=UUID(uuid_curve),
            data_column_curve=dpt_column,
            row=r,
            proj_path=self.transmission.get_proj_path(),
            history_trace=h,
            clear_linear_regions=False
        )

        self.set_datapoint_tracer_stimulus_regions()

    def set_datapoint_tracer_stimulus_regions(self):
        selected_stim_type = self.datapoint_tracer_stimulus_options_combobox.currentText()

        # don't redraw
        if self.current_stim_region_plot == selected_stim_type:
            return

        self.current_stim_region_plot = selected_stim_type

        roi_ix = self.control_widget.ui.listWidget_rois.currentItem().text()
        uuid_curve = self.roi_uuid_map[roi_ix]

        r = self.transmission.df[
            self.transmission.df['uuid_curve'] == uuid_curve
            ]

        stim_df = r['stim_maps'].item()[0][0][selected_stim_type].sort_values(by='start')

        stims = stim_df.name.unique().astype(str)

        if stims.size < 10:
            _cm = 'tab10'
        elif stims.size > 20:
            _cm = 'hsv'
        else:
            _cm = 'tab20'

        cmap = get_colormap(stims, _cm, output='pyqt')

        self.datapoint_tracer.peak_region.clear_all()

        region_samples = dict()

        for ix, stim_period in stim_df.iterrows():
            start = stim_period['start']
            end = stim_period['end']
            color = cmap[stim_period['name']]

            region = self.datapoint_tracer.peak_region.add_linear_region(
                start, end, color
            )

            if stim_period['name'] not in region_samples.keys():
                region_samples[stim_period['name']] = region

        self.clear_legend()

        for k in cmap.keys():
            p = ScatterPlotItem()
            p.setData(x=[0], y=[0], brush=cmap[k], symbol='s')
            self.color_legend_items.append(k)
            self.legend.addItem(p, k)
            self.pseudo_plots.append(p)

    def clear_legend(self):
        """Clear the legend"""
        for i in range(len(self.pseudo_plots)):
            del self.pseudo_plots[0]

        for name in self.color_legend_items:
            self.legend.removeItem(name)
        self.color_legend_items.clear()

    def send_output_transmission(self):
        """Send output Transmission containing cluster labels"""
        params = self.get_plot_opts()

        t = self.transmission.copy()
        t.history_trace.add_operation('all', operation='tuning_curves', parameters=params)

        self.sig_output_changed.emit(t)

    def save_plot(self, path):
        t = self.transmission.copy()

        params = self.get_plot_opts()

        self.transmission.history_trace.add_operation('all', operation='tuning_curves', parameters=params)
        super(TuningCurvesWidget, self).save_plot(path)

        self.transmission = t

    def set_update_live(self, b: bool):
        pass

    def get_plot_opts(self, drop: bool = False) -> dict:
        return self.control_widget.get_state()

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        # it will try to set the roi index without
        # any Sample having been selected
        try:
            self.control_widget.set_state(opts)
        except AttributeError:
            pass
