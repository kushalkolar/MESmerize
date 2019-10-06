import numpy as np
from scipy.cluster import hierarchy
from scipy.stats import wasserstein_distance
from ....analysis import Transmission
from .common import *
from typing import *
from ....analysis.math.emd import emd_1d
from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import squareform
from ....common import get_sys_config


class Linkage(CtrlNode):
    """
    Basically scipy.cluster.hierarchy.linkage
    Compute a linkage matrix for Hierarchical clustering
    """

    nodeName = 'Linkage'
    uiTemplate = [('data_column',   'combo',    {'toolTip': 'Input column for clustering data, must form a 2D array'}),
                  ('method',        'combo',    {'items': ['complete', 'average', 'single']}),
                  ('metric',        'combo',    {'items': ['wasserstein', 'euclidean']}),
                  ('optimal_order', 'check',    {'checked': True}),
                  ('Apply',         'check',    {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        dcols = organize_dataframe_columns(self.t.df.columns.to_list())[0]
        self.ctrls['data_column'].setItems(dcols)

        if not self.ctrls['Apply'].isChecked():
            return

        self.data_column = self.ctrls['data_column'].currentText()

        self.data = np.vstack(self.t.df[self.data_column].values)

        method = self.ctrls['method'].currentText()
        metric = self.ctrls['metric'].currentText()
        optimal_ordering = self.ctrls['optimal_order'].isChecked()

        if metric == 'wasserstein':
            self.data += np.abs(self.data.min())
            distM = pairwise_distances(self.data, metric=emd_1d, n_jobs=get_sys_config()['_MESMERIZE_N_THREADS'])
            condensed = squareform(distM, checks=False)
            self.linkage = hierarchy.linkage(condensed, method=method, optimal_ordering=optimal_ordering)
        else:
            metric_ = metric
            self.linkage = hierarchy.linkage(self.data, method=method, metric=metric_, optimal_ordering=optimal_ordering)

        params = {'method': method, 'metric': metric, 'optimal_ordering': optimal_ordering}

        return {'linkage': self.linkage, 'params': params}


class FCluster(CtrlNode):
    """
    Basically scipy.cluster.hierarchy.fcluster.
    Form flat clusters from the hierarchical clustering defined by the given linkage matrix.
    """

    nodeName = 'FCluster'
    uiTemplate = [('threshold', 'doubleSpin', {'step': 0.001, 'min': 0.0, 'max': 9999.0}),
                  ('criterion', 'combo', {'items': ['distance', 'maxclust', 'inconsistent',
                                                    'monocrit', 'maxclust_monocrit']}),
                  ('depth', 'intSpin', {'min': 1, 'step': 1})
                  ]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Linkage': {'io': 'in'},
                                                 'Data':    {'io': 'in'},
                                                 'IncM':    {'io': 'in'},
                                                 'Monocrit':{'io': 'in'},

                                                 'Out': {'io': 'out'}}, **kwargs)

    def process(self, **kwargs):
        out = self.processData(**kwargs)
        return {'Out': out}

    def processData(self, **inputs):
        self.linkage = inputs['Linkage']

        if self.linkage is None:
            raise ValueError('Must input Linkage matrix')

        linkage_matrix = self.linkage['linkage']
        linkage_params = self.linkage['params']

        self.t = inputs['Data'].copy()

        if 'IncM' in inputs.keys():
            self.IncM = inputs['IncM']
        if 'Monocrit' in inputs.keys():
            self.Monocrit = inputs['Monocrit']

        self.threshold = self.ctrls['threshold'].value()
        self.criterion = self.ctrls['criterion'].currentText()

        self.depth = self.ctrls['depth'].value()

        R = None
        monocrit = None

        params = {'threshold':  self.threshold,
                  'criterion':  self.criterion,
                  'depth':      self.depth,
                  'linkage_matrix': linkage_matrix.tolist(),
                  'linkage_params': linkage_params}

        if self.criterion == 'distance':
            self.cluster_labels = hierarchy.fcluster(linkage_matrix, t=self.threshold, criterion='distance')
            self.t.df['FCLUSTER_LABELS'] = self.cluster_labels
            self.t.last_output = 'fcluster'
            self.t.history_trace.add_operation('all', operation='fcluster', parameters=params)
            return self.t

        elif self.criterion == 'maxclust':
            self.cluster_labels = hierarchy.fcluster(linkage_matrix, t=int(self.threshold), criterion='maxclust')
            self.t.df['FCLUSTER_LABELS'] = self.cluster_labels
            self.t.last_output = 'fcluster'
            self.t.history_trace.add_operation('all', operation='fcluster', parameters=params)
            return self.t

        else:
            params.update({'inc_M_levels': self.IncM['levels']})
            R = self.IncM['R']


            if self.criterion == 'monocrit':
                monocrit = self.Monocrit['MR']

            elif self.criterion == 'maxclust_monocrit':
                pass


class Inconsistent(CtrlNode):
    """Calculate inconsistency statistics on a linkage matrix. Returns inconsistency matrix"""
    nodeName = 'Inconsistent'
    uiTemplate = [('levels', 'intSpin', {'value': 2, 'min': 1, 'max': 99, 'step': 1})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Linkage': {'io': 'in', 'multi': False}, 'IncM': {'io': 'out'}})

    def process(self, **kwargs) -> Dict[str, Dict[np.ndarray, int]]:
        Z = kwargs['Linkage']
        d = self.ctrls['levels']

        R = hierarchy.inconsistent(Z, d)

        return {'IncM': {'R': R, 'levels': d}}


class MaxInconsistent(CtrlNode):
    """Return the maximum inconsistency coefficient for each non-singleton cluster and its children."""
    nodeName = 'MaxInconsistent'
    uiTemplate = [('no params', 'label', {'text': 'no params'})]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Linkage': {'io': 'in', 'multi': False},
                                                 'IncM':    {'io': 'in', 'multi': False},
                                                 'MaxInc':     {'io': 'out'}}, **kwargs)

    def process(self, **kwargs):
        Z = kwargs['Linkage']
        IncM = kwargs['IncM']
        R = IncM['R']

        MI = hierarchy.maxinconsts(Z, R)

        return {'MaxInc': MI}


# class MaxDists(CtrlNode):
#     """Return the maximum distance between any non-singleton cluster."""
#     nodeName = 'MaxDists'
#     uiTemplate = [('no params', 'label', {'text', 'no params'})]
#
#     def __init__(self, name, **kwargs):
#         CtrlNode.__init__(self, name, terminals=)


class MaxIncStat(CtrlNode):
    """Return the maximum statistic for each non-singleton cluster and its children."""
    nodeName = 'MaxIncStat'
    uiTemplate = [('Stat', 'combo', {'items': ['mean', 'stdev', 'num_links', 'inc_coef']})]

    def __init__(self, name, **kwargs):
        CtrlNode.__init__(self, name, terminals={'Linkage', {'io': 'in', 'multi': False},
                                                 'IncM',    {'io': 'in', 'multi': False},
                                                 'MaxStat', {'io': 'out'}}, **kwargs)

    def process(self, **kwargs) -> Dict[str, Dict[np.ndarray, str]]:
        Z = kwargs['Linkage']
        IncM = kwargs['IncM']
        R = IncM['R']

        stat = self.ctrls['Stat'].currentText()

        if stat == 'mean':
            i = 0
        elif stat == 'stdev':
            i = 1
        elif stat == 'num_links':
            i = 2
        elif stat == 'inc_coef':
            i = 3

        MR = hierarchy.maxRstat(Z, R, i)

        return {'MaxStat': {'MR': MR, 'stat': stat}}
