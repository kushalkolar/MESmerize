from bokeh.plotting import figure, Figure, gridplot, curdoc
from bokeh.models.glyphs import Image, MultiLine
from bokeh.document import Document
from bokeh.models import HoverTool, ColumnDataSource, TapTool, Slider, TextInput, Select
from bokeh.models.mappers import LogColorMapper
from bokeh.transform import jitter
from bokeh.layouts import gridplot, column, row
import os
import numpy as np
import pandas as pd
from uuid import UUID
from pathlib import Path
from typing import *
import tifffile
from ..utils import auto_colormap, map_labels_to_colors
from .core import BokehCallbackSignal, WebPlot


_default_image_figure_params = dict(
    plot_height=500,
    plot_width=500,
    tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")],
    output_backend='webgl'
)

_default_curve_figure_params = dict(
    plot_height=300,
    plot_width=1200,
    tools='tap,hover,pan,wheel_zoom,box_zoom,reset',
)


def get_numerical_columns(dataframe: pd.DataFrame):
    return [c for c in dataframe.columns if c.startswith('_')]


def get_categorical_columns(dataframe: pd.DataFrame):
    return [c for c in dataframe.columns if not c.startswith('_')]


class DatapointTracer(WebPlot):
    sig_plot_options_changed = BokehCallbackSignal()
    sig_frame_changed = BokehCallbackSignal()

    def __init__(
            self,
            parent_document: Document,
            project_path: Union[Path, str],
            tooltip_columns: List[str] = None,
            image_figure_params: dict = None,
            curve_figure_params: dict = None
    ):
        self.parent_document: Document = parent_document
        self.project_path: Path = Path(project_path)

        if image_figure_params is None:
            image_figure_params = dict()

        img_fig_params = \
            {
                **_default_image_figure_params,
                **image_figure_params
            }

        self.image_figure: Figure = figure(
            **img_fig_params
        )

        # must initialize with some array else it won't work
        empty_img = np.zeros(shape=(100, 100), dtype=np.uint8)

        self.image_glyph: Image = self.image_figure.image(
            image=[empty_img],
            x=0, y=0,
            dw=10, dh=10,
            level="image"
        )

        self.image_figure.grid.grid_line_width = 0

        self.curve_figure: Figure = None

        if curve_figure_params is None:
            curve_figure_params = dict()

        self.curve_figure_params = \
            {
                **_default_curve_figure_params,
                **curve_figure_params
            }

        self.curve_glyph: MultiLine = None

        self.tooltip_columns = tooltip_columns
        self.tooltips = None

        if self.tooltip_columns is not None:
            self.tooltips = [(col, f'@{col}') for col in tooltip_columns]

        self.dataframe: pd.DataFrame = None
        self.sample_id: str = None
        self.img_uuid: UUID = None
        self.current_frame: int = -1
        self.tif: tifffile.TiffFile = None
        self.color_mapper: LogColorMapper = None

        self.curve_color_selector = Select(title="Color based on:", value='', options=[''])
        self.curve_color_selector.on_change('value', self.sig_plot_options_changed.trigger)

        self.curve_data_selector = Select(title="Curve data:", value='', options=[''])
        self.curve_data_selector.on_change('value', self.sig_plot_options_changed.trigger)

        self.sig_plot_options_changed.connect(self.set_curve)

        self.frame_slider = Slider(start=0, end=1000, value=1, step=10, title="Frame index:")

        self.label_filesize: TextInput = TextInput(value='', title='Filesize (GB):')

    def _check_sample(self, dataframe: pd.DataFrame):
        if len(dataframe['SampleID'].unique()) > 1:
            raise ValueError("Greater than one SampleID in the sub-dataframe")

        if len(dataframe['ImgUUID'].unique()) > 1:
            raise ValueError("Greater than one ImgUUID in the sub-dataframe")

        self.dataframe = dataframe
        self.sample_id = dataframe['SampleID'].unique()[0]
        self.img_uuid = dataframe['ImgUUID'].unique()[0]

    @WebPlot.signal_blocker
    def set_sample(self, dataframe: pd.DataFrame):
        """

        :param sdict: dict with values pertaining to one sample
        :return:
        """
        self._check_sample(dataframe)

        fname = f'{self.sample_id}-_-{self.img_uuid}.tiff'
        vid_path = self.project_path.joinpath('images', fname)

        self._set_video(vid_path)
        self._update_plot_options()

    def _set_video(self, vid_path: Union[Path, str]):
        self.tif = tifffile.TiffFile(vid_path)

        self.current_frame = 0
        frame = self.tif.asarray(key=self.current_frame)

        # this is basically used for vmin mvax
        self.color_mapper = LogColorMapper(
            palette=auto_colormap(256, 'gnuplot2'),
            low=np.nanmin(frame),
            high=np.nanmax(frame)
        )

        self.image_glyph.data_source.data['image'] = [frame]
        self.image_glyph.glyph.color_mapper = self.color_mapper

        # shows the file size in gigabytes
        self.label_filesize.update(value=str(os.path.getsize(vid_path) / 1024 / 1024 / 1024))

    def _update_plot_options(self):
        categorical_columns = get_categorical_columns(self.dataframe)
        numerical_columns = get_numerical_columns(self.dataframe)

        self.curve_color_selector.update(
            value= \
                self.curve_color_selector.value \
                    if self.curve_color_selector.value in categorical_columns \
                    else categorical_columns[0],
            options=categorical_columns
        )

        self.curve_data_selector.update(
            value= \
                self.curve_data_selector.value \
                    if self.curve_data_selector.value in numerical_columns \
                    else numerical_columns[0],
            options=numerical_columns
        )

    def _set_current_frame(self, i: int):
        self.current_frame = i
        frame = self.tif.asarray(key=self.current_frame)

        self.image_glyph.data_source.data['image'] = [frame]

    def set_curve(self):
        data_column = self.curve_data_selector.value
        ys = self.dataframe[data_column].values
        xs = [np.arange(0, v.size) for v in ys]

        self.frame_slider.update(start=0, end=ys[0].size - 1, value=0)

        df_dict = self.dataframe.drop(
            columns=[c for c in self.dataframe.columns if c not in self.tooltip_columns]
        ).to_dict()

        colors_column = self.curve_color_selector.value
        ncolors = df_dict[colors_column].unique().size
        if ncolors < 11:
            cmap = 'tab10'
        elif 10 < ncolors < 21:
            cmap = 'tab20'
        else:
            cmap = 'hsv'

        src = ColumnDataSource(
            {
                **df_dict,
                'xs': xs,
                'ys': ys,
                'colors': map_labels_to_colors(df_dict[colors_column], cmap)
            }
        )

        if self.curve_figure is not None:
            curdoc().remove_root(self.curve_figure)
            del self.curve_figure

        # New figure has to be created each time
        self.curve_figure = figure(
            **self.curve_figure_params,
            tooltips=self.tooltips
        )

        self.curve_glyph = self.curve_figure.multi_line(
            xs='xs', ys='ys',
            legend=colors_column,
            line_color='colors',
            line_width=2,
            source=src
        )

        # add the new curve plot to the doc root
        curdoc().add_root(self.curve_figure)

    def set_dashboard(self, figures: List[Figure]):
        curdoc().add_root(
            column(
                row(*(f for f in figures), self.image_figure),
                row(self.curve_data_selector, self.curve_color_selector),
                self.label_filesize,
                self.frame_slider
            )
        )
