from PyQt5 import QtWidgets
from mesmerize.analysis.data_types import Transmission
from mesmerize.plotting.widgets import KShapeWidget


def run():
    t = Transmission.from_hickle('/home/kushal/Sars_stuff/jorgen_stuff/pfeatures_100_curves_hdf5.trn')
    w = KShapeWidget()
    w.set_input(t)
    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = run()
    app.exec_()
