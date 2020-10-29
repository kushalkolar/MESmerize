import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from ...utils import ColormapListWidget
from ..base import BasePlotWidget
from .controls import *
from ....common.qdialogs import present_exceptions
from ....common import get_window_manager
from ....analysis import Transmission
from typing import *
from collections import OrderedDict
from traceback import format_exc


class LowDimData:
    def __init__(self):
        self.input_data: np.ndarray = np.empty(0)
        self.low_dim_data: np.ndarray = np.empty(0)

        self.labels: np.ndarray = np.empty(0, dtype='<U16')

        self.params: dict = None

        self.pca: PCA = None
        self.lda: LinearDiscriminantAnalysis = None
        
        self.lda_means: np.ndarray = np.empty(0)
        self.lda_covariance: np.ndarray = np.empty(0)
        self.lda_decision_function: np.ndarray = np.empty(0)

    def __del__(self):
        self.clear()

    def clear(self):  # in case the user does weird stuff in the console, should implement some forced garbage collection
        del self.input_data
        del self.low_dim_data

        del self.labels

        del self.params

        del self.pca
        del self.lda

        del self.lda_means
        del self.lda_covariance
        del self.lda_decision_function

        self.input_data: np.ndarray = np.empty(0)
        self.low_dim_data: np.ndarray = np.empty(0)

        self.labels: np.ndarray = np.empty(0, dtype='<U16')

        self.params: dict = None

        self.pca: PCA = None
        self.lda: LinearDiscriminantAnalysis = None

        self.lda_means: np.ndarray = np.empty(0)
        self.lda_covariance: np.ndarray = np.empty(0)
        self.lda_decision_function: np.ndarray = np.empty(0)

    def compute(
            self,
            sample_df: pd.DataFrame,
            data_column: str,
            stimulus_type: str,
            method: str,
            method_kwargs: dict = None,
            use_scaler: bool = False,
            scaler_method: str = None,
            stimulus_cmap: str = None,

    ):
        self.params = {
            'data_column': data_column,
            'stimulus_type': stimulus_type,
            'method': method,
            'method_kwargs': method_kwargs,
            'use_scaler': use_scaler,
            'scaler_method': scaler_method,
            'stimulus_cmap': stimulus_cmap
        }

        sample_df = sample_df.reset_index(drop=True)

        # Stimulus mapping dataframe
        stim_dataframe = sample_df.iloc[0]['stim_maps'][0][0][stimulus_type]

        # create an array where each frame is labelled with the stimulus name
        stim_labels = np.empty(
            shape=(sample_df[data_column].iloc[0].shape),  # shape is (n_frames,)
            dtype=f'<U{sample_df.name.apply(len).max()}'  # just unicode with length of longest stimulus name str
        )

        # fill the array so each frame is labelled with the stimulus name for that frame
        for i, s in stim_dataframe.sort_values(by=['start'], ascending=True).iterrows():
            stim_labels[int(s['start']):int(s['end'])] = s['name']

        self.input_data = np.vstack(sample_df[data_column].values).T

        if use_scaler:
            X = self.input_data
        else:
            scaler = getattr(preprocessing, scaler_method)
            X = scaler.fit_transform(self.input_data)

        if method == 'pca':
            self.pca = PCA(**method_kwargs)
            self.low_dim_data = self.pca.fit_transform(X)

        elif method == 'lda':
            if 'store_covariance' in self.params['method_kwargs'].keys():
                store_covariance = self.params['method_kwargs'].pop('method_kwargs')
            else:
                store_covariance = True if self.params['method_kwargs']['solver'] not in ['lsqr', 'eigen'] else False

            lda = LinearDiscriminantAnalysis(**method_kwargs, store_covariance=store_covariance)
            self.low_dim_data = lda.fit_transform(X, self.labels)

            self.lda_means = lda.means_
            self.lda_covariance = lda.covariance_
            self.lda_decision_function = lda.decision_function(X)

        return self

    def to_json_dict(self) -> dict:
        return \
            {
                'input_data': self.input_data.tolist(),
                'low_dim_data': self.low_dim_data.tolist(),
                'labels': self.labels.tolist(),
                'params': self.params,
                'lda_means': self.lda_means.tolist(),
                'lda_covariance': self.lda_covariance.tolist(),
                'lda_decision_function': self.lda_decision_function.tolist()
            }

    def from_json_dict(self, d: dict):
        for attr in d.keys():
            setattr(self, attr, d[attr])


