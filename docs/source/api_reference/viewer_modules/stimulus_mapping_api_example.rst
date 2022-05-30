This example creates a pandas DataFrame from a csv file to set the stimulus mappings. It uses the csv file from the pvc-7 dataset availble on CRCNS: http://dx.doi.org/10.6080/K0C8276G

You can also download the csv here: :download:`stimulus_pvc7.csv <./stimulus_pvc7.csv>`

This example is meant to be run through the :ref:`Viewer Script Editor <module_ScriptEditor>`

.. code-block:: python

    import pandas as pd
    from mesmerize.plotting.utils import get_colormap

    # Load dataframe from CSV
    df = pd.read_csv('path_to_csv_file')

    # Sort according to time
    df.sort_values(by='start').reset_index(drop=True, inplace=True)

    # Trim off the stimulus periods that are not in the current image sequence
    trim = get_image().shape[2]
    df = df[df['start'] <= trim]

    # get one dataframe for each of the stimulus types
    ori_df = df.drop(columns=['sf', 'tf', 'contrast'])  # contains ori stims
    sf_df = df.drop(columns=['ori', 'tf', 'contrast'])  # contains sf stims
    tf_df = df.drop(columns=['sf', 'ori', 'contrast'])  # contains tf stims

    # Rename the stimulus column of interest to "name"
    ori_df.rename(columns={'ori': 'name'}, inplace=True)
    sf_df.rename(columns={'sf': 'name'}, inplace=True)
    tf_df.rename(columns={'tf': 'name'}, inplace=True)


    # Get the stimulus mapping module
    smm = get_module('stimulus_mapping')

    # set the stimulus map in Mesmerize for each of the 3 stimulus types
    for stim_type, _df in zip(['ori', 'sf', 'tf'], [ori_df, sf_df, tf_df]):
        # data in the name column must be `str` type for stimulus mapping module
        _df['name'] = _df['name'].apply(str)

        # Get the names of the stimulus periods
        stimuli = _df['name'].unique()
        stimuli.sort()

        # Create colormap with the stimulus names
        stimuli_cmap = get_colormap(stimuli, 'tab10', output='pyqt', alpha=0.6)

        # Create a column with colors that correspond to the stimulus names
        # This is for illustrating the stimulus periods in the viewer plot
        _df['color'] = _df['name'].map(stimuli_cmap)

        # Set the data in the Stimulus Mapping module
        smm.maps[stim_type].set_data(_df)
