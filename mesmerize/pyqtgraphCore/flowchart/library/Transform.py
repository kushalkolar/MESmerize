# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sklearn import manifold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn import decomposition
from .common import *
from ....analysis import organize_dataframe_columns
import pandas as pd
from ....plotting import NeuralDecomposePlot


class Manifold(CtrlNode):
    """Manifold learning"""
    nodeName = 'Manifold'
    uiTemplate = [('data_column', 'combo', {}),

                  ('method', 'combo', {'items': ['Isomap', 'Locally Linear Embedding',
                                                 'Spectral Embedding', 'MDS']}),

                  ('n_components', 'intSpin', {'max': 3, 'min': 2, 'value': 2, 'step': 1}),

                  ('kwargs', 'kwargTextEdit', {'placeHolder': 'Any additional kwargs to pass to'
                                                              'the sklearn.manifold function'}),

                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        method = self.ctrls['method'].currentText()
        n_components = self.ctrls['n_components'].value()
        kwargs = self.ctrls['kwargs'].get_kwargs()

        output_column = '_MANIFOLD'

        data = np.vstack(self.t.df[self.data_column].values)

        T = self._get_transform(method, data, n_components, kwargs)
        self.t.df[output_column] = T.tolist()

        params = {'data_column': self.data_column,
                  'method': method,
                  'n_components': n_components,
                  'kwargs': kwargs
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='manifold', parameters=params)
        self.t.last_output = output_column

        return self.t

    def _get_transform(self, method: str, data: np.ndarray, n_components: int, kwargs: dict):
        if method == 'Isomap':
            return manifold.Isomap(n_components=n_components, **kwargs).fit_transform(data)

        elif method == 'Locally Linear Embedding':
            return manifold.LocallyLinearEmbedding(n_components=n_components, **kwargs).fit_transform(data)

        elif method == 'Spectral Embedding':
            return manifold.SpectralEmbedding(n_components=n_components, **kwargs).fit_transform(data)

        elif method == 'MDS':
            return manifold.MDS(n_components=n_components, **kwargs).fit_transform(data)


class LDA(CtrlNode):
    """Linear Discriminant Analysis, uses sklearn"""
    nodeName = "LDA"
    uiTemplate = [('train_data', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection,
                                                 'toolTip': 'Column containing the training data'}),
                  ('train_labels', 'combo', {'toolTip': 'Column containing training labels'}),
                  ('solver', 'combo', {'items': ['svd', 'lsqr', 'eigen']}),
                  ('shrinkage', 'combo', {'items': ['None', 'auto', 'value']}),
                  ('shrinkage_val', 'doubleSpin', {'min': 0.0, 'max': 1.0, 'step': 0.1, 'value': 0.5}),
                  ('n_components', 'intSpin', {'min': 2, 'max': 1000, 'step': 1, 'value': 2}),
                  ('tol', 'intSpin', {'min': -50, 'max': 0, 'step': 1, 'value': -4}),
                  ('score', 'lineEdit', {}),
                  ('predict_on', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection,
                                                 'toolTip': 'Data column of the input "predict" Transmission\n'
                                                            'that is used for predicting from the model'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'train': {'io': 'in'},
                                                 'predict': {'io': 'in'},

                                                 'T': {'io': 'out'},
                                                 'coef': {'io': 'out'},
                                                 'means': {'io': 'out'},
                                                 'predicted': {'io': 'out'}
                                                 },
                          **kwargs)
        self.ctrls['score'].setReadOnly(True)

    def process(self, **kwargs):
        return self.processData(**kwargs)

    def processData(self, train: Transmission, predict: Transmission):
        self.t = train.copy()  #: Transmisison instance containing the training data with the labels
        if predict is not None:
            self.to_predict = predict.copy()  #: Transmission instance containing the data to predict after fitting on the the training data

        dcols, ccols, ucols = organize_dataframe_columns(self.t.df.columns)

        self.ctrls['train_data'].setItems(dcols)
        self.ctrls['train_labels'].setItems(ccols)

        if predict is not None:
            pdcols, ccols, ucols = organize_dataframe_columns(self.to_predict.df.columns)
            self.ctrls['predict_on'].setItems(pdcols)

        if not self.apply_checked():
            return

        train_columns = self.ctrls['train_data'].getSelectedItems()
        labels = self.ctrls['train_labels'].currentText()

        solver = self.ctrls['solver'].currentText()

        shrinkage = self.ctrls['shrinkage'].currentText()
        if shrinkage == 'value':
            shrinkage = self.ctrls['shrinkage_val'].value()
        elif shrinkage == 'None':
            shrinkage = None

        n_components = self.ctrls['n_components'].value()
        tol = 10 ** self.ctrls['tol'].value()

        store_covariance = True if solver == 'svd' else False

        params = {'train_data': train_columns,
                  'train_labels': labels,
                  'solver': solver,
                  'shrinkage': shrinkage,
                  'n_components': n_components,
                  'tol': tol,
                  'store_covariance': store_covariance
                  }

        kwargs = params.copy()
        kwargs.pop('train_data')
        kwargs.pop('train_labels')
        self.lda = LinearDiscriminantAnalysis(**kwargs)

        # Make an array of all the data from the selected columns
        self.X = np.hstack([np.vstack(self.t.df[train_column]) for train_column in train_columns])
        self.y = self.t.df[labels]

        self.X_ = self.lda.fit_transform(self.X, self.y)

        self.t.df['_LDA_TRANSFORM'] = self.X_.tolist()
        self.t.df['_LDA_TRANSFORM'] = self.t.df['_LDA_TRANSFORM'].apply(np.array)

        params.update({'score': self.lda.score(self.X, self.y),
                       'classes': self.lda.classes_.tolist()
                       })

        self.ctrls['score'].setText(f"{params['score']:.4f}")

        self.t.history_trace.add_operation('all', 'lda', params)

        self.t.df['_LDA_DFUNC'] = self.lda.decision_function(self.X).tolist()

        coef_df = pd.DataFrame({'classes': self.lda.classes_, '_COEF': self.lda.coef_.tolist()})
        t_coef = Transmission(df=coef_df, history_trace=self.t.history_trace)

        means_df = pd.DataFrame({'classes': self.lda.classes_, '_MEANS': self.lda.means_.tolist()})
        t_means = Transmission(df=means_df, history_trace=self.t.history_trace)

        out = {'T': self.t, 'coef': t_coef, 'means': t_means, 'predicted': None}

        # Predict using the trained model
        predict_columns = self.ctrls['predict_on'].getSelectedItems()

        if not predict_columns:
            return out

        if predict_columns != train_columns:
            QtWidgets.QMessageBox.warning('Predict and Train columns do not match',
                                          'The selected train and predict columns are different')

        predict_data = np.hstack([np.vstack(self.to_predict.df[predict_column]) for predict_column in predict_columns])
        self.to_predict.df['LDA_PREDICTED_LABELS'] = self.lda.predict(predict_data)
        self.to_predict.df['_LDA_TRANSFORM'] = self.lda.transform(predict_data).tolist()
        self.to_predict.df['_LDA_TRANSFORM'] = self.to_predict.df['_LDA_TRANSFORM'].apply(np.array)

        params_predict = params.copy()
        params_predict.update({'predict_columns': predict_columns})

        self.to_predict.history_trace.add_operation('all', 'lda-predict', params_predict)

        out.update({'predicted': self.to_predict})

        return out


