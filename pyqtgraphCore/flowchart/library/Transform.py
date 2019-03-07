# -*- coding: utf-8 -*-
from sklearn import manifold
import pandas as pd
import numpy as np
from .common import *


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


class Decomposition(CtrlNode):
    """Decomposition methods for dimensionality reduction"""
    pass
