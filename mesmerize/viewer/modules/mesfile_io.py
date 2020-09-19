#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 19 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from ..core.common import ViewerUtils
from ..core.viewer_work_environment import ViewerWorkEnv
from .pytemplates.mesfile_io_pytemplate import *
from .stimulus_mapping_mesfile import *
import traceback
import pandas as pd
from .stimulus_mapping import ModuleGUI as StimMapModuleGUI


class ModuleGUI(QtWidgets.QDockWidget):
    def __init__(self, parent, viewer_reference):
        self.vi = ViewerUtils(viewer_reference)
        self.parent = parent

        QtWidgets.QDockWidget.__init__(self, parent)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.ui.btnOpenMesFile.clicked.connect(self.load_mesfile)
        self.ui.listwMesfile.itemDoubleClicked.connect(lambda sel: self.load_mesfile_selection(sel))
        self.ui.btnStimMapGUI.clicked.connect(self.open_stim_map_gui)

        self.stim_map_gui = None
        self.mesfile = None

    def load_mesfile(self):
        if not self.vi.discard_workEnv():
            return

        filelist = QtWidgets.QFileDialog.getOpenFileNames(self, 'Choose ONE mes file', '.', '(*.mes)')

        if len(filelist) == 0:
            return

        try:
            # Creates an instance of MES, see MesmerizeCore.FileInput
            self.mesfile = ViewerWorkEnv.load_mesfile(filelist[0][0])
            self.ui.listwMesfile.setEnabled(True)
            self.ui.listwMesfile.clear()
            # Get the references of the images, their descriptions, and add them to the list
            for i in self.mesfile.get_image_references():
                j = self.mesfile.image_descriptions[i]
                self.ui.listwMesfile.addItem(i + ': ' + j)

            # If Auxiliary voltage info is found in the mes file, ask the user if they want to map these to stimuli
            if len(self.mesfile.voltages_lists_dict) > 0:
                self.stim_map_gui = MesStimmapGUI(parent=None, viewer=self.vi.viewer)
                self.set_stim_map_gui()
                self.ui.btnStimMapGUI.setEnabled(True)
                if QtWidgets.QMessageBox.question(self, '', 'This .mes file contains auxilliary output voltage '
                                                            'information, would you like create Stimulus Maps now?',
                                                  QtWidgets.QMessageBox.Yes,
                                                  QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                    self.open_stim_map_gui()
            else:
                self.ui.btnStimMapGUI.setDisabled(True)

        except (IOError, IndexError) as e:
            QtWidgets.QMessageBox.warning(self, 'IOError or IndexError',
                                          "There is an problem with the files you've selected:\n" + traceback.format_exc(),
                                          QtWidgets.QMessageBox.Ok)
        return

    def load_mesfile_selection(self, s: QtWidgets.QListWidgetItem):
        if not self.vi.discard_workEnv():
            return
        try:
            self.vi.viewer.status_bar_label.showMessage('Loading image sequence from mesfile please wait...')
            self.vi.viewer.workEnv = ViewerWorkEnv.from_mesfile(self.mesfile, s.text().split(': ')[0])
        except KeyError as ke:
            QtWidgets.QMessageBox.warning(self, f'KeyError: {ke}', traceback.format_exc(), QtWidgets.QMessageBox.Ok)
            self.vi.viewer.status_bar_label.clearMessage()
            return

        except Exception:
            QtWidgets.QMessageBox.warning(self, 'Error', 'Error opening the selected ' + \
                                          'image in the currently open mes file.\n' +
                                          traceback.format_exc(), QtWidgets.QMessageBox.Ok)
            self.vi.viewer.status_bar_label.clearMessage()
            return
        self.vi.viewer.ui.label_curr_img_seq_name.setText(s.text())
        self.vi.viewer.status_bar_label.showMessage('Setting Stimulus Map...')
        self.set_stimulus_map()
        self.vi.viewer.status_bar_label.showMessage('Finished setting stimulus map!')
        self.vi.update_workEnv()
        self.vi.enable_ui(True)

    def open_stim_map_gui(self):
        self.stim_map_gui.show()

    def set_stim_map_gui(self):
        for channel in self.mesfile.voltages_lists_dict.keys():
            self.stim_map_gui.add_stim_type(channel)
            for voltage in self.mesfile.voltages_lists_dict[channel]:
                pd_series = pd.Series(data={'voltage': '%.1f' % voltage,
                                            'name': '',
                                            'color': '#FFFFFF'
                                            })
                self.stim_map_gui.tabs[channel].add_row(pd_series)

    def set_stimulus_map(self):
        if self.stim_map_gui.voltage_mappings is None:
            QtWidgets.QMessageBox.information(self, 'Voltage mappings not set',
                                              'You have not set the mesfile voltage -> stimulus mappings')
            return

        smm = self.parent.run_module(StimMapModuleGUI)
        assert isinstance(smm, StimMapModuleGUI)

        stimulus_dataframes = {}
        meta = self.vi.viewer.workEnv.meta['orig_meta']

        voltage_mappings = self.stim_map_gui.voltage_mappings

        for stim_type in voltage_mappings.keys():
            channel = voltage_mappings[stim_type]['channel']

            try:
                y = meta[channel]['y']
                x = meta[channel]['x'][1]

                firstFrameStartTime = meta['FoldedFrameInfo']['firstFrameStartTime']
                frameTimeLength = meta['FoldedFrameInfo']['frameTimeLength']

                current_map = []

                for i in range(0, y.shape[1] - 1):
                    voltage = '%.1f' % y[1][i]

                    tstart_frame = int(((y[0][i] * x) - firstFrameStartTime) / frameTimeLength)

                    if tstart_frame < 0:
                        tstart_frame = 0

                    tend_frame = int(((y[0][i + 1] * x) - firstFrameStartTime) / frameTimeLength)

                    #v = voltage# + ' V: '

                    mapping = voltage_mappings[stim_type]['dataframe'][
                        voltage_mappings[stim_type]['dataframe']['voltage'] == voltage]
                    try:
                        name = mapping['name'].item()
                    except:
                        name = mapping['name']
                    try:
                        color = mapping['color'].item()
                    except:
                        color = mapping['color']

                    current_map.append({'name': name,
                                        'start': tstart_frame,
                                        'end': tend_frame,
                                        'color': color
                                        })
                # stimulus_dataframes[stim_type] = {'units': 'frames', 'dataframe': pd.DataFrame(current_map)}
                stimulus_dataframes[stim_type] = pd.DataFrame(current_map)

            except (KeyError, IndexError):
                QtWidgets.QMessageBox.information(None, 'FYI: Missing channels in current image',
                                                  'Voltage values not found for stimulus type: "' + stim_type + \
                                                  '" in channel <' + channel + '>.\n' + traceback.format_exc())

        smm.set_all_data(stimulus_dataframes)
        print(stimulus_dataframes)
        smm.export_to_work_env()
        try:
            smm.ui.comboBoxShowTimelineChoice.setCurrentIndex(1)
        except:
            pass
