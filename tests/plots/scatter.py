from mesmerize.plotting.widgets.scatter.scatter_plot import ScatterPlotWidget
from PyQt5 import QtWidgets
from mesmerize import Transmission

app = QtWidgets.QApplication([])
w = ScatterPlotWidget()
w.show()
t = Transmission.from_hdf5('/home/kushal/Sars_stuff/hier_data_wda.trn')
w.set_input(t)
app.exec()
