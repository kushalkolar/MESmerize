from mesmerize.viewer.modules.nuset_segment import *

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    w = ModuleGUI(None, None)
    w.show()

    app.exec_()
