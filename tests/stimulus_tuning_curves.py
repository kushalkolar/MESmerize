from PyQt5 import QtWidgets
from mesmerize import Transmission
from mesmerize.plotting import TuningCurvesWidget


def main():
    t = Transmission.from_hdf5('/work/kushal/pvc7.trn')
    t.set_proj_path('/share/data/temp/kushal/pvc7_subdataset_mesmerize')
    t.set_proj_config()

    w = TuningCurvesWidget(None)
    w.set_input(t)
    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    a = main()

    app.exec()
