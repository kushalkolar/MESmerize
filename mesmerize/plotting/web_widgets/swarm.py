import sys
from bokeh.plotting import figure, Figure, gridplot, curdoc
from bokeh.models import HoverTool, ColumnDataSource, TapTool, Slider, TextInput, Select
from bokeh.transform import jitter
import pandas as pd
from pathlib import Path
from typing import *
from mesmerize.plotting.web_widgets.core import WebPlot, BokehCallbackSignal
from mesmerize.plotting.web_widgets.datapoint_tracer import DatapointTracer
import pickle


# The default figure opts that are used
_default_figure_opts = dict(
    plot_height=500,
    plot_width=500,
    tools='tap,hover,pan,wheel_zoom,box_zoom,reset',
)


# default plot opts for the swarm plot
_default_glyph_opts = dict(
    color='Gray',
    fill_alpha=0.7,
    size=7
)


class Swarm(WebPlot):
    # sig_point_selected = BokehCallbackSignal()

    def __init__(
            self,
            project_path: Union[Path, str],
            dataframe: pd.DataFrame,
            data_column: str,
            groupby_column: str,
            figure_opts: dict = None,
            glyph_opts: dict = None,
            tooltip_columns: List[str] = None,
            source_columns: List[str] = None,
    ):
        # these two lines more elegant
        self.sig_point_selected = BokehCallbackSignal()
        WebPlot.__init__(self)

        # just setting some attributes
        self.dataframe: pd.DataFrame = dataframe
        self.data_column = data_column
        self.groupby_column = groupby_column

        if source_columns is None:
            source_columns = []

        # ColumnDataSource is what bokeh uses for plotting
        # it's similar to dataframes but doesn't accept
        # some datatypes like dicts and arrays within dataframe "cells"
        self.source: ColumnDataSource = ColumnDataSource(
            self.dataframe.drop(
                columns=[c for c in self.dataframe.columns if c not in source_columns]
            )
        )

        # need to clean this up to get it within the base WebPlot.__init__()
        # for signal in self.signals:
        self.sig_point_selected.dataframe = self.dataframe
        self.sig_point_selected.source_data = self.source

        # columns used for displaying tooltips
        self.tooltip_columns = tooltip_columns
        self.tooltips = None

        # formatting the display of the tooltips
        if self.tooltip_columns is not None:
            self.tooltips = [(col, f'@{col}') for col in tooltip_columns]

        if figure_opts is None:
            figure_opts = dict()

        # create a figure, combine the default plot opts and any user specific plot opts
        self.figure = figure(
            **{
                **_default_figure_opts,
                **figure_opts
            },
            x_range=self.dataframe[self.groupby_column].unique(),
            tooltips=self.tooltips
        )

        if glyph_opts is None:
            glyph_opts = dict()

        # jitter along the x axis for the swarm scatter
        x_vals = jitter(self.groupby_column, width=0.6, range=self.figure.x_range)

        # the swarm plot itself
        self.glyph = self.figure.circle(
            x=x_vals,
            y=self.data_column,  # the user specified data column
            source=self.source,  # this is the ColumnDataSource created from the dataframe
            **{
                **_default_glyph_opts,
                **glyph_opts
            }
        )

        self.project_path = project_path
        self.source_columns = source_columns

    def start_app(self, doc):
        """
        Call this from ``bokeh.io.show()`` within a notebook to show the plot
        Can also be allowed standalone from a bokeh server

        :param doc:
        :return:
        """

        print("starting app")

        # Also create datapoint tracer plots
        self.datapoint_tracer = DatapointTracer(
            doc, self.project_path, tooltip_columns=self.tooltip_columns
        )

        self.datapoint_tracer.tooltips = self.tooltips

        # when a point is clicked on the scatter plot it will trigger ``sig_point_selected``
        self.glyph.data_source.selected.on_change('indices', self.sig_point_selected.trigger)

        # when ``sig_point_selected`` is triggered it will set the current sample in the datapoint tracer!
        self.sig_point_selected.connect_data(self.datapoint_tracer.set_sample, 'SampleID')

        # Just adds this plot to the layout of the datapoint tracer
        self.datapoint_tracer.set_dashboard([self.figure])
