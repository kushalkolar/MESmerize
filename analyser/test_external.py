#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# kwargs['In'].df['curve']
import numpy as np

t = kwargs['In'].copy()

def _get_zero_crossings(s1):
    """
    :param s1: The first derivative of the signal
    :return: Indices of peaks & bases of the curve
    """
    sc = np.diff(np.sign(s1))

    peaks = np.where(sc < 0)[0]
    bases = np.where(sc > 0)[0]

    return np.array([[peaks], [bases]])

# lf = lambda sig: _get_zero_crossings(sig)

t.df['peaks_bases'] = t.df[t.data_column].apply(_get_zero_crossings)
t.src.append({'Peaks_Bases'})
print(t.df['peaks_bases'])
output = {'Out': t}



# scope['output'] = output