from .common import *
import numpy as np
from sklearn.metrics import calinski_harabaz_score
from sklearn.cluster import KMeans


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

                 ('Apply', 'check', {'checked': False, 'applyBox': True})
                 ]

    def processData(self, transmission: Transmission):
        self.t = transmission
        self.set_data_column_combo_box()

        if self.ctrls['Apply'].isChecked() is False:
            return

        self.t = transmission.copy()

        step_size = self.ctrls['step_size'].value()
        step_start = self.ctrls['step_start'].value()
        interpolate = self.ctrls['interpolate'].isChecked()

        self.data = np.vstack(self.t.df[self.data_column])

