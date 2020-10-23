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


_default_figure_opts = dict(
    plot_height=500,
    plot_width=500,
    tools='tap,hover,pan,wheel_zoom,box_zoom,reset',
)


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
        self.sig_point_selected = BokehCallbackSignal()
        WebPlot.__init__(self)

        self.dataframe: pd.DataFrame = dataframe
        self.data_column = data_column
        self.groupby_column = groupby_column

        if source_columns is None:
            source_columns = []

        self.source: ColumnDataSource = ColumnDataSource(
            self.dataframe.drop(
                columns=[c for c in self.dataframe.columns if c not in source_columns]
            )
        )

        # for signal in self.signals:
        self.sig_point_selected.dataframe = self.dataframe
        self.sig_point_selected.source_data = self.source

        self.tooltip_columns = tooltip_columns
        self.tooltips = None

        if self.tooltip_columns is not None:
            self.tooltips = [(col, f'@{col}') for col in tooltip_columns]

        if figure_opts is None:
            figure_opts = dict()

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

        x_vals = jitter(self.groupby_column, width=0.6, range=self.figure.x_range)

        self.glyph = self.figure.circle(
            x=x_vals,
            y=self.data_column,
            source=self.source,
            **{
                **_default_glyph_opts,
                **glyph_opts
            }
        )

        self.project_path = project_path
        self.source_columns = source_columns

    def test_callback(self, attr, old, new):
        sdf = self.dataframe[self.dataframe['SampleID'] == 'odor_by_06122019_a1-_-1']
        self.datapoint_tracer.set_sample(sdf)
        print("CALLED")

    def start_app(self, doc):
        print("starting app")
        self.datapoint_tracer = DatapointTracer(
            doc, self.project_path, tooltip_columns=self.tooltip_columns
        )

        self.datapoint_tracer.tooltips = self.tooltips

        self.glyph.data_source.selected.on_change('indices', self.sig_point_selected.trigger)
        self.sig_point_selected.connect_data(self.datapoint_tracer.set_sample, 'SampleID')

        self.datapoint_tracer.set_dashboard([self.figure])
