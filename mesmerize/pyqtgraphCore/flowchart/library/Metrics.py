from .common import *
import numpy as np
from ....analysis.math import drfft_dtw


class DRFFT_DTW(CtrlNode):
    """Compute distances using Dyanamic Time Warping between: 1)Raw curve and 2) The inverse discrete fourier transform
    derived from feeding incremental steps of frequency domain from discrete fourier transform of the raw curve."""
    nodeName = 'DRFFT_DTW'
    uiTemplate= [('data_column', 'combo',
                  {'toolTip': 'Data column to use as the "raw curve", such as spliced arrays of dF/Fo'}),

                 ('step_size', 'intSpin',
                  {'max': 5000, 'min': 10, 'value': 100, 'step': 50,
                   'toolTip': 'Step size for incrementing rfft inputs for computing irfft. Reducing step size will '
                              'reduce the computation time.'}),

                 ('step_start', 'intSpin',
                  {'max': 5000, 'min': 10, 'value': 100, 'step': 50,
                   'toolTip': 'Frequency domain to start incrementing steps from'}),

                 ('interpolate', 'check', {'toolTip': 'Interpoate the inverse fourier transforms. Increases computation'
                                                      'time SIGNIFICANTLY but may produce more accurate results.'}),

                 ('start', 'button', {'text': 'Compute'})
                 # ('Apply', 'check', {'checked': False, 'applyBox': True})
                 ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})#, 'Out': {'io': 'out', 'bypass': 'In'}})
        self.ctrls['start'].clicked.connect(self._compute)
        self.results = None
        self.widget = drfft_dtw.Widget()

    def process(self, **kwargs):
        transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(transmissions)

        self.t = Transmission.merge(self.transmissions_list).copy()
        columns = self.t.df.columns.to_list()
        self.ctrls['data_column'].setItems(columns)

        self.param_step = self.ctrls['step_size'].value()
        self.param_start = self.ctrls['step_start'].value()
        self.param_interpolate = self.ctrls['interpolate'].isChecked()

        self.data = np.vstack(self.t.df[self.data_column])

    def _compute(self):
        # self.ctrls['start'].setDisabled(True)
        self.widget.show()
        start = self.param_start
        step = self.param_step
        interp = self.param_interpolate
        self.widget.start(start, step, interp, self.data)
