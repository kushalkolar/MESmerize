from mesmerize.viewer.modules.nuset_segment import *
import tifffile
import numpy as np


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    img = tifffile.imread('/home/kushal/Sars_stuff/zfish_stds/5.tiff')

    w = ModuleGUI(None, None)
    w.show()

    w.imgitem_raw.setImage(img)

    app.exec_()
