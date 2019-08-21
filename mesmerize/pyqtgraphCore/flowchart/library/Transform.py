# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sklearn import manifold
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from .common import *
from ....analysis import organize_dataframe_columns
import pandas as pd

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
    nodedName = "LDA"
    uiTemplate = [('data_columns', 'list_widget', {'selection_mode': QtWidgets.QAbstractItemView.ExtendedSelection}),
                  ('labels', 'combo', {}),
                  ('solver', 'combo', {'items': ['svd', 'lsqr', 'eigen']}),
                  ('shrinkage', 'combo', {'items': ['None', 'auto', 'value']}),
                  ('shrinkage_val', 'doubleSpin', {'min': 0.0, 'max': 1.0, 'step': 0.1, 'value': 0.5}),
                  ('n_components', 'intSpin', {'min': 2, 'max': 1000, 'step': 1, 'value': 2}),
                  ('tol', 'int', {'min': -50, 'max': 0, 'step': 1, 'value': -4}),
                  ('Apply', 'check', {'applyBox': True, 'checked': True})
                  ]

    # def __init__(self, name, **kwargs):
    #     CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'},
    #                                              'T': {'io': 'out'},
    #                                              'W': {'io': 'out'},
    #                                              'means': {'io': 'out'},
    #                                              'dfunc': {'io': 'out'}
    #                                              },
    #                       **kwargs)

    # def process(self, **kwargs):
    #     return self.processData(**kwargs)

    def processData(self, transmission: Transmission):
        self.t = transmission.copy()

        dcols, ccols, ucols = organize_dataframe_columns(self.t.df.columns)

        self.ctrls['data_columns'].setItems(dcols)
        self.ctrls['labels'].setItems(ccols)

        if not self.apply_checked():
            return

        data_columns = self.ctrls['data_columns'].getSelectedItems()
        labels_column = self.ctrls['labels'].currentText()

        solver = self.ctrls['solver'].currentText()

        shrinkage = self.ctrls['shrinkage'].currentText()
        if shrinkage == 'value':
            shrinkage = self.ctrls['shrinkage_val'].value()
        elif shrinkage == 'None':
            shrinkage = None

        n_components = self.ctrls['n_components'].value()
        tol = 10 ** self.ctrls['tol'].value()

        store_covariance = True if solver == 'svd' else False

        params = {'data_columns': data_columns,
                  'solver': solver,
                  'shrinkage': shrinkage,
                  'n_components': n_components,
                  'tol': tol,
                  'store_covariance': store_covariance
                  }

        kwargs = params.copy().pop('data_columns')
        self.lda = LinearDiscriminantAnalysis(**kwargs)

        # Make an array of all the data from the selected columns
        self.X = np.hstack([np.vstack(self.t.df[data_column]) for data_column in data_columns])

        self.y = self.t.df[labels_column]

        self.X_ = self.lda.fit_transform(self.X, self.y)

        params.update({'score': self.lda.score(self.X, self.y), 'covariance': self.lda.covariance_.tolist()})

        self.t.df['_LDA_DFUNC'] = self.lda.decision_function(self.X).tolist()
        self.t.df['_LDA_COEF'] = self.lda.coef_.tolist()
        self.t.df['_LDA_MEANS'] = self.lda.means_.tolist()
        self.t.df['_LDA_CLASSES'] = self.lda.classes_.tolist()

        return self.t

class Decomposition(CtrlNode):
    """Decomposition methods for dimensionality reduction"""
    pass
