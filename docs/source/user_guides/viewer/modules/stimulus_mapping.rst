.. _module_StimulusMapping:

Stimulus Mapping
****************

:ref:`API Reference <API_StimulusMapping>`

**Map temporal information such as stimulus or behavioral periods.**

Stimulus Mapping Module

.. image:: ./stim_maps_module.png

Stimulus periods illustrated on the viewer timeline

.. image:: ./stim_maps_viewer.png

The tabs that are available in the stimulus mapping module corresponds to the stimulus types in your :ref:`Project Configuration <StimulusTypeColumns>`.

You can add stimulus periods either manually or through a script.

Manual Annotation
=================

#. To add a stimulus manually click the "Add Row" button. This will add an empty row to the current tab page.

#. Enter a name for the stimulus, start time, end time, and pick a color for illustrating the stimulus periods on the Viewer timeline.

#. To remove a stimulus click the "Remove stim" button. Stimulus periods do not have to be added in chronological order.

#. Click "Set all maps" to set the mappings for all stimulus types. You can then choose to illustrate a stimulus on the viewer timeline by selecting it from "Show on timeline"

Import and Export are not implemented yet.

.. warning:: At the moment, only "frames" are properly supported for the time units.

.. note:: It is generally advisable to keep your stimulus names short with lowercase letters. When sharing your project you can provide a mapping for all your keys. This helps maintain consistency throughout your project and makes the data more readable.

Script
======

.. seealso:: :ref:`API Reference <API_StimulusMapping>`

You can also use the :ref:`Stimulus Mapping module's API <API_StimulusMapping>` to set the stimulus mappings from a pandas DataFrame.

This example creates a pandas DataFrame from a csv file to set the stimulus mappings. It uses the csv file from the pvc-7 dataset availble on CRCNS: http://dx.doi.org/10.6080/K0C8276G

You can also download the csv here: :download:`stimulus_pvc7.csv <./stimulus_pvc7.csv>`

.. code-block:: python
    :linenos:

    import pandas as pd
    from mesmerize.plotting.utils import get_colormap

    # Load dataframe from CSV
    df = pd.read_csv('/share/data/longterm/4/kushal/allen_data_pvc7_chunks/stimulus_pvc7.csv')

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
