# -*- coding: utf-8 -*-
"""
Created on July 7 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


import numpy as np
from scipy.fftpack import rfft, irfft
import sys


def interpolate_irfft(raw_curve: np.ndarray, rfft_curve: np.ndarray, stop_domain: int) -> np.ndarray:
    """
    1D Interpolate of the inverse fourier transform curve so that it is of the same length as the raw curve and can
    be used to calculate the sum of squared differences between them.

    :param raw_curve:   Raw curve
    :param rfft_curve:  Result from scipy.fftpack.rfft(raw_curve)
    :param stop_domain: Number of fourier domains to include for computing the inverse fourier transform
    :return:
    """
    x = np.arange(0, len(raw_curve))
    irf = irfft(rfft_curve[:stop_domain])
    xp = np.linspace(0, raw_curve.size, stop_domain)
    interp = np.interp(x, xp, fp=irf)
    return interp


def sum_of_squared_diff(a: np.ndarray, b: np.ndarray):
    """
    Calculate the sum of squared differences between "a" and "b"
    a and b must be of the same size
    :param a:   1D vector, [x1, x2, x3, ... xn]
    :param b:   1D vector, [x1, x2, x3, ... xn]
    :return:    Sum of squared differences between a and b
    """
    if a.size != b.size:
        raise ValueError('"a" and "b" must be of the same size.')
    r = a - b
    return np.dot(r, r)


def get_residuals(c: np.ndarray) -> np.ndarray:
    """
    :param c:   1D array representing a single curve
    :return:    residuals between the c and irfft of c with increasing steps of frequency domains
    """
    c_r = rfft(c)
    r = np.zeros(shape=(c.size - 1), dtype=np.float64)
    for step in range(1, c.size):
        r[step - 1] = sum_of_squared_diff(c, interpolate_irfft(raw_curve=c, rfft_curve=c_r, stop_domain=step))
    return r


def get_all_residuals(a: np.ndarray) -> np.ndarray:
    """
    :param a:   2D array of 1D curves
    :return:    2D array of residuals for each curve
    """
    r = np.zeros(shape=(a.shape[0], a.shape[1] - 1), dtype=np.float64)
    for i in range(a.shape[0]):
        r[i, :] = get_residuals(a[i, :])
        sys.stdout.write(f"\rProgress: {i/(a.shape[0] - 1)}")
    return r
