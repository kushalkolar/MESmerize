from PyQt5 import QtWidgets
from mesmerize.analysis.data_types import Transmission
from mesmerize.plotting import SOSD_Widget
from mesmerize.pyqtgraphCore.console import ConsoleWidget


def run() -> QtWidgets.QWidget:
    t = Transmission.from_hdf5('/share/data/temp/kushal/cell_types_jun_2019_hdf5.trn')
    t.df['_SPLICE_ARRAYS'] = t.df._RAW_CURVE.apply(lambda r: r[:2990])
    w = SOSD_Widget()
    w.set_input(t)
    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = run()
    c = ConsoleWidget(namespace={'this': w})
    c.show()
    app.exec_()
