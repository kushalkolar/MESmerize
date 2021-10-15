from ...common.configuration import HAS_TSLEARN

from .datapoint_tracer import DatapointTracerWidget

from .heatmap import HeatmapWidget, HeatmapSplitterWidget, HeatmapTracerWidget
from .cross_correlation import CrossCorrelationWidget
from .scatter import ScatterPlotWidget

from .beeswarms import BeeswarmPlotWindow
from .curve_plot_window import CurvePlotWindow

from .proportions import ProportionsWidget
from .space_map import SpaceMapWidget

from .stimulus_tuning import TuningCurvesWidget
from .neural_decompose import NeuralDecomposePlot

__all__ = ['DatapointTracerWidget', 'HeatmapWidget', 'HeatmapSplitterWidget',
           'HeatmapTracerWidget', 'CrossCorrelationWidget', 'ScatterPlotWidget', 'BeeswarmPlotWindow',
           'CurvePlotWindow', 'ProportionsWidget', 'SpaceMapWidget', 'TuningCurvesWidget', 'NeuralDecomposePlot']

if HAS_TSLEARN:
    from .kshape import KShapeWidget
    __all__ += ['KShapeWidget']
