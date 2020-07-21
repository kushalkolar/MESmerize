"""
Module for importing data from MESc HDF5 files created from Femtonics microscopes.
"""

from PyQt5 import QtCore, QtWidgets
import h5py
from datetime import datetime
import os
from ...common.qdialogs import use_open_file_dialog, present_exceptions
from ..core import ViewerUtils, ViewerWorkEnv
from ..core.data_types import ImgData
from typing import List, Union
from re import sub as regex_sub


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref: ViewerUtils):  # when a ModuleGUI() is instantiated the
                                                          # Viewer Window passes the viewer reference (viewer_ref)
                                                          # which can be used to interface with the viewer
        self.vi = ViewerUtils(viewer_ref)  # this is used to interface with the viewer
        QtWidgets.QDockWidget.__init__(self, parent)

        # setup the GUI layout
        self.setFloating(True)
        self.setWindowTitle('.mesc importer')

        self.widget = QtWidgets.QWidget(self)

        self.vlayout = QtWidgets.QVBoxLayout(self.widget)
        self.hlayout_btns = QtWidgets.QHBoxLayout(self.widget)

        self.btn_open_file = QtWidgets.QPushButton(self)
        self.btn_open_file.setText('Open File')
        self.btn_open_file.clicked.connect(self.set_file)
        self.hlayout_btns.addWidget(self.btn_open_file)

        self.btn_close_file = QtWidgets.QPushButton(self)
        self.btn_close_file.setText('Close File')
        self.btn_close_file.setToolTip(
            'Close the file handle, allows the file to be accessible by other programs'
        )
        self.btn_close_file.clicked.connect(self.close_file)
        self.hlayout_btns.addWidget(self.btn_close_file)

        self.qlabel_current_file_name = QtWidgets.QLabel(self)
        self.vlayout.addWidget(self.qlabel_current_file_name)

        self.vlayout.addLayout(self.hlayout_btns)

        self.listwidget_recordings = QtWidgets.QListWidget(self)
        self.listwidget_recordings.setToolTip(
            'Double click on a recording to import it into the Viewer'
        )
        self.listwidget_recordings.itemDoubleClicked.connect(self.import_recording)
        self.vlayout.addWidget(self.listwidget_recordings)

        self.setWidget(self.widget)

        self.current_file: h5py.File = None  #: h5py file handle to the `.mesc` file
        self.current_recordings: List[str] = None  #: list of `MUnit_X` recordings in the current file

    @present_exceptions(
        'Could not load file',
        'The following error occurred while trying to load hte .mesc file.'
    )
    @use_open_file_dialog('Choose .mesc file', None, ['*.mesc'])
    def set_file(self, path: str, *args):
        """
        Create an h5py file handle from the `.mesc` file at the given ``path``.

        *args are not used, its just there because it's passed through the btn_open_file.clicked signal.

        :param path: path to the `.mes` file
        :type path: str
        :param args: not used
        """
        # Create the file handle
        f = h5py.File(path, mode='r')

        if 'MSession_0' not in f.keys():
            raise TypeError(
                "The chosen file does not appear to be a valid "
                "`.mesc` file since it does not contain the "
                "'MSession_0' data group."
            )

        # close previous file handle if present
        if self.current_file is not None:
            self.current_file.close()

        # attribute to access the current file handle
        self.current_file = f

        # get a list of the `MUnit_X` recordings stored in this file
        self.current_recordings = list(f['MSession_0'].keys())

        # numerically sort the list of recordings
        self.current_recordings.sort(
            key=lambda name: int(
                regex_sub(r"[^0-9]*", '', name)
            )
        )

        # set the list widget with the current_recordings
        self.listwidget_recordings.addItems(self.current_recordings)

        # set the name of the current file in the GUI label
        self.qlabel_current_file_name.setText(
            os.path.basename(path)
        )

    @present_exceptions(
        'Could not close file',
        'The following error occurred while trying to close the file handle.'
    )
    def close_file(self, *args):
        """
        Close the h5py file handle that is currently open.

        *args are not used, its just there because it's passed through the btn_close_file.clicked signal.

        :param args: not used
        :return:
        """
        if self.current_file is None:
            raise ValueError(
                'No file is currently open'
            )

        # close the hpy file handle
        self.current_file.close()

        # reset attributes to None
        self.current_file = None
        self.current_recordings = None

        # clear the GUI
        self.listwidget_recordings.clear()
        self.qlabel_current_file_name.clear()

    @present_exceptions(
        'Could not import recording',
        'The following error occurred while trying to import the chosen recording'
    )
    def import_recording(self, item: Union[QtWidgets.QListWidgetItem, str]):
        """
        Imports the chosen ``MUnit_X`` recording into the Viewer Work Environment.

        :param item: the `MUnit_X` recording to be imported
        :type item: Union[str, QtWidgets.QListWidgetItem]
        :return:
        """
        if not self.vi.discard_workEnv():
            return

        if isinstance(item, QtWidgets.QListWidgetItem):
            item = item.text()

        # Load the image sequence stored in this `MUnit_X`
        img_seq = self.current_file['MSession_0'][item]['Channel_0'][()]

        # get the time for a single frame
        frame_time = \
            self.current_file['MSession_0'][item].attrs['ZAxisConversionConversionLinearScale'] + \
            self.current_file['MSession_0'][item].attrs['ZAxisConversionConversionLinearOffset']

        # get the sampling rate
        fps = 1 / (frame_time / 1000)  # for now just assuming the frame time are always in milliseconds

        # get the date of the recording
        date = datetime.fromtimestamp(self.current_file['MSession_0'][item].attrs['MeasurementDatePosix'])

        # format the date into YYYYMMDD_HHMMSS
        date_str = date.strftime('%Y%m%d_%H%M%S')

        # create a minimal meta data dict that is required for the Viewer Work Environment.
        # the keys ``fps``, ``origin`` and ``date`` are mandatory
        meta = \
            {
                'fps': fps,
                'origin': 'femtonics .mesc',
                'date': date_str,
            }

        # Create an ``ImgData`` object, see the ImgData class under Viewer Core API for more information
        imgdata = ImgData(img_seq.T, meta)

        # Create a new Viewer Work Environment object using this ``ImgData`` object
        self.vi.viewer.workEnv = ViewerWorkEnv(imgdata)

        # Update the GUI according to the new ViewerWorkEnv
        self.vi.update_workEnv()
