# -*- coding: utf-8 -*-
from sklearn import manifold
import pandas as pd
import numpy as np
from .common import *


class Manifold(CtrlNode):
    """Manifold learning"""
    nodeName = 'Manifold'
    uiTemplate = [('method', 'combo', {'items': ['Isomap', 'Locally Linear Embedding',
                                                 'Spectral Embedding', 'MDS']}),
                  ('n_components', 'intSpin', {'max': 3, 'min': 2, 'value': 2, 'step': 1}),
                  ('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        data_column = self.ctrls['data_column'].currentText()

        n_components = self.ctrls['n_components'].value()

        method = self.ctrls['method'].currentText()

        data = np.vstack(self.t.df[data_column].values)

        output_column = '_TRANSFORM_' + data_column

        self.t.df[output_column] = self._get_transform(method, data, n_components)

        self.t.src.append({'Manifold': {'data_column': data_column, 'method': method, 'n_components': str(n_components)}})

        return self.t

    def _get_transform(self, method: str, data: np.ndarray, n_components: int):
        if method == 'Isomap':
            return manifold.Isomap(n_components=n_components).fit_transform(data)
        elif method == 'Locally Linear Embedding':
            return manifold.LocallyLinearEmbedding(n_components=n_components).fit_transform(data)
        elif method == 'Spectral Embedding':
            return manifold.SpectralEmbedding(n_components=n_components).fit_transform(data)
        elif method == 'MDS':
            return manifold.MDS(n_components=n_components).fit_transform(data)
