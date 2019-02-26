from .common import *
from sklearn import neighbors
from common.configuration import sys_cfg


class KneighborsGraph(CtrlNode):
    """Computes the (weighted) graph of k-Neighbors for points in data\n
    Output column -> _KNGRAPH_<data_column>"""
    nodeName = 'KneighborsGraph'
    uiTemplate = [('n_neighbors', 'intSpin',
                   {'max': 1000, 'min': 1, 'value': 2, 'step': 5,
                    'toolTip': 'Number of neighbors for each sample'}),

                  ('mode', 'combo', {'items': ['connectivity', 'distance'],
                                     'toolTip': '‘connectivity’ will return the connectivity matrix with ones and zeros'
                                                '\n‘distance’ will return the distances between neighbors according to the given metric'}),

                  ('metric', 'combo', {'items': ['euclidean', 'manhattan', 'chebyshev',
                                                 'minkowski', 'wminkowski', 'seuclidean', 'mahalanobis'],
                                       'toolTip': 'The distance metric used to calculate the k-Neighbors for each sample point.'
                                                  '\nThe DistanceMetric class gives a list of available metrics.\n'
                                                  'The default distance is ‘euclidean’ (‘minkowski’ metric with the p param equal to 2.)'}),

                  ('p', 'intSpin', {'min': 0, 'max': 100, 'value': 2, 'step': 1,
                                    'toolTip': 'Power parameter for the Minkowski metric.\n'
                                               'When p = 1, this is equivalent to using manhattan_distance (l1), and euclidean_distance (l2) for p = 2.\n'
                                               'For arbitrary p, minkowski_distance (l_p) is used.'}),

                  ('metric_params', 'kwargTextEdit',
                   {'placeHolder': 'additional keyword arguments for the metric function.'}),

                  ('include_self', 'check', {'toolTip': 'Mark each sample as the first nearest neighbor to itself.'}),

                  ('data_column', 'combo', {}),

                  ('Apply', 'check', {'checked': True, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        n_neighbors = self.ctrls['n_neighbors'].value()
        mode = self.ctrls['mode'].currentText()
        metric = self.ctrls['metric'].currentText()
        p = self.ctrls['p'].value()
        metric_params = self.ctrls['metric_params'].get_kwargs()
        include_self = self.ctrls['include_self'].isChecked()

        data_column = self.ctrls['data_column'].currentText()
        output_column = '_KNGRAPH_' + data_column

        data = self.t.df[data_column]

        kngraph = neighbors.kneighbors_graph(data, n_neighbors=n_neighbors, mode=mode, metric=metric,
                                             p=p, metric_params=metric_params, include_self=include_self,
                                             n_jobs=sys_cfg['HARDWARE']['n_processes'])
        kngraph_array = kngraph.toarray()

        self.t.df[output_column] = kngraph.tolist()
        self.t.src.append({'KneighborsGraph':
                               {'data_column': data_column,
                                'n_neigbors': n_neighbors,
                                'mode': mode,
                                'metric': metric
                                }
                           })

        return self.t