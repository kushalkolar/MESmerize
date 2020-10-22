from bokeh.plotting import figure, gridplot, curdoc
# from bokeh.io import output_notebook, show
from bokeh.models import HoverTool, ColumnDataSource, TapTool, Slider, TextInput
from bokeh.models.mappers import LogColorMapper
from bokeh.transform import jitter
from bokeh.layouts import gridplot, column, row
from typing import *


class BokehCallbackSignal:
    def __init__(self, source):
        self.source_data: ColumnDataSource = source

        self.callbacks = []
        self.callbacks_data = []

    def connect(self, func: callable):
        """
        Use this to just pass the new value from the widget or glyph to the callback function

        :param func:
        :return:
        """
        self.callbacks.append(func)

    def connect_data(self, func: callable):
        """
        Use this to pass the new source data as a dict to the callback function

        :param func:
        :return:
        """
        self.callbacks_data.append(func)

    def disconnect(self, func: callable):
        if func in self.callbacks:
            self.callbacks.remove(func)
        elif func in self.callbacks_data:
            self.callbacks_data.remove(func)

    def trigger(self, attr, old, val):
        """
        The function signature must have 3 and only 3 args, bokeh is very picky

        :param attr: name of the attribute

        :param old: old value of the attribute

        :param val: the index within `self.source_data` (such as from a glyph using a `ColumnDataSource`)
                    or the new value (such as from a widget)
        :type val:  Union[List[int], Any]

        :return:
        """
        # if there are multiple values
        # such as if multiple datapoints were selected in a glyph
        if len(val) != 1:
            return

        out = dict.fromkeys(self.source_data.column_names)

        for k in out.keys():
            # create a dict of the source_data values at the requested index `val`
            out[k] = self.source_data.data[k][val][0]

        for f in self.callbacks_data:
            f(out)  # send out the source_data present at the `val` index

        for f in self.callbacks:
            f(val)  # send out val directly
