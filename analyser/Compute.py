#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
from scipy import integrate
import os
# os.system("taskset -p 0xff %d" % os.getpid())


class PeakFeatures:
    @staticmethod
    def amplitude_relative(q, peak_curve, ix_peak_rel):
        try:
            result = abs(min(peak_curve) - peak_curve[ix_peak_rel])
        except:
            result = np.NaN
        q.put({'_pfeature_amplitude_relative': result})

    @staticmethod
    def amplitude_abs(q, pre_peak_baseline, ix_peak_abs):
        try:
            result = ix_peak_abs - pre_peak_baseline
        except:
            result = np.NaN
        q.put({'_pfeature_amplitude_abs': result})

    @staticmethod
    def area(q, peak_curve):
        try:
            result = integrate.simps(peak_curve)
        except:
            result = np.NaN
        q.put({'_pfeature_area': result})

    @staticmethod
    def rising_slope_at_mid(q, peak_curve, ix_peak_rel):
        pass

    @staticmethod
    def rising_slope_avg(q, peak_curve, ix_peak_rel):
        try:
            dy = abs(peak_curve[0] - peak_curve[ix_peak_rel])
            result = dy / ix_peak_rel
        except:
            result = np.NaN
        q.put({'_pfeature_rising_slope_avg': result})

    @staticmethod
    def falling_slope_at_mid(q, peak_curve, ix_peak_rel):
        pass

    @staticmethod
    def falling_slope_avg(q, peak_curve, ix_peak_rel):
        try:
            dy = abs(peak_curve[-1] - peak_curve[ix_peak_rel])
            result = dy / abs(len(peak_curve) - ix_peak_rel)
        except:
            result = np.NaN
        q.put({'_pfeature_falling_slope_avg': result})

    @staticmethod
    def duration_base(q, peak_curve):
        try:
            result = np.size(peak_curve)
        except:
            result = np.NaN
        q.put({'_pfeature_duration_base': result})

    @staticmethod
    def duration_mid(q, curve):
        pass

    @staticmethod
    def inter_peak_interval(q, ix_peak_abs, ix_pre_peak, ix_nex_peak):
        try:
            if (ix_pre_peak is None) or (ix_nex_peak is None):
                result = np.NaN
            else:
                result = np.mean([ix_peak_abs - ix_pre_peak, ix_nex_peak - ix_peak_abs])
        except:
            result = np.NaN

        q.put({'_pfeature_inter_peak_interval': result})
