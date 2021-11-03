import numpy as np
from ...common.qdialogs import *
from ..core.common import ViewerUtils
from PyQt5 import QtWidgets
from ..core import ViewerWorkEnv
from ..core.data_types import ImgData
from multiprocessing.shared_memory import SharedMemory
import os
from subprocess import Popen


class Widget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.vboxlayout = QtWidgets.QVBoxLayout(self)
        self.hboxlayout = QtWidgets.QHBoxLayout(self)

        self.label_choose_file = QtWidgets.QLabel()
        self.label_choose_file.setText("Choose `.isxd` file")
        self.vboxlayout.addWidget(self.label_choose_file)

        self.line_edit_path = QtWidgets.QLineEdit()
        self.line_edit_path.setPlaceholderText("Path to `.isxd` file")
        self.line_edit_path.returnPressed.connect(self.parent().load_file)
        self.hboxlayout.addWidget(self.line_edit_path)

        self.btn_open_file_dialog = QtWidgets.QPushButton()
        self.btn_open_file_dialog.setText("...")
        self.btn_open_file_dialog.clicked.connect(self.parent().file_dialog)
        self.hboxlayout.addWidget(self.btn_open_file_dialog)

        self.vboxlayout.addLayout(self.hboxlayout)

        self.btn_load_file = QtWidgets.QPushButton()
        self.btn_load_file.setText("Load File")
        self.btn_load_file.clicked.connect(self.parent().load_file)
        self.vboxlayout.addWidget(self.btn_load_file)


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)
        self.setFloating(True)
        self.setWindowTitle('Inscopix Importer')

        self.widget = Widget(parent=self)

        self.setWidget(self.widget)

        # self.setLayout(self.vboxlayout)
    @use_open_file_dialog("Choose .isxd file", "", exts=["*.isxd"])
    def file_dialog(self, path, *args, **kwargs):
        self.widget.line_edit_path.setText(path)

    @present_exceptions("File open error", "The following error occurred when opening the file")
    def load_file(self, *args, **kwargs):
        shm = SharedMemory(create=True, size=5 * np.dtype('<U64').itemsize)

        # get array metadata, shared memory buffer name, dtype, and shape
        array_metadata = np.ndarray(shape=(5,), dtype=np.dtype('<U64'), buffer=shm.buf)

        importer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_inscopix_importer.py')

        file_path = self.widget.line_edit_path.text()

        cmd = ['python', importer_path, '--isx-path', file_path, '--shm-meta-array-name', shm.name]
        print(cmd)
        proc = Popen(
            cmd,
            env=os.environ.copy()
        )
        proc.wait()

        # read the metadata
        name = array_metadata[0]
        dtype = array_metadata[1]
        shape = array_metadata[2]

        # open the shared buffer
        existing_shm = SharedMemory(name=array_metadata[0])

        shape = tuple(map(int, shape.split(',')))

        _imgseq = np.ndarray(shape, dtype=np.dtype(dtype), buffer=existing_shm.buf)

        imgseq = np.zeros(shape=shape, dtype=np.dtype(dtype))
        imgseq[:] = _imgseq[:]

        d = \
            {
                'fps': float(array_metadata[3]),
                'origin': array_metadata[4],
                'date': '00000000_000000'
            }

        imgdata = ImgData(imgseq, d)

        self.vi.viewer.workEnv = ViewerWorkEnv(imgdata)
        self.vi.update_workEnv()

        existing_shm.close()

