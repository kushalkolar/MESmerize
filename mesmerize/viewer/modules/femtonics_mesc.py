"""
Module for importing data from MESc HDF5 files created from Femtonics microscopes.
"""

from .pytemplates.femtonics_mesc_template import *
import h5py
from datetime import datetime
import os
from ...common.qdialogs import use_open_file_dialog, present_exceptions
from ..core import ViewerUtils, ViewerWorkEnv
from ..core.data_types import ImgData
from typing import List, Union
from re import sub as regex_sub
from ...pyqtgraphCore import PlotWidget
import numpy as np
from cv2 import bitwise_not


def ascii_to_str(array: np.ndarray):
    """
    Get a string from an array of ascii integers

    :param array: array of integers representing ascii chars
    :return: string represented by the array
    """
    return ''.join(
        map(
            chr, filter(None, array)
        )
    )


# Navigator object which helps control the
# user's file navigation through the .mesc file
class MEScNavigator(QtWidgets.QWidget):
    # emitted every time the hdf path changes
    # used by ModuleGUI() to determine if Import Image button should be enabled
    sig_hpath_changed: QtCore.pyqtSignal = QtCore.pyqtSignal(dict)  #: emitted every time the hdf path changes

    sig_channel_doubleclicked: QtCore.pyqtSignal = QtCore.pyqtSignal(dict)  #: emitted when a ``Channel`` or ``Curve`` item is double clicked

    def __init__(self, parent, list_widgets: List[ListWidget]):
        """
        :param parent: parent dockWidget
        :param list_widgets: list of ListWidget ui objects, in the following order:
                             [sessions_list_widget, units_list_widget, channels_list_widget]
        """
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.path: str = ''  #: system path to the hdf5 file
        self.file: h5py.File = None  #: h5py file handle

        self.session: str = ''  #: currently selected MSession
        self.sessions: List[str] = []  #: list of ``MSession`` options available in current file
        self.listw_sessions: ListWidget = list_widgets[0]  #: ui list of ``MSession`` options
        self.listw_sessions.itemClicked.connect(self.set_session)  #: sets the current ``MSession``
        self.listw_sessions.currentItemChanged.connect(self.set_session)

        self.unit: str = ''  #: currently selected ``MUnit``
        self.units: List[str] = []  #: list of ``MUnit`` options available in current ``MSession``
        self.listw_units: ListWidget = list_widgets[1]  #: ui list of ``MUnit`` options
        self.listw_units.itemClicked.connect(self.set_unit)  #: sets the current MUnit
        self.listw_units.currentItemChanged.connect(self.set_unit)

        self.channel: str = ''  #: currently selected ``Channel``
        self.channels: List[str] = []  #: list of ``Channel`` options available in current ``MUnit``
        self.listw_channels: ListWidget = list_widgets[2]  #: ui list of ``Channel`` options
        self.listw_channels.itemClicked.connect(self.set_channel)  #: sets the current ``Channel``
        self.listw_channels.currentItemChanged.connect(self.set_channel)
        self.listw_channels.itemDoubleClicked.connect(self._channel_clicked)

    def set_file_path(self, path: str):
        """
        set the path to the .mesc file

        :param path: path to the .mesc hdf5 file
        """
        f = h5py.File(path, mode='r')

        # Check if "MSession_X" keys exist in the file
        has_session_key = any(
            k.startswith('MSession') for k in f.keys()
        )

        if not has_session_key:
            raise TypeError(
                "The chosen file does not appear to be a valid "
                "`.mesc` file since it does not contain any "
                "'MSession_X' data group(s)."
            )

        self.path = path
        self.file = f

        # just clear out everything
        self.session: str = ''
        self.sessions: List[str] = list(self.file.keys())
        self._sort_list(self.sessions)
        self.listw_sessions.setItems(self.sessions)

        self.unit: str = ''
        self.units: List[str] = []
        self.listw_units.clear()

        self.channel: str = ''
        self.channels: List[str] = []
        self.listw_units.clear()

        self.sig_hpath_changed.emit(self.get_hpath(dict))

    def close_file(self):
        """
        Close the h5py file handle that is currently open.
        """
        if self.file is None:
            raise ValueError(
                'No file is currently open'
            )

        # close the hpy file handle
        self.file.close()

        # reset attributes to None
        self.file = None
        self.path = ''

        self.session: str = ''
        self.sessions: List[str] = []
        self.listw_sessions.clear()

        self.unit: str = ''
        self.units: List[str] = []
        self.listw_units.clear()

        self.channel: str = ''
        self.channels: List[str] = []
        self.listw_channels.clear()

        self.sig_hpath_changed.emit(self.get_hpath(dict))

    def set_session(self, key: Union[str, QtWidgets.QListWidgetItem]):
        """
        Set the MSession option

        :param key: a valid ``MSession``
        :return:
        """
        key = self._get_listw_text(key)
        if key is None:
            return

        if key not in self.sessions:
            raise KeyError(f"Session <{key}> not found in current file")

        self.session = key

        self.unit = ''
        self.units = list(self.file[self.session].keys())
        self._sort_list(self.units)
        self.listw_units.setItems(self.units)

        self.channel = ''
        self.channels: List[str] = []
        self.listw_channels.clear()

        self.sig_hpath_changed.emit(self.get_hpath(dict))

    def set_unit(self, key: Union[str, QtWidgets.QListWidgetItem]):
        """
        Set the MUnit option

        :param key: a valid ``MUnit``
        :return:
        """
        key = self._get_listw_text(key)
        if key is None:
            return

        if isinstance(key, QtWidgets.QListWidgetItem):
            key = key.text()

        if key not in self.units:
            raise KeyError(f"Unit <{key}> not found in current MSession")

        self.unit = key

        self.channel = ''
        self.channels = list(self.file[self.session][self.unit].keys())
        self._sort_list(self.channels)
        self.listw_channels.setItems(self.channels)
        self.listw_channels.setCurrentRow(0)

        self.sig_hpath_changed.emit(self.get_hpath(dict))

    def set_channel(self, key: Union[str, QtWidgets.QListWidgetItem]):
        """
        Set a Channel or Curve option

        :param key: a valid ``Channel`` or ``Curve``
        :return:
        """
        key = self._get_listw_text(key)
        if key is None:
            return

        if key not in self.channels:
            raise KeyError(f"Channel <{key}> not found in current MUnit")

        self.channel = key

        self.sig_hpath_changed.emit(self.get_hpath(dict))

    def _channel_clicked(self):
        if self.channel:
            self.sig_channel_doubleclicked.emit(self.get_hpath(dict))

    def get_hpath(self, astype: type) -> Union[str, list, dict]:
        """
        get the current hdf path

        :param astype: one of `str`, `list`, or `dict`
        :return: the hdf path as the chosen data type
        """
        path = [self.session, self.unit, self.channel]

        if astype is str:
            return '/'.join(
                filter(None, path)
            )

        elif astype is list:
            return path

        elif astype is dict:
            return {
                'session':  self.session,
                'unit':     self.unit,
                'channel': self.channel
            }

    def _get_listw_text(self, item: [str, QtWidgets.QListWidgetItem]) -> str:
        if isinstance(item, QtWidgets.QListWidgetItem):
            return item.text()
        else:
            return item

    def _sort_list(self, l: list):
        l.sort(
            key=lambda name: int(
                regex_sub(r"[^0-9]*", '', name)
            )
        )


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_ref):  # when a ModuleGUI() is instantiated the
                                             # Viewer Window passes the viewer reference (viewer_ref)
                                             # which can be used to interface with the viewer
        self.vi = ViewerUtils(viewer_ref)  # this is used to interface with the viewer
        QtWidgets.QDockWidget.__init__(self, parent)

        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)
        self.setWindowTitle('.mesc importer')

        self.ui.pushButton_open_file.clicked.connect(self.set_file)
        self.ui.pushButton_close_file.clicked.connect(self.close_file)
        self.ui.pushButton_import_image.clicked.connect(self.import_recording)

        # the list widgets for navigation
        list_widgets = [
            self.ui.listWidget_session,
            self.ui.listWidget_unit,
            self.ui.listWidget_channel
        ]

        self.mesc_navigator = MEScNavigator(self, list_widgets)  #: instance of ``MEScNavigator``
        self.mesc_navigator.sig_hpath_changed.connect(self._set_comment_line)
        self.mesc_navigator.sig_hpath_changed.connect(self._enable_import_button)

        self.mesc_navigator.sig_channel_doubleclicked.connect(
            self._channel_doubleclicked
        )

        self.plot_widgets = []  #: list of plot widgets

    @present_exceptions(
        'Could not load file',
        'The following error occurred while trying to load hte .mesc file.'
    )
    @use_open_file_dialog('Choose .mesc file', None, ['*.mesc'])
    def set_file(self, path: str, *args):
        """
        Create an h5py file handle from the `.mesc` file at the given ``path``.

        *args are not used, its just there for compatibility with the decorator.

        :param path: path to the `.mes` file
        :type path: str
        :param args: not used
        """
        self.mesc_navigator.set_file_path(path)

        # set the name of the current file in the GUI label
        self.ui.label_current_file_name.setText(
            os.path.basename(path)
        )

    @present_exceptions(
        'Could not close file',
        'The following error occurred while trying to close the file handle.'
    )
    def close_file(self, *args):
        """
        Close the file handle

        :param args: *args not used, just there for compatibility with the decorator
        """
        self.mesc_navigator.close_file()
        self.ui.label_current_file_name.clear()

    def _enable_import_button(self, hpath: dict):
        if hpath['channel']:
            self.ui.pushButton_import_image.setEnabled(True)
            self.ui.pushButton_import_stim_map.setEnabled(True)

        else:
            self.ui.pushButton_import_image.setEnabled(False)
            self.ui.pushButton_import_stim_map.setEnabled(False)

    def _channel_doubleclicked(self, hpath: dict):
        if hpath['channel'].startswith('Channel'):
            self.import_recording()

        elif hpath['channel'].startswith('Curve'):
            f = self.mesc_navigator.file
            hpath = self.mesc_navigator.get_hpath(str)

            ys = f[hpath]['CurveDataYRawData'][()]

            if 'CurveDataXRawData' in f[hpath].keys():
                xs = f[hpath]['CurveDataXRawData'][()]
            else:
                xs = np.arange(ys.size)

            pw = PlotWidget(parent=None)
            pw.plot(xs, ys, title=hpath)
            pw.show()

            self.plot_widgets.append(pw)

    def _set_comment_line(self, hpath: dict):
        if hpath['unit']:
            f = self.mesc_navigator.file
            comment = f[hpath['session']][hpath['unit']].attrs['Comment']
            comment = ascii_to_str(comment)
            self.ui.lineEdit_comment.setText(comment)

        else:
            self.ui.lineEdit_comment.clear()

    @present_exceptions(
        'Could not import recording',
        'The following error occurred while trying to import the chosen recording'
    )
    def import_recording(self, *args):
        """
        Imports the chosen recording into the Viewer Work Environment based
        on the user selected hpath from the list widgets

        *args not used, just there for compatibility with the decorator
        """
        if not self.vi.discard_workEnv():
            return

        # Load the image sequence stored in this `MUnit_X`
        f = self.mesc_navigator.file  # hdf file handle
        hpath = self.mesc_navigator.get_hpath(str)  # hdf path
        img_seq = bitwise_not(  # load & invert image array
            f[hpath][()]
        )

        sess = self.mesc_navigator.get_hpath(dict)['session']
        unit = self.mesc_navigator.get_hpath(dict)['unit']
        # get the time for a single frame
        frame_time = \
            f[sess][unit].attrs['ZAxisConversionConversionLinearScale'] + \
            f[sess][unit].attrs['ZAxisConversionConversionLinearOffset']

        z_units = ascii_to_str(f[sess][unit].attrs['ZAxisConversionUnitName'])
        if z_units != 'ms':
            raise TypeError(f"Z-axis units <{z_units}> not supported")

        # get the sampling rate
        fps = 1 / (frame_time / 1000)  # for now just assuming the frame time are always in milliseconds

        # get the date of the recording
        date = datetime.fromtimestamp(
            f[sess][unit].attrs['MeasurementDatePosix']
        )

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

        # set the "Current Image sequence" in the Viewer
        self.vi.viewer.ui.label_curr_img_seq_name.setText(hpath)
