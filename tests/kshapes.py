from PyQt5 import QtWidgets
from analysis.data_types import Transmission
from plotting.widgets import KShapeWidget


def run():
    t = Transmission.from_pickle('/home/kushal/Sars_stuff/jorgen_stuff/pfeatures_100_curves.trn')
    w = KShapeWidget()
    w.set_input(t)
    w.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    run()
    app.exec_()
