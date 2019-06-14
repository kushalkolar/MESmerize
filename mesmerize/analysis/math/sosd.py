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


def interpolate_irfft(raw_curve: np.ndarray, rfft_curve: np.ndarray, stop_domain: int) -> np.ndarray:
    """
    1D Interpolate of the inverse fourier transform curve so that it is of the same length as the raw curve and can
    be used to calculate the sum of squared differences between them.

    :param raw_curve:   Raw curve
    :param rfft_curve:  Result from scipy.fftack.rfft(raw_curve)
    :param stop_domain: Number of fourier domains to include for computing the inverse fourier transform
    :return:
    """
    x = np.arange(0, len(raw_curve))
    irf = irfft(rfft_curve[:stop_domain])
    xp = np.linspace(0, raw_curve.size, stop_domain)
    interp = np.interp(x, xp, fp=irf)
    return interp


def sum_of_squared_diff(a: np.ndarray, b: np.ndarray):
    r = a - b
    return np.dot(r, r)
