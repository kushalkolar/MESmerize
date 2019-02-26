from .common import *
from sklearn import cluster as skcluster


class KMeans(CtrlNode):
    """KMeans clustering\nhttps://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html\n
    Output column -> _KMEANS_CLUSTER_<data_column>"""
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

                  ('Apply', 'check', {'checked': True, 'applyBox': True})
                  ]

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

        self.t.df[output_column] = self.kmeans.labels_

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
    Output column -> _AGG_CLUSTER_<data_column>"""
    nodeName = 'Agglomerative'
    uiTemplate = [('n_clusters', 'intSpin',
                   {'min': 2, 'max': 999, 'step': 1, 'value': 2,
                    'toolTip': 'The number of clusters to find.'}),

                  ('affinity', 'combo',
                   {'items': ['euclidean', 'l1', 'l2', 'manhattan', 'cosine', 'precomputed'],
                    'tooltip': 'Metric used to compute the linkage.\n'
                               'Can be “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, or ‘precomputed’.'
                               '\nIf linkage is “ward”, only “euclidean” is accepted'}),

                  ('connectivity_matrix', 'combo',
                   {'toolTip': 'Dataframe column containing a connectivity matrix.\n'
                               'Defines for each sample the neighboring samples following a given structure of the data.\n'
                               'This can be a connectivity matrix itself or a callable that transforms the data\n'
                               'into a connectivity matrix, such as derived from kneighbors_graph.\n'
                               'Default is None, i.e, the hierarchical clustering algorithm is unstructured.'}),

                  ('compute_full_tree', 'combo',
                   {'items': ['auto', 'True', 'False'],
                    'toolTip': 'Stop early the construction of the tree at n_clusters.'
                               '\nThis is useful to decrease computation time if the number of clusters is not small compared to the number of samples.\n'
                               'This option is useful only when specifying a connectivity matrix.\n'
                               'Note also that when varying the number of clusters and using caching, it may be advantageous to compute the full tree.'}),

                  ('linkage', 'combo',
                   {'items': ['ward', 'complete', 'average', 'single'],
                    'toolTIp': 'The linkage criterion determines which distance to use between sets of observation.'
                               '\nThe algorithm will merge the pairs of cluster that minimize this criterion.'
                               '\nward minimizes the variance of the clusters being merged.\n'
                               'average uses the average of the distances of each observation of the two sets.\n'
                               'complete or maximum linkage uses the maximum distances between all observations of the two sets.\n'
                               'single uses the minimum of the distances between all observations of the two sets.'})

                  ]

    def processData(self, transmission: Transmission):
        columns = transmission.df.columns
        self.ctrls['data_column'].setItems(columns.to_list())
        self.ctrls['connectivity_matrix'].setItems(['None'] + columns.to_list())
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        n_clusters = self.ctrls['n_clusters'].value()
        affinity = self.ctrls['affinity'].currentText()

        connectivity_matrix = self.ctrls['connectivity_matrix'].currentText()
        if connectivity_matrix == 'None':
            connectivity_matrix = None
            connectivity_matrix_col = None
        else:
            connectivity_matrix_col = connectivity_matrix
            connectivity_matrix = np.vstack(self.t.df[connectivity_matrix_col].values)

        compute_full_tree = self.ctrls['compute_full_tree'].isChecked()
        if compute_full_tree == 'True':
            compute_full_tree = True
        elif compute_full_tree == 'False':
            compute_full_tree = False

        linkage = self.ctrls['linkage'].currentText()
        data_column = self.ctrls['data_column'].currentText()
        output_column = '_AGG_CLUSTER_' + data_column

        data = np.vstack(self.t.df['data_column'].values)

        self.clustering = skcluster.AgglomerativeClustering(n_clusters=n_clusters, affinity=affinity,
                                                            connectivity=connectivity_matrix,
                                                            compute_full_tree=compute_full_tree, linkage=linkage)

        self.clustering.fit(data)

        self.t.df[output_column] = self.clustering.labels_
        self.t.src.append({'Agglomerative Clustering':
                               {'data_column': data_column,
                                'n_clusters': n_clusters,
                                'affinity': affinity,
                                'connectivity_matrix_column': connectivity_matrix_col,
                                'compute_full_tree': compute_full_tree,
                                'linkage': linkage
                                }
                           })

        return self.t
