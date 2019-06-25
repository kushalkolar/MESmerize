from .variants import *
from .widgets import *

from ..analysis import Transmission
from ..common import get_project_manager
from PyQt5.QtWidgets import QWidget


def open_plot_file(file_path: str) -> QWidget:
    t = Transmission.from_hdf5(file_path)

    if t.plot_state is None:
        raise ValueError('The chosen Transmission file does not have the required "plot_state" attribute')

    if t.plot_state['type'] not in widgets.__all__:
        raise ValueError('Plot type not found.')

    plot_widget = getattr(widgets, t.plot_state['type'])()
    plot_widget.open_plot(file_path, get_project_manager().root_dir)

    return plot_widget
