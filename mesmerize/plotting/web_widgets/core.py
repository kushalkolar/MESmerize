from bokeh.plotting import figure, gridplot, curdoc
# from bokeh.io import output_notebook, show
from bokeh.models import HoverTool, ColumnDataSource, TapTool, Slider, TextInput
from bokeh.models.mappers import LogColorMapper
from bokeh.transform import jitter
from bokeh.layouts import gridplot, column, row


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

    def trigger(self, attr, old, new):
        if len(new) != 1:
            return

        out = dict.fromkeys(self.source_data.column_names)

        for k in out.keys():
            out[k] = self.source_data.data[k][new][0]

        for f in self.callbacks_data:
            f(out)

        for f in self.callbacks:
            f(new)
