#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 27 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""
import scipy.io as spio


def are_floats_equal(m: float, n: float, epsilon: float = 0.0001) -> bool:
    return abs((m + 0.0) - (n + 0.0)) < epsilon


class MatlabFuncs:
    @staticmethod
    def loadmat(filename: str) -> dict:
        data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
        return MatlabFuncs._check_keys(data)

    @staticmethod
    def _check_keys(d: dict) -> dict:
        for key in d:
            if isinstance(d[key], spio.matlab.mio5_params.mat_struct):
                d[key] = MatlabFuncs._todict(d[key])
        return d

    @staticmethod
    def _todict(matobj: spio.matlab.mio5_params.mat_struct) -> dict:
        d = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                d[strg] = MatlabFuncs._todict(elem)
            else:
                d[strg] = elem
        return d
