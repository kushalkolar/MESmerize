import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from ...utils import ColormapListWidget
from ..base import BasePlotWidget
from .controls import *
from ....common.qdialogs import present_exceptions

class LowDimData:
    def __init__(self):
        self.input_data: np.ndarray = np.empty(0)
        self.low_dim_data: np.ndarray = np.empty(0)

        self.labels: np.ndarray = np.empty(0, dtype='<U16')

        self.params: dict = None

        self.lda_means: np.ndarray = np.empty(0)
        self.lda_covariance: np.ndarray = np.empty(0)
        self.lda_decision_function: np.ndarray = np.empty(0)

        self.pca: PCA = None
        self.lda: LinearDiscriminantAnalysis = None

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
        
