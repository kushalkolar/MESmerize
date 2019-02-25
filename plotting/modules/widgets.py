from PyQt5 import QtCore, QtGui, QtWidgets
from glob import glob
import os


class ColormapListWidget(QtWidgets.QListWidget):
    signal_colormap_changed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtWidgets.QListWidget.__init__(self, parent=parent)
        self.populate_colormaps()
        self.currentItemChanged.connect(self.emit_colormap_changed)
        self.setToolTip('Colormap picker')
        self.setCurrentRow(0)

    @property
    def current_cmap(self) -> str:
        return self.currentItem().text()

    @current_cmap.setter
    def current_cmap(self):
        pass

    def emit_colormap_changed(self, item: QtWidgets.QListWidgetItem):
        self.signal_colormap_changed.emit(item.text())

    def populate_colormaps(self):
        mpath = os.path.abspath(__file__)
        mdir = os.path.dirname(mpath)

        for path in glob(mdir + '/colormaps/*.png'):
            img = QtGui.QIcon(path)
            item = QtWidgets.QListWidgetItem(path.split('/')[-1][:-4])
            item.setIcon(img)
            self.addItem(item)
        self.setIconSize(QtCore.QSize(100,50))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ColormapListWidget()
    w.signal_colormap_changed.connect(lambda c: print(w.current_cmap))
    w.show()
    app.exec_()