from PyQt5 import QtWidgets
from mesmerize.analysis.data_types import Transmission
from mesmerize.plotting import HeatmapTracerWidget
from mesmerize.pyqtgraphCore.console import ConsoleWidget


def run() -> QtWidgets.QWidget:
    t = Transmission.from_hdf5('/share/data/temp/kushal/cell_types_jun_2019_hdf5.trn')
    t.set_proj_path('/share/data/temp/kushal/cell_types_apr_2019')
    t.df['_SPLICE_ARRAYS'] = t.df._RAW_CURVE.apply(lambda r: r[:2990])
    w = HeatmapTracerWidget()
    w.set_input(t)
    # w.open_plot(ptrn_path='/home/kushal/MESmerize/tests/heatmapfile.ptrn', proj_path='/share/data/temp/kushal/cell_types_apr_2019')
    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = run()
    c = ConsoleWidget(namespace={'this': w})
    c.show()
    app.exec_()
