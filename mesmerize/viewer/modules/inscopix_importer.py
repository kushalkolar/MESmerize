import isx
import numpy as np
from ...common.qdialogs import *
from ..core.common import ViewerUtils
from PyQt5 import QtWidgets
from ..core import ViewerWorkEnv
from ..core.data_types import ImgData


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        QtWidgets.QDockWidget.__init__(self, parent)

        self.vboxlayout = QtWidgets.QVBoxLayout(self)
        self.hboxlayout = QtWidgets.QHBoxLayout(self)

        self.label_choose_file = QtWidgets.QLabel()
        self.label_choose_file.setText("Choose `.isxd` file")
        self.vboxlayout.addWidget(self.label_choose_file)

        self.line_edit_path = QtWidgets.QLineEdit()
        self.line_edit_path.setPlaceholderText("Path to `.isxd` file")
        self.hboxlayout.addWidget(self.line_edit_path)

        self.btn_open_file_dialog = QtWidgets.QPushButton()
        self.btn_open_file_dialog.setText("...")
        self.hboxlayout.addWidget(self.btn_open_file_dialog)

        self.vboxlayout.addLayout(self.hboxlayout)

        self.btn_load_file = QtWidgets.QPushButton()
        self.btn_load_file.setText("Load File")
        self.btn_load_file.clicked.connect(self.load_file)
        self.vboxlayout.addWidget(self.btn_load_file)

        self.movie: isx.Movie = None

    @present_exceptions("File open error", "The following error occurred when opening the file")
    @use_open_file_dialog("Choose .isxd file", "", exts=["*.isxd"])
    def load_file(self, path, *args, **kwargs):
        self.movie = isx.Movie.read(path)

        meta = self.movie.get_acquisition_info()
        # organize into mesmerize format
        d = \
            {
                'fps': 1000 / self.movie.timing.period.to_msecs(),
                'origin': meta['Microscope Type'],
                'date': "00000000_000000",
                'orig_meta': meta,
            }

        nframes = self.movie.timing.num_samples
        frame0 = self.movie.get_frame_data(0)

        # preallocate empty array of correct shape
        imgseq = np.zeros(shape=(*frame0, nframes), dtype=self.movie.data_type)
        imgdata = ImgData(imgseq, d)

        self.vi.viewer.workEnv = ViewerWorkEnv(imgdata)
        self.vi.update_workEnv()
