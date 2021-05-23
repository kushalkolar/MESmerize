You can save a Transmission files using the :ref:`Save node <node_Save>` and work with the data directly in scripts, jupyter notebooks etc. You can also save them through the flowchart console (and plot consoles) through  :func:`Transmission.to_hdf5 <mesmerize.Transmission.to_hdf5>`.

Workign with Transmission files
-------------------------------

Load a saved Transmission instance using :func:`Transmission.from_hdf5 <mesmerize.Transmission.from_hdf5>`

.. code-block:: python
    :linenos:

    >>> from mesmerize import Transmission
    >>> from uuid import UUID

    # load transmission file
    >>> t = Transmission.from_hdf5('/share/data/temp/kushal/data.trn')
    <mesmerize.analysis.data_types.Transmission at 0x7f4d42f386a0>

    # The DataFrame is always the 'df' attribute
    >>> t.df.head()

                                               CurvePath  ... FCLUSTER_LABELS
    0  curves/a2-_-1-_-843c2d43-75f3-421a-9fef-483d1e...  ...               8
    1  curves/brn3b_a6-_-2-_-21557a64-6868-4ff4-8db1-...  ...               4
    2  curves/brn3b_a6-_-2-_-21557a64-6868-4ff4-8db1-...  ...               5
    3  curves/brn3b_day1_3-_-2-_-ff3e95df-0e15-495c-9...  ...               8
    4  curves/brn3b_day1_3-_-2-_-ff3e95df-0e15-495c-9...  ...               6

    [5 rows x 27 columns]

    # the `df` is just a pandas dataframe
    # View a list of samples in the current file
    >>> t.df.SampleID.unique()

    array(['a2-_-1', 'a5-_-1', 'brn3b_a6-_-2', 'brn3b_day1_3-_-2',
        'brn3b_day1_a1-_-2', 'brn3b_day1_a2-_-2', 'brn3b_day1_a4-_-2',
        'brn3b_day2_a1-_-2', 'brn3b_day2_a1-_-t', 'brn3b_day2_a10-_-2',
        'brn3b_day2_a2-_-1', 'brn3b_day2_a2-_-3', 'brn3b_day2_a8-_-1',
        'cesa_a1-_-1', 'cesa_a1-_-2', 'cesa_a1_jan_2019-_-1',
        'cesa_a1_jan_2019-_-2', 'cesa_a2-_-2', 'cesa_a6-_-1',
        'cesa_a7-_-1', 'cesa_a7-_-2', 'cesa_a8-_-1', 'cesa_a9-_-1',
        'cng_ch4_day1_a2-_-t1', 'cng_ch4_day1_a2-_-t2',
        'cng_ch4_day2_a4-_-t1', 'dmrt1_day1_a2-_-2', 'dmrt1_day1_a4-_-t2',
        'dmrt1_day1_a5-_-', 'dmrt1_day1_a6-_-t', 'dmrt1_day1_a6-_-t2',
        'dmrt1_day2_a1-_-t1', 'dmrt1_day2_a1-_-t2', 'dmrt1_day2_a2-_-t1',
        'dmrt1_day2_a3-_-t1', 'dmrt1_day2_a3-_-t2', 'dmrt1_day2_a4-_-t1',
        'dmrt1_day2_a4-_-t2', 'hnk1_a5-_-2', 'hnk1_a6-_-1', 'hnk1_a7-_-1',
        'hnk1_a7-_-2', 'hnk1_a8-_-1', 'pc2_a10-_-1', 'pc2_a11-_-1',
        'pc2_a13-_-1', 'pc2_a14-_-1', 'pc2_a15-_-1', 'pc2_a16-_-1',
        'pc2_a9-_-1', 'pde9_day1_a2-_-2', 'pde9_day1_a3-_-1',
        'pde9_day1_a4-_-1', 'pde9_day1_a4-_-2', 'pde9_day2_a2-_-t2',
        'pde9_day2_a2-_-t4', 'pde9_day2_a4-_-t1', 'pde9_day2_a4-_-t2',
        'pde9_day2_a4-_-t3', 'pde9_day2_a5-_-t1', 'pde9_day2_a5-_-t2',
        'pde9_day2_a6-_-t1', 'pde9_day2_a7-_-t1', 'pde9_day2_a7-_-t2'],
        dtype=object)

    # Show data associated with a single sample
    >>> t.df[t.df['SampleID'] == 'brn3b_day1_a1-_-2']

                                                CurvePath  ... FCLUSTER_LABELS
    6   curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...  ...               6
    7   curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...  ...               6
    8   curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...  ...               5
    9   curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...  ...               7
    10  curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...  ...               5

    # View the data associated with one ROI
    # the `uuid_curve` is a unique identifier for each curve/ROI
    >> t.df[t.df['SampleID'] == 'brn3b_day1_a1-_-2'].iloc[0]

    CurvePath              curves/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...
    ImgInfoPath            images/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...
    ImgPath                images/brn3b_day1_a1-_-2-_-d3c5f225-7039-4abd-...
    ImgUUID                             d3c5f225-7039-4abd-a7a1-5e9ef2150013
    ROI_State              {'roi_xs': [554, 553, 553, 552, 552, 551, 551,...
    SampleID                                               brn3b_day1_a1-_-2
    anatomical_location                                                 palp
    cell_name                                                           palp
    comments                                                        untagged
    date                                                     20190425_110103
    dorso_ventral_axis                                              untagged
    misc                                                                  {}
    morphology                                                      untagged
    promoter                                                           brn3b
    rostro_caudal_axis                                              untagged
    stimulus_name                                                 [untagged]
    uuid_curve                          f44fbd3d-6eaa-4e19-a677-496908565fde
    _RAW_CURVE             [81.41972198848178, 75.61356993008134, 70.0493...
    meta                   {'origin': 'AwesomeImager', 'version': '4107ff...
    stim_maps                                                       [[None]]
    _BLOCK_                             3e069e2d-d012-47ee-830c-93d85197e2f4
    _SPLICE_ARRAYS         [2.646593459501195, 1.8252819116136887, 1.7422...
    _NORMALIZE             [0.0681729940259753, 0.06533186950232853, 0.06...
    _RFFT                  [443.19357880089615, -66.8777897472859, 55.244...
    _ABSOLUTE_VALUE        [443.19357880089615, 66.8777897472859, 55.2443...
    _LOG_TRANSFORM         [2.646593459501195, 1.8252819116136887, 1.7422...
    FCLUSTER_LABELS                                                        6
    Name: 6, dtype: object

    # Show the ROI object data
    >>> t.df[t.df['SampleID'] == 'brn3b_day1_a1-_-2'].iloc[0]['ROI_State']

    {'roi_xs': array([554, 553, 553, 552, 552, 551, 551, 551, 551, 550, 550, 550, 549,
        548, 547, 547, 546, 546, 545, 545, 544, 543, 543, 542, 541, 541,
        540, 540, 539, 539, 538, 537, 536, 535, 534, 533, 532, 531, 531,
        530, 529, 528, 527, 527, 526, 526, 525, 525, 525, 524, 524, 523,
        522, 522, 521, 521, 520, 521, 521, 521, 521, 521, 522, 522, 522,
        522, 522, 522, 522, 522, 521, 521, 521, 521, 521, 521, 522, 523,
        524, 524, 525, 525, 525, 526, 526, 527, 528, 528, 529, 529, 529,
        530, 530, 531, 532, 532, 533, 534, 535, 535, 536, 536, 537, 538,
        539, 540, 540, 541, 541, 542, 542, 543, 544, 545, 546, 546, 547,
        548, 548, 549, 549, 549, 549, 550, 550, 550, 550, 551, 551, 551,
        552, 552, 552, 553, 553, 553, 554, 554, 554, 553, 554, 554, 554,
        554, 554]),
    'roi_ys': array([155, 156, 156, 157, 157, 158, 159, 160, 160, 161, 162, 162, 162,
            162, 163, 163, 164, 164, 165, 165, 165, 166, 166, 166, 167, 167,
            167, 166, 167, 167, 167, 167, 167, 167, 167, 167, 167, 168, 168,
            168, 168, 168, 168, 167, 167, 166, 166, 165, 164, 164, 163, 163,
            163, 162, 162, 161, 161, 160, 160, 159, 158, 157, 156, 156, 155,
            154, 153, 152, 151, 150, 150, 149, 148, 147, 146, 145, 144, 144,
            144, 144, 143, 143, 142, 141, 141, 140, 140, 140, 139, 139, 138,
            137, 137, 136, 136, 136, 135, 135, 135, 136, 136, 137, 137, 137,
            137, 137, 138, 138, 138, 137, 137, 136, 136, 136, 136, 137, 137,
            137, 138, 138, 139, 140, 141, 141, 142, 143, 144, 144, 145, 146,
            146, 147, 148, 148, 149, 150, 150, 151, 151, 152, 152, 153, 154,
            155, 155]),
    'curve_data': (array([   0,    1,    2, ..., 2996, 2997, 2998]),
    array([ 81.41972199,  75.61356993,  70.04934883, ..., 195.4416283 ,
            184.8844155 , 174.76708104])),
    'tags': {'anatomical_location': 'palp',
    'cell_name': 'palp',
    'morphology': 'untagged'},
    'roi_type': 'CNMFROI',
    'cnmf_idx': 2}


View History Log
----------------

Transmissions have a `history_trace` attribute which is an instance of :class:`HistoryTrace <mesmerize.analysis.data_types.HistoryTrace>`.

Use the :func:`get_data_block_history <mesmerize.analysis.data_types.HistoryTrace.get_data_block_history>` and :func:`get_operations_list <mesmerize.analysis.data_types.HistoryTrace.get_operations_list>` methods to view the history log of a data block.

.. code-block:: python
    :linenos:

    # To view the history log, first get the block UUID of the dataframe row of which you want the history log

    # Block UUIDs are stored in the _BLOCK_ column
    >>> bid = t.df.iloc[10]._BLOCK_
    >>> bid

    '248a6ece-e60e-4a09-845e-188a5199d262'

    # Get the history log of this data block
    # HistoryTrace.get_operations_list() returns a list of operations, without parameters
    # HistoryTrace.get_data_block_history() returns the operations list with the parameters
    >>> t.history_trace.get_operations_list(bid)

    ['spawn_transmission',
     'splice_arrays',
     'normalize',
     'rfft',
     'absolute_value',
     'log_transform',
     'splice_arrays',
     'fcluster']

    # View the entire history log with all params
    >>> t.history_trace.get_data_block_history(bid)

    [{'spawn_transmission': {'sub_dataframe_name': 'neuronal',
    'dataframe_filter_history': {'dataframe_filter_history': ['df[~df["promoter"].isin([\'cesa\', \'hnk1\'])]',
        'df[~df["promoter"].isin([\'cesa\', \'hnk1\'])]',
        'df[~df["cell_name"].isin([\'not_a_neuron\', \'non_neuronal\', \'untagged\', \'ependymal\'])]']}}},
    {'splice_arrays': {'data_column': '_RAW_CURVE',
    'start_ix': 0,
    'end_ix': 2990,
    'units': 'time'}},
    {'normalize': {'data_column': '_SPLICE_ARRAYS', 'units': 'time'}},
    {'rfft': {'data_column': '_NORMALIZE',
    'frequencies': [0.0,
        0.0033444816053511705,
        0.0033444816053511705,
        0.006688963210702341,
        ...

    # Get the parameters for the 'fcluster' operation
    >>> fp = t.history_trace.get_operation_params(bid, 'fcluster')

    # remove the linkage matrix first so we can view the other params
    >>> fp.pop('linkage_matrix');fp

    {'threshold': 8.0,
     'criterion': 'maxclust',
     'depth': 1,
     'linkage_params': {'method': 'complete',
     'metric': 'wasserstein',
     'optimal_ordering': True}}

    # Draw the analysis history as a graph
    # This will open your defeault pdf viewer with the graph
    >>> t.history_trace.draw_graph(bid, view=True)

    # If you are using the API to perform analysis on
    # transmission files, you can use the `HistoryTrace`
    # to log the analysis history
    # For example, add a number `3.14` to all datapoints in a curve
    >>> t.df['_RAW_CURVE'] = t.df['_RAW_CURVE'].apply(lambda x: x + 3.14)

    # Append the analysis log
    >>> t.history_trace.add_operation(data_block_id='all', operation='addition', parameters={'value': 3.14}

