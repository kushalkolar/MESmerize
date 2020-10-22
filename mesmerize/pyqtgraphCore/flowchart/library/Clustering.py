from .common import *
from sklearn import cluster as skcluster
from ....common.configuration import HAS_TSLEARN
from warnings import warn
if HAS_TSLEARN:
    from ....plotting.widgets import KShapeWidget


class KShape(CtrlNode):
    """k-Shape clustering"""
    nodeName = "KShape"
    uiTemplate = [('ShowGUI', 'button', {'text': 'ShowGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}, 'Out': {'io': 'out'}})
        self.output_transmission = False
        if HAS_TSLEARN:
            self.kshape_widget = KShapeWidget(parent=None)
            self.kshape_widget.sig_output_changed.connect(self._send_output)
            self.ctrls['ShowGUI'].clicked.connect(self.kshape_widget.show)
        else:
            warn("tslearn not installed, KShape is disabled.")

    def _send_output(self, t: Transmission):
        self.output_transmission = t
        self.changed()

    def process(self, output_transmission=False, **kwargs):
        if self.output_transmission:
            out = self.output_transmission
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


# class LDA(CtrlNode):
#     """LDA"""
#     nodeName = 'LDA'
#     uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
#                   ('ShowGUI', 'button', {'text': 'OpenGUI'})]
#
#     def __init__(self, name):
#         CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
#         self.plot_widget = None
#         self.ctrls['ShowGUI'].clicked.connect(self._open_plot_gui)
#
#     def process(self, **kwargs):
#         if (self.ctrls['Apply'].isChecked() is False) or self.plot_widget is None:
#             return
#
#         transmissions = kwargs['In']
#
#         transmissions_list = merge_transmissions(transmissions)
#
#         self.plot_widget.update_input_transmissions(transmissions_list)
#
#     def _open_plot_gui(self):
#         if self.plot_widget is None:
#             self.plot_widget = LDAPlot()
#         self.plot_widget.show()


