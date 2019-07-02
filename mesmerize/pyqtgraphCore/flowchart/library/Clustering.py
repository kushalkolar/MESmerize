from .common import *
from sklearn import cluster as skcluster
from ....plotting.widgets import LDAPlot
from ....plotting.widgets import KShapeWidget
from scipy.stats import wasserstein_distance
from sklearn.metrics import pairwise_distances
from scipy.cluster import hierarchy

class KShape(CtrlNode):
    """k-Shape clustering"""
    nodeName = "KShape"
    uiTemplate = [('ShowGUI', 'button', {'text': 'ShowGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}, 'Out': {'io': 'out'}})
        self.kshape_widget = KShapeWidget(parent=None)
        self.kshape_widget.sig_output_changed.connect(lambda out: self.process(output_transmission=out))
        self.ctrls['ShowGUI'].clicked.connect(self.kshape_widget.show)

    def process(self, output_transmission=False, **kwargs):
        if output_transmission:
            out = output_transmission
        else:
            out = self.processData(**kwargs)

        return {'Out': out}

    def processData(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)
        self.t = Transmission.merge(self.transmissions_list)
        self.kshape_widget.set_input(self.t)
        return None


class KMeans(CtrlNode):
    """KMeans clustering\nhttps://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html\n
    Output column -> KMEANS_CLUSTER_<data_column>"""
    nodeName = "KMeans"
    uiTemplate = [('data_column', 'combo', {}),

                  ('n_clusters', 'intSpin',
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

                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

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

        self.data = np.vstack(self.t.df[self.data_column].values)

        output_column = 'KMEANS_CLUSTER_LABEL'

        self.kmeans = skcluster.KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter, tol=tol,
                                       precompute_distances=precompute_distances)

        self.kmeans.fit(self.data)

        self.t.df[output_column] = self.kmeans.labels_

        params = {'data_column': self.data_column,
                  'n_init': n_init,
                  'max_iter': max_iter,
                  'tol': tol,
                  'precompute_distances': precompute_distances}
        self.t.history_trace.add_operation(data_block_id='all', operation='kmeans_clustering', parameters=params)
        self.t.last_output = output_column

        return self.t


class Linkage(CtrlNode):
    """Basically scipy.cluster.hierarchy.linkage, Compute a linkage matrix for Hierarchical clustering"""
    nodeName = 'Linkage'
    uiTemplate = [('data_column',   'combo',    {'toolTip', 'Input column for clustering data, must form a 2D array'}),
                  ('method',        'combo',    {'items': ['complete', 'average', 'single']}),
                  ('metric',        'combo',    {'items': ['wasserstein', 'euclidean']}),
                  ('optimal_order', 'check',    {'checked': True}),
                  ('Apply',         'check',    {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.ctrls['data_column'].setItems(self.t.df.columns)

        if not self.ctrls['Apply'].isChecked():
            return

        self.data_column = self.ctrls['data_column'].currentText()

        self.data = np.vstack(self.t.df[self.data_column].values)

        method = self.ctrls['method'].currentText()
        metric = self.ctrls['metric'].currentText()
        optimal_ordering = self.ctrls['optimal_order'].isChecked()

        self.linkage = hierarchy.linkage(self.data, method=method, metric=metric, optimal_ordering=optimal_ordering)
        params = {'method': method, 'metric': metric, 'optimal_ordering': optimal_ordering}

        return {'linkage': self.linkage, 'params': params}


class HierFCluster(CtrlNode):
    """Basically scipy.cluster.hierarchy.fcluster.
    Form flat clusters from the hierarchical clustering defined by the given linkage matrix.
    """
    nodeName = 'FCluster'
    uiTemplate = [('')]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Linkage': {'io': 'in', 'multi': False},
                                                 'Data':    {'io': 'in', 'multi': False},
                                                 'Out': {'io': 'out'}})


# class Agglomerative(CtrlNode):
#     """Recursively merges the pair of clusters that minimally increases a given linkage distance.\n
#     https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html\n
#     Output column -> AGG_CLUSTER_<data_column>"""
#     nodeName = 'Agglomerative'
#     uiTemplate = [('data_column', 'combo', {}),
#
#                   ('n_clusters', 'intSpin',
#                    {'min': 2, 'max': 999, 'step': 1, 'value': 2,
#                     'toolTip': 'The number of clusters to find.'}),
#
#                   ('affinity', 'combo',
#                    {'items': ['wasserstein', 'euclidean', 'l1', 'l2', 'manhattan', 'cosine'],
#                     'tooltip': 'Metric used to compute the linkage.\n'
#                                'Can be “euclidean”, “l1”, “l2”, “manhattan”, “cosine”, or ‘precomputed’.'
#                                '\nIf linkage is “ward”, only “euclidean” is accepted'}),
#
#                   ('connectivity_matrix', 'combo',
#                    {'toolTip': 'Dataframe column containing a connectivity matrix.\n'
#                                'Defines for each sample the neighboring samples following a given structure of the data.\n'
#                                'This can be a connectivity matrix itself or a callable that transforms the data\n'
#                                'into a connectivity matrix, such as derived from kneighbors_graph.\n'
#                                'Default is None, i.e, the hierarchical clustering algorithm is unstructured.'}),
#
#                   ('compute_full_tree', 'combo',
#                    {'items': ['auto', 'True', 'False'],
#                     'toolTip': 'Stop early the construction of the tree at n_clusters.'
#                                '\nThis is useful to decrease computation time if the number of clusters is not small compared to the number of samples.\n'
#                                'This option is useful only when specifying a connectivity matrix.\n'
#                                'Note also that when varying the number of clusters and using caching, it may be advantageous to compute the full tree.'}),
#
#                   ('linkage', 'combo',
#                    {'items': ['complete', 'average', 'single', 'ward'],
#                     'toolTIp': 'The linkage criterion determines which distance to use between sets of observation.'
#                                '\nThe algorithm will merge the pairs of cluster that minimize this criterion.'
#                                '\nward minimizes the variance of the clusters being merged.\n'
#                                'average uses the average of the distances of each observation of the two sets.\n'
#                                'complete or maximum linkage uses the maximum distances between all observations of the two sets.\n'
#                                'single uses the minimum of the distances between all observations of the two sets.'}),
#
#                   ('Apply', 'check', {'checked': False, 'applyBox': True})
#                   ]
#
#     def processData(self, transmission: Transmission):
#         self.t = transmission
#         self.set_data_column_combo_box()
#         columns = transmission.df.columns
#         self.ctrls['connectivity_matrix'].setItems(['None'] + columns.to_list())
#
#         if self.ctrls['Apply'].isChecked() is False:
#             return
#
#         self.t = transmission.copy()
#
#         n_clusters = self.ctrls['n_clusters'].value()
#         affinity = self.ctrls['affinity'].currentText()
#
#         connectivity_matrix = self.ctrls['connectivity_matrix'].currentText()
#         if connectivity_matrix == 'None':
#             connectivity_matrix = None
#             connectivity_matrix_col = None
#         else:
#             connectivity_matrix_col = connectivity_matrix
#             connectivity_matrix = np.vstack(self.t.df[connectivity_matrix_col].values)
#
#         compute_full_tree = self.ctrls['compute_full_tree'].currentText()
#         if compute_full_tree == 'True':
#             compute_full_tree = True
#         elif compute_full_tree == 'False':
#             compute_full_tree = False
#
#         linkage = self.ctrls['linkage'].currentText()
#
#         output_column = 'AGG_CLUSTER_LABEL'
#
#         data = np.vstack(self.t.df[self.data_column].values)
#
#         if affinity == 'wasserstein':
#             data = pairwise_distances(data, metric=wasserstein_distance)
#             distance_metric = 'wasserstein'
#             affinity = 'precomputed'
#         else:
#             distance_metric = affinity
#
#         self.clustering = skcluster.AgglomerativeClustering(n_clusters=n_clusters, affinity=affinity,
#                                                             connectivity=connectivity_matrix,
#                                                             compute_full_tree=compute_full_tree, linkage=linkage)
#
#         self.clustering.fit(data)
#
#         self.t.df[output_column] = self.clustering.labels_
#
#         params = {'data_column':                    self.data_column,
#                   'n_clusters':                     n_clusters,
#                   'affinity':                       affinity,
#                   'distance_metric':                distance_metric,
#                   'connectivity_matrix_column':     connectivity_matrix_col,
#                   'compute_full_tree':              compute_full_tree,
#                   'linkage':                        linkage,
#                   'children':                       self.clustering.children_.tolist()
#                   }
#
#         self.t.history_trace.add_operation(data_block_id='all', operation='agglomerative_clustering', parameters=params)
#         self.t.last_output = output_column
#
#         return self.t


class LDA(CtrlNode):
    """LDA"""
    nodeName = 'LDA'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_gui = None
        self.ctrls['ShowGUI'].clicked.connect(self._open_plot_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_gui is None:
            return

        transmissions = kwargs['In']

        transmissions_list = merge_transmissions(transmissions)

        self.plot_gui.update_input_transmissions(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_gui is None:
            self.plot_gui = LDAPlot(parent=self.parent())
        self.plot_gui.show()


