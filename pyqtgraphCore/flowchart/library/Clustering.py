from .common import *
from sklearn import cluster as skcluster


class KMeans(CtrlNode):
    """KMeans clustering\nhttps://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html\n
    Output column -> _KMEANS_CLUSTER_LABEL_<data_column>"""
    nodeName = "KMeans"
    uiTemplate = [('n_clusters', 'intSpin',
                        {'max': 100, 'min': 2, 'value': 2, 'step': 1,
                         'toolTip': 'The number of clusters to form as well as the number of centroids to generate.'}),

                  ('n_init', 'intSpin',
                        {'max': 100, 'min': 1, 'value': 10, 'step': 10,
                         'toolTip': 'Number of time the k-means algorithm will be run with different centroid seeds.\n'
                                    'The final results will be the best output of n_init consecutive runs in terms '
                                    'of inertia.'}),

                  ('max_iter', 'intSpin',
                        {'max': 10000, 'min': 1, 'value': 300, 'step': 50,
                         'toolTip': 'Maximum number of iterations of the k-means algorithm for a single run.'}),

                  ('tol', 'doubleSpin',
                        {'max': 1.0, 'min': 0.0000001, 'step': 0.000001, 'value': 0.0001,
                            'toolTip': 'Relative tolerance with regards to inertia to declare convergence'}),

                  ('precompute_distances', 'combo',
                        {'items': ['auto', 'True', 'False']}),

                  ('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': True, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        n_clusters = self.ctrls['n_clusters'].value()
        n_init = self.ctrls['n_init'].value()
        max_iter = self.ctrls['max_iter'].value()
        tol = self.ctrls['tol'].value()
        precompute_distances = self.ctrls['precompute_distances'].currentText()

        if precompute_distances == 'True':
            precompute_distances = True
        elif precompute_distances == 'False':
            precompute_distances = False

        data_column = self.ctrls['data_column'].currentText()
        self.data = np.vstack(self.t.df[data_column].values)

        output_column = '_KMEANS_CLUSTER_LABEL_' + data_column

        self.kmeans = skcluster.KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, tol=tol,
                                  precompute_distances=precompute_distances)


        self.kmeans.fit(self.data)

        cluster_labels = self.kmeans.labels_

        self.t.df[output_column] = cluster_labels

        self.t.src.append({'KMeans':
                               {'data_column': data_column,
                                'n_init': n_init,
                                'max_iter': max_iter,
                                'tol': tol,
                                'precompute_distances': precompute_distances}})

        return self.t


class Agglomerative(CtrlNode):
    """Recursively merges the pair of clusters that minimally increases a given linkage distance.\n
    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html\n
    Output column -> _AGG_CLUSTER_LABEL_<data_column>"""
    nodeName = 'Agglomerative'
