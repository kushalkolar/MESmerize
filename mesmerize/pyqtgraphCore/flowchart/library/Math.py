# -*- coding: utf-8 -*-
import numpy as np
from ....analysis.math.tvregdiff import tv_reg_diff
from .common import *
from ....analysis.data_types import Transmission


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
                  ('output_col', 'lineEdit', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if not self.apply_checked():
            return

        self.t = transmission.copy()

        output_column = self.ctrls['output_col'].text()

        output_column = output_column.upper()
        if not output_column.startswith('_'):
            output_column = '_' + output_column

        function = self.ctrls['function']

        params = {'data_column': self.data_column,
                  'output_column': output_column,
                  'function': function
                  }

        func = getattr(np, function)

        self.t.df[output_column] = self.t.df[self.data_column].apply(lambda x: func(x))
        self.t.last_output = output_column

        self.t.history_trace.add_operation('all', 'array_stats', params)

        return self.t

