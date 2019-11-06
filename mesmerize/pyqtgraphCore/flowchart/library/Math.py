# -*- coding: utf-8 -*-
from ....analysis.math.tvregdiff import tv_reg_diff
from .common import *
from ....analysis.data_types import Transmission
from scipy.stats import zscore as _zscore, linregress
import pandas as pd


class AbsoluteValue(CtrlNode):
    """Performs numpy.abs(<input>). Returns root-mean-square value if <input> is complex"""
    nodeName = 'AbsoluteValue'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        output_column = '_ABSOLUTE_VALUE'

        self.t = transmission.copy()

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.abs(x))

        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='absolute_value', parameters=params)
        self.t.last_output = output_column

        return self.t


class XpowerY(CtrlNode):
    """Raise each element of arrays in data column to the exponent Y"""
    nodeName = 'XpowerY'
    # Not sure why someone would take the 99th power, but I'll leave it there
    uiTemplate = [('data_column', 'combo', {}),
                  ('Y', 'doubleSpin', {'value': 2.0, 'min': -99.0, 'max': 99.0, 'step': 0.5}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]
    output_column = '_X_POWER_Y'

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()
        Y = self.ctrls['Y'].value()
        params = {'data_column': self.data_column,
                  'exponent':    Y}

        self.t.df[self.output_column] = self.t.df[self.data_column].apply(lambda x: np.power(x, Y))

        self.t.history_trace.add_operation(data_block_id='all', operation='x_power_y', parameters=params)
        self.t.last_output = self.output_column

        return self.t


class LogTransform(CtrlNode):
    """Can perform various log transforms"""
    nodeName = 'LogTransform'
    uiTemplate = [('data_column', 'combo', {}),
                  ('transform', 'combo', {'values': ['log10', 'ln', 'modlog10', 'modln']}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_LOG_TRANSFORM'

        transform = self.ctrls['transform'].currentText()
        params = {'data_column': self.data_column,
                  'transform': transform,
                  'units': self.t.last_unit}

        if transform == 'log10':
            self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.log10(x))

        elif transform == 'ln':
            self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: np.log(x))

        elif transform == 'modlog10':
            logmod = lambda x: np.sign(x) * (np.log10(np.abs(x) + 1))
            self.t.df[output_column] = self.t.df[self.data_column].apply(logmod)

        elif transform == 'modln':
            logmod = lambda x: np.sign(x) * (np.log(np.abs(x)) + 1)
            self.t.df[output_column] = self.t.df[self.data_column].apply(logmod)

        self.t.history_trace.add_operation(data_block_id='all', operation='log_transform', parameters=params)
        self.t.last_output = output_column

        return self.t


class Derivative(CtrlNode):
    """Return the Derivative of a curve."""
    nodeName = 'Derivative'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_DERIVATIVE'

        self.t.df[output_column] = self.t.df[self.data_column].apply(np.gradient)
        self.t.last_output = output_column

        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='derivative', parameters=params)

        return self.t


class TVDiff(CtrlNode):
    """Total Variation Regularized Numerical Differentiation, Chartrand 2011 method"""
    nodeName = 'TVDiff'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        output_column = '_TVDIFF'
        tqdm.pandas()
        self.t.df[output_column] = self.t.df[self.data_column].progress_apply(lambda x: self._func(x, 100, 1e-1, dx=0.05, ep=1e-2, scale='large', diagflag=0))
        self.t.last_output = output_column

        params = {'data_column': self.data_column,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='tvdiff', parameters=params)

        return self.t

    def _func(self, *args, **kwargs):
        return tv_reg_diff(*args, **kwargs)


class Integrate(CtrlNode):
    pass


