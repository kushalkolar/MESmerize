# -*- coding: utf-8 -*-
from ...Qt import QtGui, QtCore, QtWidgets
from spyder.widgets.variableexplorer.objecteditor import oedit
from .common import *
import traceback
from ....analysis import Transmission
from ....analysis.history_widget import HistoryTreeWidget
from ....common import get_project_manager
from ....common.qdialogs import *
import os
import pickle
from glob import glob
from ....common.configuration import HAS_TSLEARN
if HAS_TSLEARN:
    from tslearn.preprocessing import TimeSeriesScalerMinMax


class LoadProjDF(CtrlNode):
    """Load raw project DataFrames as Transmission"""
    nodeName = 'Load_Proj_DF'
    uiTemplate = [('DF_Name', 'combo'),
                  ('Update', 'button', {'text': 'Update', 'toolTip': 'When clicked this node will update'
                                                                     ' from the project DataFrame'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False}),
                  ('PinDF', 'check', {'text': 'Yes', 'toolTip': 'Pin the DataFrame to the flowchart, this way\n'
                                                                'you can open another project and still propogate\n'
                                                                'the data from this node.'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Out': {'io': 'out'}})
        self._loadNode = True
        self.t = None
        child_df_names = ['root'] + list(get_project_manager().child_dataframes.keys())
        self.ctrls['DF_Name'].addItems(child_df_names)
        self.ctrls['Update'].clicked.connect(self.changed)
        # print('Node Refs:')
        # print(configuration.df_refs)

    def process(self):
        if self.ctrls['Apply'].isChecked() is False:
            return self.t

        # print('#######Weak Refs Dict########')
        # print(configuration.df_refs)

        if self.ctrls['PinDF'].isEnabled():
            if self.ctrls['PinDF'].isChecked():
                # self.t = self.t.copy()
                self.ctrls['PinDF'].setDisabled(True)
                self.ctrls['Update'].setDisabled(True)
                return {'Out': self.t}

            if self.ctrls['DF_Name'].currentText() == '':
                return
            child_df_name = self.ctrls['DF_Name'].currentText()
            if child_df_name == 'root':
                df = get_project_manager().dataframe
                filter_history = None
            else:
                df = get_project_manager().child_dataframes[child_df_name]['dataframe']
                filter_history = get_project_manager().child_dataframes[child_df_name]['filter_history']
            proj_path = get_project_manager().root_dir
            # print('*****************config df ref hex ID:*****************')
            # print(hex(id(df)))
            self.t = Transmission.from_proj(proj_path, df, sub_dataframe_name=child_df_name,
                                            dataframe_filter_history={'dataframe_filter_history': filter_history})

            # print('Tranmission dataframe hexID:')
            # print(hex(id(self.t.df)))

        return {'Out': self.t}


class LoadFile(CtrlNode):
    """Load Transmission data object from pickled file"""
    nodeName = 'LoadFile'
    uiTemplate = [('load_trn', 'button', {'text': 'Open .trn File'}),
                  ('proj_trns', 'combo', {}),
                  ('fname', 'label', {'text': ''}),
                  ('proj_path', 'button', {'text': 'Project Path'}),
                  ('proj_path_label', 'label', {'text': ''})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Out': {'io': 'out'}})
        self.ctrls['load_trn'].clicked.connect(lambda: self.load_file())
        self.ctrls['proj_path'].clicked.connect(self.dir_dialog_proj_path)

        self.t = None
        self._loadNode = True

        proj_path = get_project_manager().root_dir
        
        if proj_path is not None:
            trns = glob(os.path.join(proj_path, 'trns', '*.trn'))
            trns_names = [""] + [os.path.basename(f) for f in trns]
            self.ctrls['proj_trns'].setItems(trns_names)
            self.ctrls['proj_trns'].currentTextChanged.connect(lambda fname: self.load_file(os.path.join(get_project_manager().root_dir, 'trns', fname) if fname else False, qdialog=False))

    # def file_dialog_trn_file(self):
    #     path = QtWidgets.QFileDialog.getOpenFileName(None, 'Import Transmission object', '', '(*.trn *.ptrn)')
    #     if path == '':
    #         return
    #     self.load_file(path[0])

    @use_open_file_dialog('Load Transmission file', None, ['*.trn', '*.ptrn'])
    def load_file(self, path: str, qdialog=True):
        if not path:
            return
        try:
            self.t = Transmission.from_hdf5(path)
        except:
            QtWidgets.QMessageBox.warning(None, 'File open Error!', 'Could not open the chosen file.\n' + traceback.format_exc())
            return

        self.ctrls['fname'].setText(os.path.basename(path))

        proj_path = get_project_manager().root_dir
        if proj_path is not None:
            self._set_proj_path(proj_path)

        # print(self.transmission)
        # self.update()
        self.changed()

    def _set_proj_path(self, path: str):
        self.ctrls['proj_path_label'].setText(os.path.basename(path))
        self.t.set_proj_path(path)
        self.t.set_proj_config()

    def dir_dialog_proj_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Project Folder')

        if path == '':
            return

        try:
            self._set_proj_path(path)
            self.changed()
        except (FileNotFoundError, NotADirectoryError) as e:
            QtWidgets.QMessageBox.warning(None, 'Invalid Project Folder', 'This is not a valid Mesmerize project\n' + e)
            return

    def process(self):
        return {'Out': self.t}


class Save(CtrlNode):
    """Save Transmission data object"""
    nodeName = 'Save'
    uiTemplate = [('saveBtn', 'button', {'text': 'OpenFileDialog'}),
                  ('path', 'label', {'text' : ''}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name):
        # super(Save, self).__init__(name, terminals={'data': {'io': 'in'}})
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}})
        self._bypass = False
        self.bypassButton = None
        self.ctrls['saveBtn'].clicked.connect(self._fileDialog)
        self._saveNode = True
        self.saveValue = None

    def process(self, In, display=True):
        if In is not None:
            self._save(In)
        else:
            raise Exception('No incoming transmission to save!')

    def _fileDialog(self):
        path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Transmission as', '', '(*.trn)')
        if path == '':
            return
        if path[0].endswith('.trn'):
            path = path[0]
        else:
            path = path[0] + '.trn'

        self.ctrls['path'].setText(path)

    def _save(self, transmission):
        # self.ctrls['saveBtn'].clicked.connect(self._fileDialog)
        if self.ctrls['Apply'].isChecked is False:
            return

        if self.ctrls['path'].text() != '':
            try:
                transmission.to_hdf5(self.ctrls['path'].text())
            except:
                QtWidgets.QMessageBox.warning(None, 'File save error', 'Could not save the transmission to file.\n' + traceback.format_exc())


class Merge(CtrlNode):
    """Merge transmissions"""
    nodeName = 'Merge'
    uiTemplate = [('no controls', 'label')]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}, 'Out': {'io': 'out'}})

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        return {'Out': self.t}


