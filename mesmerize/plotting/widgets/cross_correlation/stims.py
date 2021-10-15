"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import pandas as pd
import numpy as np
from typing import Tuple, List


def get_binary_stims(
        stim_df: pd.DataFrame,
        index_size: int,
        start_offset: int = 0,
        end_offset: int = 0
) -> Tuple[np.ndarray, List[str]]:
    """

    """

    stims = stim_df['name'].unique()

    if index_size < stim_df['end'].max():
        index_size = int(stim_df['end'].max())

    binarized_arrays = []

    for stimulus in stims:
        sub_df = stim_df[stim_df['name'] == stimulus]

        # One binary stim array for each stimulus in the `stim_df`
        stim_array = np.empty(index_size, dtype=np.uint8)
        stim_array[:] = 0

        # fill stim_array
        # stim_array is used for fancy indexing
        for ix, r in sub_df.iterrows():  # iterate through the stimulus periods
            # apply any offsets
            start_ix = r['start'] + start_offset
            end_ix = r['end'] + end_offset

            # set this period to 1 in the array
            stim_array[int(start_ix):int(end_ix)] = 1

        binarized_arrays.append(stim_array)

    return np.vstack(binarized_arrays), stims.tolist()
