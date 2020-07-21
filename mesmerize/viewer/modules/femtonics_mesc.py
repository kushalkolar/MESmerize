"""
Module for importing data from MESc HDF5 files created from Femtonics microscopes.
"""

from PyQt5 import QtCore, QtWidgets
import h5py
from datetime import datetime
from ...common.qdialogs import use_open_file_dialog, present_exceptions
from ..core import ViewerUtils, ViewerWorkEnv
from ..core.data_types import ImgData
from typing import List, Union


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref: ViewerUtils):
        self.vi = viewer_ref
        QtWidgets.QDockWidget.__init__(self, parent)

        self.setFloating(True)

        self.vlayout = QtWidgets.QVBoxLayout()
        self.hlayout_btns = QtWidgets.QHBoxLayout()

        self.btn_open_file = QtWidgets.QPushButton(self)
        self.btn_open_file.setText('Open File')
        self.btn_open_file.clicked.connect(self.set_file)
        self.hlayout_btns.addWidget(self.btn_open_file)

        self.btn_close_file = QtWidgets.QPushButton(self)
        self.btn_close_file.setText('Close File')
        self.btn_close_file.setToolTip('Close the file handle, allows the file to be accessible by other programs')
        self.btn_close_file.clicked.connect(self.close_file)
        self.hlayout_btns.addWidget(self.btn_close_file)

        self.vlayout.addLayout(self.hlayout_btns)

        self.listwidget_recordings = QtWidgets.QListWidget(self)
        self.listwidget_recordings.setToolTip('Double click on a recording to import it into the Viewer')
        self.listwidget_recordings.itemDoubleClicked.connect(self.import_recording)
        self.vlayout.addWidget(self.listwidget_recordings)

        # self.btn_load_recording = QtWidgets.QPushButton(self)
        # self.btn_load_recording.setText('Load Selected Recording')
        # self.btn_load_recording.clicked.connect(self.import_recording)
        # self.vlayout.addWidget(self.btn_load_recording)

        self.current_file: h5py.File = None
        self.current_recordings: List[str] = None

    @present_exceptions(
        'Could not load file',
        'The following error occurred while trying to load hte .mesc file.'
    )
    @use_open_file_dialog('Choose .mesc file', None, ['*.mesc'])
    def set_file(self, path, *args):
        f = h5py.File(path)

        if 'MSession_0' not in f.keys():
            raise TypeError(
                "The chosen file does not appear to be a valid "
                "`.mesc` file since it does not contain the "
                "'MSession_0' data group."
            )

        self.current_file = f
        self.current_recordings = list(f.keys())

        self.listwidget_recordings.setItems(self.current_recordings)

    @present_exceptions(
        'Could not close file',
        'The following error occurred while trying to close the file handle.'
    )
    def close_file(self):
        if self.current_file is None:
            raise ValueError(
                'No file is currently open'
            )

        self.current_file.close()

        self.current_file = None
        self.current_recordings = None

    @present_exceptions(
        'Could not import recording',
        'The following error occurred while trying to import the chosen recording'
    )
    def import_recording(self, item: Union[QtWidgets.QListWidgetItem, str]):
        if not self.vi.discard_workEnv():
            return

        if isinstance(item, QtWidgets.QListWidgetItem):
            item = item.text()

        img_seq = self.current_file['MSession_0'][item]['Channel_0']

        frame_time = \
            self.current_file['MSession_0'][item].attrs['ZAxisConversionConversionLinearScale'] + \
            self.current_file['MSession_0'][item].attrs['ZAxisConversionConversionLinearOffset']

        fps = 1 / (frame_time / 1000)  # assuming the frame time are always in milliseconds

        date = datetime.fromtimestamp(self.current_file['MSession_0'][item].attrs['MeasurementDatePosix'])
        date_str = date.strftime('%Y%m%d_%H%M%S')

        meta = \
            {
                'fps': fps,
                'source': 'femtonics .mesc',
                'date': date_str,
            }

        imgdata = ImgData(img_seq.T, meta)

        self.vi.viewer.workEnv = ViewerWorkEnv(imgdata)
        self.vi.update_workEnv()