class ArrayStats(CtrlNode):
    """Perform various statistical functions"""
    nodeName = 'ArrayStats'
    uiTemplate = [('data_column', 'combo', {}),
                  ('function', 'combo', {'items': ['amin', 'amax', 'nanmin', 'nanmax', 'ptp', 'median', 'mean', 'std',
                                                   'var', 'nanmedian', 'nanmean', 'nanstd', 'nanvar']}),
                  ('group_by', 'combo', {}),
                  ('group_by_sec', 'combo', {}),
                  ('output_col', 'lineEdit', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        dcols = organize_dataframe_columns(transmission.df.columns)[0]
        self.ctrls['data_column'].setItems(dcols)

        ccols = ['------'] + organize_dataframe_columns(self.t.df.columns)[1]
        self.ctrls['group_by'].setItems(ccols)
        self.ctrls['group_by_sec'].setItems(ccols)

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        output_column = self.ctrls['output_col'].text()

        output_column = output_column.upper()
        if not output_column.startswith('_'):
            output_column = '_' + output_column

        function = self.ctrls['function'].currentText()

        if self.ctrls['group_by'].currentIndex() > 0:
            group_by = self.ctrls['group_by'].currentText()
        else:
            group_by = False

        if self.ctrls['group_by_sec'].currentIndex() > 0:
            group_by_sec = self.ctrls['group_by_sec'].currentText()
        else:
            group_by_sec = False

        params = {'data_column': self.data_column,
                  'output_column': output_column,
                  'function': function,
                  'group_by': group_by,
                  'group_by_sec': group_by_sec
                  }

        func = getattr(np, function)

        if group_by_sec:
            secondary_groups = self.t.df[group_by_sec].unique()
        else:
            secondary_groups = ['']

        if group_by:
            grouped_df = Transmission.empty_df(self.t, addCols=[f'{output_column}'])

            groups_primary = self.t.df[group_by].unique()

            for group in tqdm(groups_primary, total=groups_primary.size, desc='groups'):
                gdf = self.t.df[self.t.df[group_by] == group]

                for sgroup in secondary_groups:

                    if sgroup:
                        sgdf = gdf[gdf[group_by_sec] == sgroup]
                        s = sgdf.iloc[0].copy()

                    else:
                        sgdf = gdf
                        s = gdf.iloc[0].copy()

                    data = np.vstack(sgdf[self.data_column])
                    results = func(data, axis=0)

                    s[f'{output_column}'] = results

                    grouped_df = grouped_df.append(s, ignore_index=True)

            self.t.df = grouped_df
        else:
            self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: func(x))

        self.t.last_output = output_column

        self.t.history_trace.add_operation('all', 'array_stats', params)

        return self.t


class ArgGroupStat(CtrlNode):
    """Group by a certain column and return value of another column based on a data column statistic"""
    nodeName = 'ArgGroupStat'
    uiTemplate = [('data_column', 'combo', {}),
                  ('group_by', 'combo', {}),
                  ('return_col', 'combo', {}),
                  ('stat', 'combo', {'items': ['min', 'max']}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        ccols = organize_dataframe_columns(self.t.df.columns)[1]
        self.ctrls['group_by'].setItems(ccols)

        self.ctrls['return_col'].setItems(self.t.df.columns.tolist())

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        group_by = self.ctrls['group_by'].currentText()
        return_col = self.ctrls['return_col'].currentText()
        stat = self.ctrls['stat'].currentText()
        output_column = 'ARG_STAT'

        params = {'data_column': self.data_column,
                  'group_by': group_by,
                  'return_col': return_col,
                  'stat': stat,
                  'output_column': output_column
                  }

        out_df = Transmission.empty_df(self.t, addCols=['ARG_STAT'])

        for group in self.t.df[group_by].unique():
            gdf = self.t.df[self.t.df[group_by] == group]
            gdf.reset_index(drop=True, inplace=True)

            if stat == 'max':
                ix = gdf[self.data_column].idxmax()

            elif stat == 'min':
                ix = gdf[self.data_column].idxmin()

            s = gdf.iloc[ix].copy()
            s['ARG_STAT'] = s[return_col]

            out_df = out_df.append(s, ignore_index=True)

        self.t.df = out_df
        self.t.history_trace.add_operation('all', 'arg-group-stat', params)

        return self.t


class ZScore(CtrlNode):
    """
    Z-Score the input data. Uses scipy.stats.zscore.
    Computes over sub-DataFrames that are created according to the "group_by" column parameter
    """
    nodeName = 'ZScore'
    uiTemplate = [('data_column', 'combo', {}),
                  ('group_by', 'combo', {}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        ccols = organize_dataframe_columns(self.t.df.columns)[1]
        self.ctrls['group_by'].setItems(ccols)

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        group_by = self.ctrls['group_by'].currentText()
        output_column = '_ZSCORE'

        params = {'data_column': self.data_column,
                  'group_by': group_by,
                  'output_column': output_column
                  }

        out_dfs = []

        # Per group
        for group in self.t.df[group_by].unique():
            sub_df = self.t.df[self.t.df[group_by] == group].copy()

            data = np.vstack(sub_df[self.data_column].values)
            zdata = _zscore(data, axis=None)

            sub_df['_ZSCORE'] = zdata.tolist()

            out_dfs.append(sub_df)

        df = pd.concat(out_dfs).reset_index(drop=True)
        df['_ZSCORE'] = df._ZSCORE.apply(np.array)

        self.t.df = df

        self.t.history_trace.add_operation('all', 'zscore', params)
        self.t.last_output = '_ZSCORE'

        return self.t


class LinRegress(CtrlNode):
    """Linear Regression"""
    nodeName = 'LinRegress'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        params = {'data_column': self.data_column}

        self.t.df[['_SLOPE', '_INTERCEPT', '_R-VALUE', '_P-VALUE', '_STDERR']] \
            = self.t.df[self.data_column].apply(lambda y: self._linreg(np.arange(y.size), y))

        self.t.history_trace.add_operation('all', 'linreg', params)
        self.t.last_output = None

        return self.t

    def _linreg(self, x, y):
        r = linregress(x=np.arange(y.size), y=y)

        return pd.Series({'_SLOPE': r[0],
                          '_INTERCEPT': r[1],
                          '_R-VALUE': r[2],
                          '_P-VALUE': r[3],
                          '_STDERR': r[4]})
