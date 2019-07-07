from PyQt5 import QtCore
import tifffile
from uuid import UUID
import traceback
import os
from typing import Optional


class Signals(QtCore.QObject):
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(str)


class Compressor(QtCore.QRunnable):
    def __init__(self, file_path: str, u: Optional[UUID] = None):
        super(Compressor, self).__init__()
        self.signals = Signals()
        self.u = u
        self.file_path = file_path

    def run(self):
        try:
            tif = tifffile.imread(self.file_path)
            seq = tif.asarray(maxworkers=8)
            filename = os.path.splitext(self.file_path)[0]
            tmp_path = f'{filename}_tmp.tiff'

            tifffile.imsave(tmp_path, data=seq, bigtiff=True, compress=True)

            os.remove(self.file_path)
            os.rename(tmp_path, self.file_path)
        except:
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.finished.emit(self.u)
        finally:
            pass