class ControlDock(QtWidgets.QDockWidget):
    def __init__(self, parent):
        QtWidgets.QDockWidget.__init__(self, parent=parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.listWidgetStimulusColormap.set_cmap('tab10')

    @present_exceptions(
        'Cannot set params',
        'You probably have not formatted your method params correctly.\n'
        'They must be formatted as keyword arguments.'
    )
    def get_params(self) -> dict:
        _kwargs = self.ui.plainTextEditMethodParams.toPlainText()
        method_kwargs = eval(f"dict({_kwargs})")
        return \
            {
                'data_column': self.ui.comboBoxDataColumn.currentText(),
                'stimulus_type': self.ui.comboBoxStimulusMapping.currentText(),
                'method': self.ui.comboBoxMethod.currentText(),
                'method_kwargs': method_kwargs,
                'use_scaler': self.ui.checkBoxUsePreprocessScaler.isChecked(),
                'scaler_method': self.ui.comboBoxPreprocessScaler.currentText(),
                'stimulus_cmap': self.ui.listWidgetStimulusColormap.get_cmap()
            }


class NeuralDecomposePlot(QtWidgets.QMainWindow, BasePlotWidget):
    drop_opts = []

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        BasePlotWidget.__init__(self)

        self.setWindowTitle('Neural Activity Decomposition')

        self.control_widget = ControlDock()
        self.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self.control_widget
        )

        self.data: OrderedDict[LowDimData] = None

        self.control_widget.ui.pushButtonComputeAllSamples.clicked.connect(lambda: self.compute())

        self.control_widget.ui.listWidgetComputedSamples.currentRowChanged.connect(self.update_plot)

        self.viewer_window = None

    def set_input(self, transmission: Transmission):
        if self._transmission is not None:
            if QtWidgets.QMessageBox.warning(
                self,
                'Overwrite input?',
                'The input data to this plot node has changed.\n'
                'Do you want to load the new input data, this will clear all current data!'
            ) == QtWidgets.QMessageBox.No:
                return
            else:
                self.clear_data()

        super(NeuralDecomposePlot, self).set_input(transmission)
        self.control_widget.ui.comboBoxStimulusMapping.clear()
        self.control_widget.ui.comboBoxStimulusMapping.addItems(
            self.transmission.STIM_DEFS
        )

    def fill_control_widget(self, data_columns: list, categorical_columns: list, uuid_columns: list):
        self.control_widget.ui.comboBoxDataColumn.clear()
        self.control_widget.ui.comboBoxDataColumn.addItems(data_columns)

    @present_exceptions(
        'Error computing decomposition',
        'There is probably an issue with a sample(s) or your parameters'
    )
    @BasePlotWidget.signal_blocker
    def compute(self):
        if self.data is not None:
            self.clear_data()

        self.control_widget.ui.listWidgetComputedSamples.clear()

        self.data = OrderedDict()

        params = self.control_widget.get_params()
        samples = self.transmission.df['SampleID'].unique()
        n_samples = samples.size

        for i, sid in enumerate(samples):
            sample_df = self.transmission.df[self.transmission.df['SampleID'] == sid]

            try:
                self.data[sid] = LowDimData().compute(sample_df, **params)
            except:
                raise ValueError(
                    f'Exception encountered for the following sample:'
                    f'\n\t{sid}\n'
                    f'{format_exc()}'
                )

            self.control_widget.ui.progressBar.setValue(int(i / n_samples))

        self.control_widget.ui.listWidgetComputedSamples.addItems(
            samples.tolist()
        )

    def clear_data(self):
        for k in self.data.keys():
            del self.data[k]

        self.data = None

        self.control_widget.ui.listWidgetComputedSamples.clear()

    def open_viewer(self):
        """
        Open a sample in the viewer
        """
        if self.viewer_window is not None:
            self.viewer_window.vi.viewer
            self.viewer_window.close()

        w = get_window_manager().get_new_viewer_window()
        w.open_from_dataframe(proj_path=self.proj_path, row=self.row)

        self.viewer_window = w


    @present_exceptions('Plot error')
    def update_plot(self, *args, **kwargs):
        pass
