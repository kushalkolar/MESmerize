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
os.system("taskset -p 0xff %d" % os.getpid())


class PeakFeatures:
    @staticmethod
    def amplitude_relative(q, peak_curve, ix_peak_rel):
        result = abs(min(peak_curve) - peak_curve[ix_peak_rel])
        q.put({'amplitude_relative': result})

    @staticmethod
    def amplitude_abs(q, pre_peak_baseline, ix_peak_abs):
        result = ix_peak_abs - pre_peak_baseline
        q.put({'amplitude_abs': result})

    @staticmethod
    def area(q, peak_curve):
        result = integrate.simps(peak_curve)
        q.put({'area': result})

    @staticmethod
    def rising_slope_at_mid(q, peak_curve, ix_peak_rel):
        pass

    @staticmethod
    def rising_slope_avg(q, peak_curve, ix_peak_rel):
        dy = abs(peak_curve[0] - peak_curve[ix_peak_rel])
        result = dy / ix_peak_rel
        q.put({'rising_slope_avg': result})

    @staticmethod
    def falling_slope_at_mid(q, peak_curve, ix_peak_rel):
        pass

    @staticmethod
    def falling_slope_avg(q, peak_curve, ix_peak_rel):
        dy = abs(peak_curve[-1] - peak_curve[ix_peak_rel])
        result = dy / abs(len(peak_curve) - ix_peak_rel)
        q.put({'falling_slope_avg': result})

    @staticmethod
    def duration_base(q, peak_curve):
        result = np.size(peak_curve)
        q.put({'duration_base': result})

    @staticmethod
    def duration_mid(q, curve):
        pass

    @staticmethod
    def inter_peak_interval(q, ix_peak_abs, ix_pre_peak, ix_nex_peak):
        if (ix_pre_peak is None) or (ix_nex_peak is None):
            result = 'BAAAAAAAAAH'
        else:
            result = {'pre': ix_peak_abs - ix_pre_peak, 'post': ix_nex_peak - ix_peak_abs}

        q.put({'inter_peak_interval': result})
