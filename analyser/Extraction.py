#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""
import pandas as pd
import numpy as np
if __name__ == '__main__':
    from DataTypes import Transmission
#    import Compute
    import ComputeInterfaces
    import Compute

else:
    from .DataTypes import Transmission
#    from . import Compute
    from . import ComputeInterfaces
    from . import Compute


class PeakFeatures:
    def __init__(self, transmission):
        assert isinstance(transmission, Transmission)
        self.t = transmission

    def get_all(self):
        self.row = 0
#        self.t.df['peaks_bases']['bah'] = self.t.df[['curve', 'peaks_bases']].apply(lambda x: self._per_curve(x['curve'], x['peaks_bases']), axis=1)
#        self.t.df['peaks_bases'] = self.t.df.apply(lambda x: self._per_curve(x['curve'], x['peaks_bases']), axis=1)
        
        newdf = Transmission.empty_df(self.t)
        
        newdf = self.t.df.apply(lambda x: self._per_curve(x['curve'], x['peaks_bases']), axis=1)

        print('Reaches here')
        return newdf#self.t#self.t.df

    def _per_curve(self, curve, pb_df):
        # assert isinstance(pb_df, pd.DataFrame)
        self.curve = curve
        self.pb_df = pb_df
        # self.peaks = pb_df['event'][pb_df['peak']]
        self.all_peaks = np.where(self.pb_df['peak'])[0]
#        self.pb_df['features'] = self.pb_df.apply(lambda x: self._per_peak(x.name, x.event) if x.peak else {}, axis=1)
        
        features = self.pb_df.apply(lambda x: self._per_peak(x.name, x.event) if x.peak else {}, axis=1)
        
#        self.pb_df.apply(lambda x: print(x), axis=1)
#        print(self.pb_df)
        print('Finished with curve' +str(self.row))
        self.row +=1
#        print(type(self.pb_df.transpose()))
#        return self.pb_df
#        return features
#        return pd.concat([self.pb_df.transpose, features])
        self.pb_df['features'] = features
        return [self.pb_df]

    def _per_peak(self, df_ix, ix_peak_abs):
        try:
            ix_base_left_abs = self.pb_df.iloc[df_ix-1]['event']
        except IndexError:
            ix_base_left_abs = None
            
        try:
            ix_base_right_abs = self.pb_df.iloc[df_ix+1]['event']
        except IndexError:
#            print('Cannot calculate features for peak at index: ' + str(df_ix) + ' since it is missing at least one base')
            ix_base_right_abs = None
#            return None

        if ix_base_left_abs != 'base' or ix_base_right_abs != 'base':
            pass
#            print('Cannot calculate features for peak at index: ' + str(df_ix) + ' since it is missing at least one base')

#            return None

        try:
            ixp = np.where(self.all_peaks == ix_peak_abs)[0][0]
#            print(ixp)
            ix_pre_peak = self.all_peaks[ixp - 1]
            ix_nex_peak = self.all_peaks[ixp + 1]
        except IndexError:
            ix_pre_peak = None
            ix_nex_peak = None
#            print('Missing a neighboring peak')

        # peak_curve is the portion of the main curve (self.curve) that is between the 2 bases of the peak.
        # ix_base_left_abs is the index of the left base of the peak
        # ix_base_right_abs is the index of the right base of the peak
        if (ix_base_left_abs is None) or (ix_base_right_abs is None):
            peak_curve = None
            ix_peak_rel = None
        else:
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
        # print(args_d)
        
        to_compute = Compute.PeakFeatures
        # Create instance of Static interface by passing in Compute class and args dictionary
        compute_interface = ComputeInterfaces.StaticMT(to_compute, args_d)
        # Spawn and run the processes, and get results
        peak_features = compute_interface.compute()
        peak_features.update({'ix_peak_abs': ix_peak_abs, 'ix_peak_rel': ix_peak_rel, 'peak_curve': peak_curve})
        return peak_features

        # With this I can get a list of all the static methods in


class PeakFeaturesIter(PeakFeatures):
    def __init__(self, transmission):
        PeakFeatures.__init__(self, transmission)

    def get_all(self):

        df_exist = False
        for ix, r in self.t.df.iterrows():
            peak_features = self._per_curve(r['curve'], r['peaks_bases'])
            r = r.drop(['peaks_bases', 'curve'])                
            if df_exist is False:
                cols = list(peak_features.iloc[0].keys()) + list(r.index)
                newdf = pd.DataFrame(columns=cols)
                df_exist = True
                
            for p in peak_features:
                ps = pd.Series(p)
                ps = ps.append(r)
                tdf = pd.DataFrame(ps)
                newdf = pd.concat([newdf, tdf.T], ignore_index=True)                
        self.t.df = newdf
        self.t.src.append({'PeakFeaturesGet': ''})
        return self.t
    
    def _per_curve(self, curve, pb_df):
        assert isinstance(pb_df, pd.DataFrame)
        self.curve = curve
        self.pb_df = pb_df
        self.all_peaks = np.where(self.pb_df['peak'])[0]
        self.pb_df['peak_features'] = self.pb_df.apply(lambda x: self._per_peak(x.name, x.event) if x.peak else False, axis=1)
        self.pb_df.drop(self.pb_df[self.pb_df['peak_features'] == False].index, inplace=True)
        self.pb_df.reset_index(drop=True)
        return pb_df['peak_features']
        
if __name__ == '__main__':
    transmission = Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/MESmerize/peaks_new_with_bool.trn')
    t = transmission.copy()
    pf = PeakFeaturesIter(t)
    r = pf.get_all()