class PCA(CtrlNode):
    """Principal component analysis. Uses sklearn.decomposition.PCA"""
    nodeName = 'PCA'
    uiTemplate = [('data_column', 'combo', {}),

                  ('n_components', 'intSpin', {'min': 2, 'max': 999, 'value': 2, 'step': 1}),

                  ('whiten', 'check', {'chcked': False}),

                  ('svd_solver', 'combo', {'items': ['auto', 'full', 'arpack', 'randomized']}),

                  ('tol', 'doubleSpin', {'min': 0.0, 'max': 999.0, 'value': 0, 'step': 0.05}),

                  ('iterated_power', 'intSpin', {'min': -1, 'max': 999, 'value': -1, 'step': 1,
                                                 'toolTip': 'If value is -1 then iterated power is set to "auto"'}),
                  ('exp_var', 'lineEdit', {'readOnly': True, 'toolTip': 'Variance explained by each component'}),

                  ('exp_var_p', 'lineEdit', {'readOnly': True,
                                             'toolTip': 'Percentage of variance explained by each component'}),

                  ('sing_vals', 'lineEdit', {'readOnly': True, 'toolTip': 'Singular values for each component'}),

                  ('Apply', 'check', {'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_PCA_TRANSFORM'

        n_components = self.ctrls['n_components'].value()
        whiten = self.ctrls['whiten'].isChecked()
        svd_solver = self.ctrls['svd_solver'].currentText()
        tol = self.ctrls['tol'].value()
        iterated_power = self.ctrls['iterated_power'].value()
        if iterated_power == -1:
            iterated_power = 'auto'

        params = {'n_components': n_components,
                  'whiten': whiten,
                  'svd_solver': svd_solver,
                  'tol': tol,
                  iterated_power: iterated_power
                  }

        pca = decomposition.PCA(n_components=n_components, whiten=whiten, svd_solver=svd_solver, tol=tol,
                                iterated_power=iterated_power)

        self.X = np.vstack(self.t.df[self.data_column].values)

        self.X_ = pca.fit_transform(self.X)

        exp_var = pca.explained_variance_
        exp_var_p = pca.explained_variance_ratio_

        params.update({**params,
                       'exp_var': exp_var,
                       'exp_var_p': exp_var_p
                       })

        self.t.df[output_column] = self.X_.tolist()
        self.t.df[output_column] = self.t.df['_PCA_TRANSFORM'].apply(np.array)

        self.t.history_trace.add_operation('all', 'pca', params)

        self.ctrls['exp_var'].setText(str(exp_var))
        self.ctrls['exp_var_p'].setText(str(exp_var_p))
        self.ctrls['sing_vals'].setText(str(pca.singular_values_))

        return self.t


class NeuralDynamics(CtrlNode):
    """Dimensionality reduction of neuronal dynamics"""
    nodeName = 'NeuralDynamics'
    uiTemplate = [('ShowGUI', 'button', {'text': 'Show GUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.widget = NeuralDecomposePlot()
        self.ctrls['ShowGUI'].clicked.connect(self.widget.show)

    def process(self, output_transmission=False, **kwargs):
        self.processData(**kwargs)

    def processData(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)
        self.t = Transmission.merge(self.transmissions_list)
        self.widget.set_input(self.t)
        return None
