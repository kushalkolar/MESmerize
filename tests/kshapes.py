from PyQt5 import QtWidgets
from analyser.DataTypes import Transmission
from plotting.widgets import KShapeWidget


app = QtWidgets.QApplication([])

t = Transmission.from_pickle('/home/kushal/Sars_stuff/jorgen_stuff/pfeatures_100_curves.trn')
# t.df['splice'] = t.df._RAW_CURVE.apply(lambda x: x[:2990])

w = KShapeWidget()
w.set_input(t)
w.show()

app.exec_()
