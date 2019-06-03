from PyQt5 import QtWidgets
from mesmerize.analysis.data_types import Transmission
from mesmerize.plotting.widgets import CrossCorrelationWidget
from mesmerize.pyqtgraphCore.console import ConsoleWidget


def run():
    t = Transmission.from_hickle('/home/kushal/Sars_stuff/mesmerize_toy_datasets/cesa_hnk1_raw_data.trn')
    w = CrossCorrelationWidget()
    w.set_input(t)
    w.show()
    return w


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = run()
    c = ConsoleWidget(namespace={'this': w})
    c.show()
    app.exec_()
