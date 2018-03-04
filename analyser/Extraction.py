#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
from .DataTypes import Transmission
import pandas as pd
import numpy as np
from . import Compute
from . import ComputeInterfaces



class PeakFeatures:
    def __init__(self, transmission):
        assert isinstance(transmission, Transmission)
        self.t = transmission

        self.t.df[self.t.data_column['peaks_bases']] = \
            self.t.df[self.t.data_column['peaks_bases']].apply(lambda x:
                                               self._per_curve(x[self.t.data_column['curve']],
                                                               x[self.t.data_column['peaks_bases']]), axis=1)

    def _per_curve(self, curve, pb_df):
        assert isinstance(pb_df, pd.DataFrame)
        self.curve = curve
        self.pb_df = pb_df
        # self.peaks = pb_df['event'][pb_df['peak']]
        self.all_peaks = np.where(self.pb_df['peak'])[0]
        self.pb_df['features'] = self.pb_df.apply(lambda x: self._per_peak(x.name, x.event) if x.peak else {})

        return self.pb_df

    def _per_peak(self, df_ix, ix_peak_abs):
        try:
            ix_base_left_abs = self.pb_df.iloc[df_ix-1]['event']
            ix_base_right_abs = self.pb_df.iloc[df_ix+1]['event']
        except IndexError:
            print('Cannot calculate features for peak at index: ' + str(df_ix) + ' since it is missing at least one base')

            return {}

        if ix_base_left_abs != 'base' or ix_base_right_abs != 'base':
            print('Cannot calculate features for peak at index: ' + str(df_ix) + ' since it is missing at least one base')

            return {}

        try:
            ixp = np.where(self.all_peaks == ix_peak_abs)[0][0]
            ix_pre_peak = self.pb_df[self.all_peaks[ixp - 1]]
            ix_nex_peak = self.pb_df[self.all_peaks[ixp + 1]]
        except IndexError:
            ix_pre_peak = None
            ix_nex_peak = None
            print('Missing a neighboring peak')

        # peak_curve is the portion of the main curve (self.curve) that is between the 2 bases of the peak.
        # ix_base_left_abs is the index of the left base of the peak
        # ix_base_right_abs is the index of the right base of the peak
        peak_curve = np.take(self.curve, np.arange(ix_base_left_abs, ix_base_right_abs))
        ix_peak_rel = ix_peak_abs - ix_base_left_abs  # Relative index of the peak within peak_curve

        # A dictionary of Compute function names as the key, the stuff in that key is that function's arguments
        args_d = {'amplitude_relative': [peak_curve, ix_peak_rel],
                  'amplitude_abs': [min(self.curve), ix_peak_abs],
                  'area': [peak_curve],
                  'rising_slope_at_mid': [peak_curve, ix_peak_rel],
                  'rising_slope_avg': [peak_curve, ix_peak_rel],
                  'falling_slope_at_mid': [peak_curve, ix_peak_rel],
                  'falling_slope_avg': [peak_curve, ix_peak_rel],
                  'duration_base': [peak_curve],
                  'duration_mid': [peak_curve],
                  'inter_peak_interval': [ix_peak_abs, ix_pre_peak, ix_nex_peak]
                  }

        to_compute = Compute.PeakFeatures
        # Create instance of Static interface by passing in Compute class and args dictionary
        compute_interface = ComputeInterfaces.Static(to_compute, args_d)
        # Spawn and run the processes
        compute_interface.run()
        # Get the results after everything has been computed.
        return compute_interface.get_results()

        # With this I can get a list of all the static methods in

