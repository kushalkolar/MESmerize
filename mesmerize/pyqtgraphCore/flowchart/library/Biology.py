# -*- coding: utf-8 -*-
# from . import functions
from .common import *
from ....analysis.data_types import *
from ....analysis.stimulus_extraction import StimulusExtraction
from ....plotting import TuningCurvesWidget


class ExtractStim(CtrlNode):
    """Extract portions of curves according to stimulus maps"""
    nodeName = 'ExtractStim'
    uiTemplate = [('data_column', 'combo', {}),
                  ('Stim_Type', 'combo', {}),
                  ('start_offset', 'intSpin', {'min': -999999, 'max': 999999, 'value': 0, 'step': 1}),
                  ('end_offset', 'intSpin', {'min': -999999, 'max': 999999, 'value': 0, 'step': 1}),
                  ('zero_pos', 'combo', {'values': ['start_offset', 'stim_end', 'stim_center']}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()
        self.ctrls['Stim_Type'].setItems(self.t.STIM_DEFS)

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        data_column = self.ctrls['data_column'].currentText()

        stim_def = self.ctrls['Stim_Type'].currentText()
        start_offset = self.ctrls['start_offset'].value()
        end_offset = self.ctrls['end_offset'].value()
        zero_pos = self.ctrls['zero_pos'].currentText()

        self.stim_extractor = StimulusExtraction(self.t, data_column, stim_def, start_offset, end_offset, zero_pos)

        self.t = self.stim_extractor.extract()

        params = {'stim_type': stim_def,
                  'start_offset': start_offset,
                  'end_offset': end_offset,
                  'zero_pos': zero_pos
                  }

        self.t.history_trace.add_operation('all', operation='extract_stim', parameters=params)
        self.t.last_output = '_ST_CURVE'

        return self.t


class StimTuning(CtrlNode):
    """Get stimulus tuning curves"""
    nodeName = "StimTuning"
    uiTemplate = [('ShowGUI', 'button', {'text': 'Show GUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}, 'Out': {'io': 'out'}})
        self.widget = TuningCurvesWidget()
        self.widget.sig_output_changed.connect(self._send_output)
        self.ctrls['ShowGUI'].clicked.connect(self.widget.show)
        self.output_transmission = None

    def _send_output(self, t: Transmission):
        self.output_transmission = t
        self.changed()

    def process(self, output_transmission=False, **kwargs):
        if self.output_transmission:
            out = self.output_transmission
        else:
            out = self.processData(**kwargs)

        return {'Out': out}

    def processData(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)
        self.t = Transmission.merge(self.transmissions_list)
        self.widget.set_input(self.t)
        return None


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
