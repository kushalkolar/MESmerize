#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @author: kushal
#
# Chatzigeorgiou Group
# Sars International Centre for Marine Molecular Biology
#
# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007


import numpy as np
from itertools import product
from ...common.utils import HdfTools
from ...common.configuration import HAS_TSLEARN
if HAS_TSLEARN:
    from tslearn.cycc import normalized_cc


def ncc_c(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Must pass 1D array to both x and y

    :param x: Input array [x1, x2, x3, ... xn]
    :param y: Input array [y2, y2, x3, ... yn]

    :return:  Returns the normalized cross correlation function (as an array) of the two input vector arguments "x" and "y"
    :rtype: np.ndarray
    """
    cc = normalized_cc(x.reshape(-1, 1), y.reshape(-1, 1))
    return cc


def get_omega(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> int:
    """
    Must pass a 1D array to either both "x" and "y" or a cross-correlation function (as an array) to "cc"

    :param x: Input array [x1, x2, x3, ... xn]
    :param y: Input array [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as an array [c1, c2, c3, ... cn]

    :return: index (x-axis position) of the global maxima of the cross-correlation function
    :rtype: np.ndarray
    """
    if cc is None:
        cc = ncc_c(x, y)
    w = np.argmax(cc)
    return w


def get_lag(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> float:
    """
    Must pass a 1D array to either both "x" and "y" or a cross-correlation function (as an array) to "cc"

    :param x: Input array [x1, x2, x3, ... xn]
    :param y: Input array [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as a array [c1, c2, c3, ... cn]

    :return: Position of the maxima of the cross-correlation function with respect to middle point of the cross-correlation function
    :rtype: np.ndarray
    """
    if cc is None:
        w = get_omega(x, y)
        s = w - x.shape[0]
    else:
        w = get_omega(cc=cc)
        s = w - int(cc.shape[0] / 2)
    return float(-s)


def get_epsilon(x: np.ndarray = None, y: np.ndarray = None, cc: np.ndarray = None) -> float:
    """
    Must pass a 1D vector to either both "x" and "y" or a cross-correlation function to "cc"

    :param x: Input array [x1, x2, x3, ... xn]
    :param y: Input array [y2, y2, x3, ... yn]
    :param cc: cross-correlation function represented as an array [c1, c2, c3, ... cn]

    :return: Magnitude of the global maxima of the cross-correlationn function
    :rtype: np.ndarray
    """
    if cc is None:
        cc = ncc_c(x, y)
    e = np.max(cc)
    return e


def get_lag_matrix(curves: np.ndarray = None, ccs: np.ndarray = None) -> np.ndarray:
    """
    Get a 2D matrix of lags. Can pass either a 2D array of 1D curves or cross-correlations

    :param curves: 2D array of 1D curves
    :param ccs:    2D array of 1D cross-correlation functions represented by arrays

    :return: 2D matrix of lag values, shape is [n_curves, n_curves]
    :rtype: np.ndarray
    """
    if ccs is None:
        m = curves.shape[0]
        a = np.zeros((m, m))

        for i, j in product(*(range(m),) * 2):
            a[i, j] = get_lag(curves[i], curves[j])
        return a

    return _compute_from_ccs(ccs, get_lag)


def get_epsilon_matrix(curves: np.ndarray = None, ccs: np.ndarray = None) -> np.ndarray:
    """
    Get a 2D matrix of maximas. Can pass either a 2D array of 1D curves or cross-correlations

    :param curves: 2D array of 1D curves
    :param ccs:    2D array of 1D cross-correlation functions represented by arrays

    :return: 2D matrix of maxima values, shape is [n_curves, n_curves]
    :rtype: np.ndarray
    """
    if ccs is None:
        m = curves.shape[0]
        a = np.zeros((m, m))
        for i, j in product(*(range(m),) * 2):
            a[i, j] = get_epsilon(curves[i], curves[j])
        return a

    return _compute_from_ccs(ccs, get_epsilon)


def _compute_from_ccs(ccs: np.ndarray, func: callable) -> np.ndarray:
    m = ccs.shape[0]
    a = np.zeros(shape=(m, m))
    for i, j in product(*(range(m),) * 2):
        a[i, j] = func(cc=ccs[i, j, :])
    return a


class CC_Data:
    def __init__(self,
                 input_data: np.ndarray = None,
                 ccs: np.ndarray = None,
                 lag_matrix: np.ndarray = None,
                 epsilon_matrix: np.ndarray = None,
                 curve_uuids: np.ndarray = None,
                 labels: np.ndarray = None):
        """
        Object for organizing cross-correlation data

        types must be numpy.ndarray to be compatible with hdf5

        :param ccs:             array of cross-correlation functions, shape: [n_curves, n_curves, func_length]
        :type ccs:              np.ndarray
        :param lag_matrix:      the lag matrix, shape: [n_curves, n_curves]
        :type lag_matrix:       np.ndarray
        :param epsilon_matrix:  the maxima matrix, shape: [n_curves, n_curves]
        :type epsilon_matrix:   np.ndarray
        :param curve_uuids:     uuids (str representation) for each of the curves, length: n_curves
        :type curve_uuids:      np.ndarray
        :param labels:          labels for each curve, length: n_curves
        :type labels:           np.ndarray
        """
        self.input_data: np.ndarray = input_data
        self.ccs = ccs  #: array of cross-correlation functions
        self.lag_matrix = lag_matrix  #: lag matrix
        self.epsilon_matrix = epsilon_matrix  #: maxima matrix
        self.curve_uuids = curve_uuids  #: uuids for each curve
        self.labels = labels  #: labels for each curve

    def get_threshold_matrix(self, matrix_type: str, lag_thr: float, max_thr: float,
                             lag_thr_abs: bool = True) -> np.ndarray:
        """
        Get lag or maxima matrix with thresholds applied. Values outside the threshold are set to NaN

        :param matrix_type:     one of 'lag' or 'maxima'
        :param lag_thr:         lag threshold
        :param max_thr:         maxima threshold
        :param lag_thr_abs:     threshold with the absolute value of lag

        :return:    the requested matrix with the thresholds applied to it.
        :rtype: np.ndarray
        """
        # Get lag and maxima matrices
        l = self.lag_matrix
        m = self.epsilon_matrix

        if (l is None) or (m is None):
            raise ValueError('No lag or maxima data available')

        # The type of matrix to return
        if matrix_type == 'lag':
            a = np.copy(l)
        elif matrix_type == 'maxima':
            a = np.copy(m)
        else:
            raise ValueError('Argument "matrix_type" must be "lag" or "maxima"')

        # Set all values below both thresholds to nan
        if lag_thr_abs:
            a[np.abs(l) > lag_thr] = np.nan
        else:
            a[l > lag_thr] = np.nan

        a[m < max_thr] = np.nan

        return a

    @classmethod
    def from_dict(cls, d: dict):
        """Load data from a dict"""
        return cls(**d)

    def to_hdf5(self, path: str):
        """
        Save as an HDF5 file

        :param path: path to save the hdf5 file to, file must not exist.
        """

        HdfTools.save_dict(self.__dict__, path, 'cross_corr_data')

    @classmethod
    def from_hdf5(cls, path: str):
        """
        Load cross-correlation data from an hdf5 file

        :param path: path to the hdf5 file
        """
        d = HdfTools.load_dict(path, 'cross_corr_data')
        return cls(**d)


def compute_cc_data(curves: np.ndarray) -> CC_Data:
    """
    Compute cross-correlation data (cc functions, lag and maxima matrices)

    :param curves: input curves as a 2D array, shape is [n_samples, curve_size]

    :return:    cross correlation data for the input curves as a CC_Data instance
    :rtype: CC_Data
    """
    ccs = compute_ccs(curves)

    l = get_lag_matrix(ccs=ccs)
    e = get_epsilon_matrix(ccs=ccs)

    return CC_Data(curves, ccs, l, e)


def compute_ccs(a: np.ndarray) -> np.ndarray:
    """
    Compute cross-correlations between all 1D curves in a 2D input array

    :param a: 2D input array of 1D curves, shape is [n_samples, curve_size]

    :rtype: np.ndarray
    """
    n = a.shape[0]
    m = a.shape[1]
    out = np.zeros(shape=(n, n, (2 * m) - 1))

    for i, j in product(*(range(n),) * 2):
        out[i, j, :] = ncc_c(a[i], a[j])
    return out
