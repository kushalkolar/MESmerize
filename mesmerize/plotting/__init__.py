from .variants import *
from .widgets import *

from ..analysis import Transmission
from ..common import get_project_manager
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from os.path import basename


def open_plot_file(file_path: str) -> QWidget:
    t = Transmission.from_hdf5(file_path)

    if t.plot_state is None:
        raise ValueError('The chosen Transmission file does not have the required "plot_state" attribute')

    if t.plot_state['type'] not in widgets.__all__:
        raise TypeError(f'Plot type not found: {t.plot_state["type"]}.\nSupported plot types are:\n{widgets.__all__}')

    plot_widget = getattr(widgets, t.plot_state['type'])()
    plot_widget.open_plot(file_path, get_project_manager().root_dir)
    plot_widget.setAttribute(Qt.WA_DeleteOnClose)
    plot_widget.setWindowTitle(f"{plot_widget.windowTitle()} - {basename(file_path)}")

    return plot_widget