class ViewTransmission(CtrlNode):
    """View transmission using the spyder object editor"""
    nodeName = 'ViewData'
    uiTemplate = [('no controls', 'label')]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}})
        # self.edited_transmission = None

    def processData(self, transmission: Transmission):
        self.t = transmission.copy()
        oedit({'dataframe': self.t.df, 'history_trace': self.t.history_trace.history})
        # if self.edited is not None:
        #     self.edited.add_operation('all', 'object_editor', {})
        #     return self.edited

        # return self.t


class DropNa(CtrlNode):
    """Drop NaNs from the DataFrame"""
    nodeName = 'DropNaNs'
    uiTemplate = [('axis', 'combo', {'values': ['row', 'columns'], 'toolTip': 'Choose to drop NaNs from according to all '
                                                                              'rows, columns, or a specific column'}),
                  ('how', 'combo', {'values': ['any', 'all'], 'toolTip': 'any: drop from chosen axis if any element is NaN\n'
                                                                         'all: drop from chosen axis if all elements are NaN'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def __init__(self, *args, **kwargs):
        super(DropNa, self).__init__(*args, **kwargs)

    def processData(self, transmission: Transmission):
        items = ['row', 'columns'] + ['---------'] + transmission.df.columns.to_list()
        self.ctrls['axis'].setItems(items)

        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        axis = self.ctrls['axis'].currentText()

        if self.ctrls['axis'].currentIndex() < 2:
            if axis == 'row':
                axis = 0
            elif axis == 'columns':
                axis = 1

            how = self.ctrls['how'].currentText()
            self.t.df.dropna(axis=axis, how=how, inplace=True)
        else:
            how = None
            self.t.df = self.t.df[~self.t.df[axis].isna()]

        self.t.history_trace.add_operation('all', 'dropna', parameters={'axis': axis, 'how': how})

        return self.t


class ViewHistory(CtrlNode):
    """View History Trace of the input Transmission"""
    nodeName = 'ViewHistory'
    uiTemplate = [('Show', 'button')]

    def __init__(self, *args, **kwargs):
        super(ViewHistory, self).__init__(*args, **kwargs)
        self.history_widget = HistoryTreeWidget()
        self.ctrls['Show'].clicked.connect(self.history_widget.show)

    def processData(self, transmission: Transmission):
        self.history_widget.fill_widget(transmission.history_trace)


class iloc(CtrlNode):
    """Pass only one or multiple DataFrame Indices"""
    nodeName = 'iloc'
    uiTemplate = [('Index', 'intSpin', {'min': 0, 'step': 1, 'value': 0})
                  # ('Indices', 'lineEdit', {'text': '0', 'toolTip': 'Index numbers separated by commas'})
                  ]

    def processData(self, transmission):
        self.ctrls['Index'].setMaximum(transmission.df.index.size - 1)
        # self.ctrls['Index'].valueChanged.connect(
        #     partial(self.ctrls['Indices'].setText, str(self.ctrls['Index'].value())))

        # indices = [int(ix.strip()) for ix in self.ctrls['Indices'].text().split(',')]
        i = self.ctrls['Index'].value()
        self.t = transmission.copy()
        self.t.df = self.t.df.iloc[i]
        # self.t.src.append({'iloc': {'index': i}})
        return self.t


class SpliceArrays(CtrlNode):
    """Splice 1-D numpy arrays in a particular column."""
    nodeName = 'SpliceArrays'
    uiTemplate = [('Apply', 'check', {'checked': True, 'applyBox': True}),
                  ('data_column', 'combo', {}),
                  ('indices', 'lineEdit', {'text': '', 'placeHolder': 'start_ix:end_ix'})]
    output_column = '_SPLICE_ARRAYS'

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()
        indices = self.ctrls['indices'].text()

        if indices == '':
            return
        if ':' not in indices:
            return
        else:
            indices = indices.split(':')

        start_ix = int(indices[0])
        end_ix = int(indices[1])

        data_column = self.ctrls['data_column'].currentText()


        self.t.df[self.output_column] = self.t.df[data_column].apply(lambda a: a[start_ix:end_ix])

        params = {'data_column': data_column,
                  'start_ix': start_ix,
                  'end_ix': end_ix,
                  'units': self.t.last_unit
                  }

        self.t.history_trace.add_operation(data_block_id='all', operation='splice_arrays', parameters=params)
        self.t.last_output = self.output_column

        return self.t


class PadArrays(CtrlNode):
    """Pad 1-D numpy arrays in a particular column"""
    nodeName = 'PadArrays'
    uiTemplate = [('data_column', 'combo', {}),
                  # ('output_size', 'intSpin', {'min': -1, 'max': 9999999, 'step': 100, 'value': -1}),
                  ('method', 'combo', {'items': ['fill-size', 'random']}),
                  ('mode', 'combo', {'items': ['minimum', 'constant', 'edge', 'maximum',
                                               'mean', 'median', 'reflect', 'symmetric', 'wrap'], 'toolTip': 'Passed to numpy.pad "mode" parameter'}),
                  ('constant', 'doubleSpin', {'min': -9999999.9, 'max': 9999999.9, 'value': 1.0, 'step': 10.0,
                                              'tooltip': 'Value to use if "mode" is set to "constant"'}),
                  ('pad_with_nans', 'check', {'checked': False,
                                              'toolTip': 'Pad with nans, only if `mode` is set to `constant`'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        a = self.t.df[self.data_column].values

        method = self.ctrls['method'].currentText()
        mode = self.ctrls['mode'].currentText()
        constant = self.ctrls['constant'].value()
        pad_with_nans = self.ctrls['pad_with_nans'].isChecked()

        if mode == 'constant' and pad_with_nans:
            constant = np.nan

        params = \
            {
                'method': method,
                'mode': mode,
                'constant': constant,
                'pad_with_nans': pad_with_nans
            }

        self.padded_output = self._pad(a, method, mode, constant, pad_with_nans)

        self.t.df['_PADDED'] = self.padded_output.tolist()
        self.t.df['_PADDED'] = self.t.df['_PADDED'].apply(np.array)

        self.t.history_trace.add_operation(data_block_id='all', operation='pad_arrays', parameters=params)
        self.t.last_output = '_PADDED'

        return self.t

    def _pad(self, a, method, mode, constant, pad_with_nans) -> np.ndarray:
        l = 0  # size of largest time series

        # Get size of largest time series
        for c in a:
            s = c.size
            if s > l:
                l = s

        # pre-allocate output array
        p = np.zeros(shape=(a.size, l))

        if mode == 'constant':
            kwargs = \
                {
                    'mode': 'constant',
                    'constant_values': constant
                }
        else:
            kwargs = {'mode': mode}

        # pad each 1D time series
        for i in tqdm(range(p.shape[0])):
            s = a[i].size

            if s == l:
                p[i, :] = a[i]
                continue

            max_pad_en_ix = l - s

            if method == 'random':
                pre = np.random.randint(0, max_pad_en_ix)
            elif method == 'fill-size':
                pre = 0
            else:
                raise ValueError('Must specific method as either "random" or "fill-size"')

            post = l - (pre + s)
            p[i, :] = np.pad(a[i], (pre, post), **kwargs)

        return p


class SelectRows(CtrlNode):
    pass


class SelectColumns(CtrlNode):
    pass


class TextFilter(CtrlNode):
    """Simple string filtering in a specified column"""
    nodeName = 'TextFilter'
    uiTemplate = [('Column', 'combo', {'toolTip': 'Filter according to this column'}),
                  ('filter', 'lineEdit', {'toolTip': 'Filter to apply in selected column'}),
                  ('Include', 'radioBtn', {'checked': True}),
                  ('Exclude', 'radioBtn', {'checked': False}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    # def __init__(self, name):
    #     CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}})
    #     self.ctrls['ROI_Type'].returnPressed.connect(self._setAvailTags)

    def processData(self, transmission: Transmission):
        ccols = organize_dataframe_columns(transmission.df.columns.to_list())[1]
        self.ctrls['Column'].setItems(ccols)
        col = self.ctrls['Column'].currentText()
        completer = QtWidgets.QCompleter(list(map(str, transmission.df[col].unique())))
        self.ctrls['filter'].setCompleter(completer)

        if self.ctrls['Apply'].isChecked() is False:
            return

        filt = self.ctrls['filter'].text()

        self.t = transmission.copy()

        include = self.ctrls['Include'].isChecked()
        exclude = self.ctrls['Exclude'].isChecked()

        params = {'column': col,
                  'filter': filt,
                  'include': include,
                  'exclude': exclude
                  }

        if include:
            self.t.df = self.t.df[self.t.df[col].astype(str) == filt]
        elif exclude:
            self.t.df = self.t.df[self.t.df[col].astype(str) != filt]

        self.t.df = self.t.df.reset_index(drop=True)

        self.t.history_trace.add_operation('all', operation='text_filter', parameters=params)

        return self.t


class NormRaw(CtrlNode):
    """Normalize between raw min and max values."""
    nodeName = 'NormRaw'
    uiTemplate = [('option', 'combo', {'items': ['top_5', 'top_10', 'top_5p', 'top_10p', 'top_25p', 'full_mean']}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False})
                  ]

    def processData(self, transmission: Transmission):
        t = transmission
        dcols = organize_dataframe_columns(t.df.columns)[0]
        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        output_column = '_NORMRAW'

        self.option = self.ctrls['option'].currentText()

        params = {'data_column': '_RAW_CURVE',
                  'option': self.option,
                  'output_column': output_column}

        self.proj_path = self.t.get_proj_path()

        tqdm().pandas()

        self.excluded = 0

        self.t.df[output_column] = self.t.df.progress_apply(lambda r: self._func(r['_RAW_CURVE'], r['ImgInfoPath'], r['ROI_State']), axis=1)

        self.t.history_trace.add_operation('all', 'normrawminmax', params)
        self.t.last_output = output_column

        if self.excluded > 0:
            QtWidgets.QMessageBox.warning(None, 'Curves excluded',
                                          f'The following number of curves were excluded because '
                                          f'the raw min value was larger than the max\n{self.excluded}')

            self.t.df = self.t.df[~self.t.df[output_column].isna()]

        return self.t

    def _func(self, data: np.ndarray, img_info_path: str, roi_state: dict) -> np.ndarray:
        if 'raw_min_max' in roi_state.keys():
            raw_min_max = roi_state['raw_min_max']

        else:
            cnmf_idx = roi_state['cnmf_idx']
            img_info_path = os.path.join(self.proj_path, img_info_path)
            roi_states = pickle.load(open(img_info_path, 'rb'))['roi_states']

            idx_components = roi_states['cnmf_output']['idx_components']

            list_ix = np.argwhere(idx_components == cnmf_idx).ravel().item()

            state = roi_states['states'][list_ix]

            if not state['cnmf_idx'] == cnmf_idx:
                raise ValueError('cnmf_idx from ImgInfoPath dict and DataFrame ROI_State dict do not match.')

            raw_min_max = state['raw_min_max']

        raw_min = raw_min_max['raw_min'][self.option]
        raw_max = raw_min_max['raw_max'][self.option]

        if raw_min >= raw_max:
            self.excluded += 1
            return np.NaN

        return TimeSeriesScalerMinMax(value_range=(raw_min, raw_max)).fit_transform(data).ravel()
