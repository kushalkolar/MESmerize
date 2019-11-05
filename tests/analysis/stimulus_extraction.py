from mesmerize import Transmission
from mesmerize.analysis.stimulus_extraction import StimulusExtraction
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

t = Transmission.from_hdf5(os.path.join(curr_dir, '../data/trns/heatmap_allen_pvc7.ptrn'))

se = StimulusExtraction(t, '_ZSCORE', 'ori', 0, 0, 'start_offset')

df = se.extract()
