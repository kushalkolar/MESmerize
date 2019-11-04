# -*- coding: utf-8 -*-
# from . import functions
from .common import *
from ....analysis.data_types import *
from caiman.source_extraction.cnmf.utilities import detrend_df_f
from ....analysis.stimulus_extraction import StimulusExtraction


class ExtractStim(CtrlNode):
    """Extract portions of curves according to stimulus maps"""
    nodeName = 'ExtractStim'
    # Cannot use QComboBox for Stim_type since it leads to a stack overflow in Node.__getattr__ when removing or clearing the combobox
    uiTemplate = [('data_column', 'combo', {}),
                  ('Stim_Type', 'combo', {}),
                  ('Stimulus', 'lineEdit', {'placeHolder': 'Stimulus', 'text': ''}),
                  ('start_offset', 'doubleSpin', {'min': -999999.0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('end_offset', 'doubleSpin', {'min': -999999.0, 'max': 999999.99, 'value': 0, 'step': 1}),
                  ('zero_pos', 'combo', {'values': ['start_offset', 'stim_end', 'stim_center']}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        # self.transmission = transmission
        self.t = transmission
        self.set_data_column_combo_box()
        self.ctrls['Stim_Type'].setItems(self.t.STIM_DEFS)

        # ac = QtWidgets.QCompleter(self.transmission.STIM_DEFS, self.ctrls['Stim_Type'])
        # self.ctrls['Stim_Type'].setCompleter(ac)
        # self.ctrls['Stim_Type'].setToolTip('\n'.join(self.transmission.STIM_DEFS))

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        data_column = self.ctrls['data_column'].currentText()

        stim_def = self.ctrls['Stim_Type'].currentText()
        stim_tag = self.ctrls['Stimulus'].text()
        start_offset = self.ctrls['start_offset'].value()
        end_offset = self.ctrls['end_offset'].value()
        zero_pos = self.ctrls['zero_pos'].currentText()

        stim_extractor = StimulusExtraction(self.t, data_column, stim_def, start_offset, end_offset, zero_pos)

        self.t = stim_extractor.extract()

        params = {'stim_type': stim_def,
                  'stimulus': stim_tag,
                  'start_offset': start_offset,
                  'end_offset': end_offset,
                  'zero_pos': zero_pos
                  }

        self.t.history_trace.add_operation('all', operation='extract_stim', parameters=params)
        self.t.last_output = '_st_curve'

        return self.t


# class ROI_TagFilter(CtrlNode):
#     """Pass-through DataFrame rows if they have the chosen tags"""
#     nodeName = 'ROI_TagFilter'
#     # Cannot use QComboBox for ROI_Type since it leads to a stack overflow in Node.__getattr__ when removing or clearing the combobox
#     uiTemplate = [('ROI_Type', 'combo', {}),
#                   # ('availTags', 'label', {'toolTip': 'All tags found under this ROI_Def'}),
#                   ('ROI_Tag', 'combo', {}),
#                   ('Include', 'radioBtn', {'checked': True}),
#                   ('Exclude', 'radioBtn', {'checked': False}),
#                   ('Apply', 'check', {'checked': False, 'applyBox': True})
#                   ]
#
#     def __init__(self, name):
#         CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}})
#         self.ctrls['ROI_Type'].currentIndexChanged.connect(self._setAvailTags)
#         # QtWidgets.QComboBox.currentInde
#         # self.ctrls['ROI_Type'].returnPressed.connect(self._setAvailTags)
#
#     def _setAvailTags(self):
#         try:
#             roi_type = self.ctrls['ROI_Type'].currentText()
#             avail_tags = list(set(self.t.df[roi_type]))
#             self.ctrls['ROI_Tag'].setItems(avail_tags)
#         except:
#             pass
#
#     # try:
#     #         tags = list(set(self.transmission.df[self.ctrls['ROI_Type'].text()]))
#     #     except (KeyError, IndexError) as e:
#     #         QtWidgets.QMessageBox.warning(None, 'ROI type not found',
#     #                                       'The ROI type which you have entered'
#     #                                       ' does not exist in the incoming dataframe\n' + str(e))
#     #         return
#     #     self.ctrls['availTags'].setText(', '.join(tags))
#     #     self.ctrls['availTags'].setToolTip('\n'.join(tags))
#     #     self._setROITagAutoCompleter(tags)
#     #
#     # def _setROITagAutoCompleter(self, tags):
#     #     ac = QtWidgets.QCompleter(tags, self.ctrls['ROI_Tags'])
#     #     self.ctrls['ROI_Tags'].setCompleter(ac)
#
#     def processData(self, transmission: Transmission):
#         self.t = transmission
#         # self.set_data_column_combo_box()
#
#         self.ctrls['ROI_Type'].setItems(self.t.ROI_DEFS)
#         self._setAvailTags()
#         # ac = QtWidgets.QCompleter(self.tran/smission.ROI_DEFS, self.ctrls['ROI_Type'])
#         # self.ctrls['ROI_Type'].setCompleter(ac)
#         # self.ctrls['ROI_Type'].setToolTip('\n'.join(self.transmission.ROI_DEFS))
#         if self.ctrls['Apply'].isChecked() is False:
#             return
#
#         self.t = transmission.copy()
#
#         roi_type = self.ctrls['ROI_Type'].currentText()
#         roi_tag = self.ctrls['ROI_Tag'].currentText()
#
#         include = self.ctrls['Include'].isChecked()
#         exclude = self.ctrls['Exclude'].isChecked()
#
#         params = {'roi_type': roi_type,
#                   'roi_tag': roi_tag,
#                   'include': include,
#                   'exclude': exclude
#                   }
#
#         if include:
#             self.t.df = self.t.df[self.t.df[roi_type] == roi_tag]
#         elif exclude:
#             self.t.df = self.t.df[self.t.df[roi_type] != roi_tag]
#
#         self.t.history_trace.add_operation(data_block_id='all', operation='roi_tag_filter', parameters=params)
#
#         return self.t


        # chosen_tags = [tag.strip() for tag in self.ctrls['ROI_Tags'].text().split(',')]
        #
        # t = self.transmission.copy()
        # '''***************************************************************************'''
        # TODO: CHECK IF THIS IS ACTUALLY DOING THE RIGHT THING!!!!
        # if self.ctrls['Include'].isChecked():
        #     t.df = t.df[t.df[self.ctrls['ROI_Type'].text()].isin(chosen_tags)]
        #     prefix = 'include tags'
        # elif self.ctrls['Exclude'].isChecked():
        #     t.df = t.df[~t.df[self.ctrls['ROI_Type'].text()].isin(chosen_tags)]
        #     prefix = 'exclude tags'
        # '''***************************************************************************'''
        #
        # params = {'ROI_DEF': self.ctrls['ROI_Type'].text(),
        #           prefix: chosen_tags}
        #
        # t.src.append({'ROI_Include': params})

        # return t


# class DeltaFoF(CtrlNode):
#     uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
#                   ('OpenGUI', 'button', {'text': 'Open GUI'})]
#
#     def __init__(self, name, **kwargs):
#         CtrlNode.__init__(self, name, terminals={'Derivative': {'io': 'in'},
#                                                  'Curve': {'io': 'in'},
#                                                  'Out': {'io': 'out', 'bypass': 'Curve'}}, **kwargs)
#         self.data_modified = False
#         self.editor_output = False
#         self.ctrls['Edit'].clicked.connect(self._peak_editor)


class DetrendDFoF(CtrlNode):
    """Uses detrend_df_f from Caiman library."""
    nodeName = 'DetrendDFoF'
    uiTemplate = [('quantileMin', 'intSpin', {'min': 1, 'max': 100, 'step': 1, 'value': 20}),
                  ('frames_window', 'intSpin', {'min': 2, 'max': 5000, 'step': 10, 'value': 100}),
                  ('auto_quantile', 'check', {'checked': True, 'toolTip': 'determine quantile automatically'}),
                  ('fast_filter', 'check', {'checked': True, 'tooTip': 'use approximate fast percentile filtering'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})]

    def processData(self, transmission: Transmission):
        if self.ctrls['Apply'].isChecked() is False:
            return
        self.t = transmission.copy()
        # self.df = t.df

        self.params = {'quantileMin': self.ctrls['quantileMin'].value(),
                       'frames_window': self.ctrls['frames_window'].value(),
                       'auto_quantile': self.ctrls['auto_quantile'].isChecked(),
                       'fast_filter': self.ctrls['fast_filter'].isChecked(),
                       'output_column': '_DETREND_DF_O_F'
                       }

        self.t.df.sort_values(by=['SampleID', 'CurvePath'], inplace=True)
        self.t.df = self.t.df.reset_index(drop=True)

        self._load_data()

        self.t.history_trace.add_operation('all', operation='detrend_df_o_f', parameters=self.params)
        self.t.last_output = '_DETREND_DF_O_F'

        return self.t

    def _load_data(self):
        self.current_sample_id = None
        self.ix = 0
        dfof_curves = None

        proj_path = self.t.get_proj_path()
        self.t.df['_DETREND_DF_O_F'] = [np.array([], dtype=np.float64)] * self.t.df.index.size
        for index, row in self.t.df.iterrows():
            self.ix += 1

            if row['SampleID'] != self.current_sample_id:
                self.idx_components = None
                self.ix = 0
                dfof_curves = None

                self.current_sample_id = row['SampleID']

                pikPath = os.path.join(proj_path, row['ImgInfoPath'])
                pik = pickle.load(open(pikPath, 'rb'))

                cnmA = pik['roi_states']['cnmf_output']['cnmA']
                cnmb = pik['roi_states']['cnmf_output']['cnmb']
                cnmC = pik['roi_states']['cnmf_output']['cnmC']
                cnm_f = pik['roi_states']['cnmf_output']['cnm_f']
                cnmYrA = pik['roi_states']['cnmf_output']['cnmYrA']

                self.idx_components = pik['roi_states']['cnmf_output']['idx_components']
                try:
                    dfof_curves = detrend_df_f(cnmA, cnmb, cnmC, cnm_f, YrA=cnmYrA,
                                               quantileMin=self.params['quantileMin'],
                                               frames_window=self.params['frames_window'])  # ,
                    # self.dfof_curves = dfof_curves
                except:
                    tb = traceback.format_exc()
                    raise Exception('The following exception was raised in caiman detrend_df_f method for SampleID: '
                                    + self.current_sample_id + '\n\n' + tb)
                # flag_auto=self.ctrls['auto_quantile'].isChecked(),
                # use_fast=self.ctrls['fast_filter'].isChecked())
                if self.idx_components[self.ix] != row['ROI_State']['cnmf_idx']:
                    raise Exception(
                        'CNMF component index Mismatch Error! Something went very wrong. Check the indices of your '
                        'CNMF components from SampleID: ' + self.current_sample_id +
                        '\nIndex in pickle is: ' + str(self.idx_components[self.ix]) +
                        '\nIndex in dataframe is: ' + str(row['ROI_State']['cnmf_idx']) + '\n at iloc: ' + str(index))

            self.t.df.at[index, '_DETREND_DF_O_F'] = dfof_curves[self.idx_components[self.ix]]


class StaticDFoFo(CtrlNode):
    """Perform (F - Fo / Fo) without a rolling window to find Fo"""
    nodeName = 'StaticDFoFo'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        data_column = self.ctrls['data_column'].currentText()
        output_column = '_STATIC_DF_O_F'
        params = {'data_column': data_column}

        self.t.df[output_column] = self.t.df[data_column].apply(lambda a: self._static_dfof(a))

        self.t.history_trace.add_operation(data_block_id='all', operation='static_df_o_f', parameters=params)
        self.t.last_output = output_column

        return self.t

    def _static_dfof(self, F: np.ndarray) -> np.ndarray:
        Fo = np.min(F)
        d = ((F - Fo) / Fo)
        return d


class ManualDFoF(CtrlNode):
    """Set Fo for dF/Fo using a particular time period. Useful for looking at stimulus responses"""
    nodeName = 'ManualDFoF'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {}),
                  ('OpenGUI', 'button', {'text': 'OpenGUI'})]
