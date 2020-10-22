from bokeh.plotting import figure, Figure, gridplot, curdoc
from bokeh.models.glyphs import Image
from bokeh.document import Document
from bokeh.models import HoverTool, ColumnDataSource, TapTool, Slider, TextInput
from bokeh.models.mappers import LogColorMapper
from bokeh.transform import jitter
from bokeh.layouts import gridplot, column, row
import os
import numpy as np
from pathlib import Path
from typing import *
import tifffile
from ..utils import auto_colormap


class DatapointTracer:
    def __init__(self, parent_document: Document, project_path: Union[Path, str]):
        self.parent_document: Document = parent_document
        self.project_path: Path = Path(project_path)

        self.image_figure: Figure = figure(
            plot_height=600,
            plot_width=600,
            tooltips=[("x", "$x"), ("y", "$y"), ("value", "@image")],
            output_backend='webgl'
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

        self.current_frame: int = -1
        self.tif: tifffile.TiffFile = None
        self.color_mapper: LogColorMapper = None

        self.label_filesize: TextInput = TextInput(value='', title='Filesize (GB):')

    def set_sample(self, sdict: dict):
        """

        :param sdict: dict with values pertaining to one sample
        :return:
        """

        sid = sdict['SampleID']
        img_uuid = sdict['ImgUUID']

        img_path = self.project_path.joinpath('images', 'images', f'{sid}-_-{img_uuid}.tiff')

        self.tif = tifffile.TiffFile(img_path)

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
        self.label_filesize.update(value=str(os.path.getsize(img_path) / 1024 / 1024 / 1024))

    def _set_current_frame(self, i: int):
        self.current_frame = i
        frame = self.tif.asarray(key=self.current_frame)

        self.image_glyph.data_source.data['image'] = [frame]

