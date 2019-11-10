.. _module_StimulusMapping:

Stimulus Mapping
****************

:ref:`API Reference <module_StimulusMapping>`

**Map temporal information such as stimulus or behavioral periods.**


Console
=======

.. seealso:: :ref:`API Reference <module_StimulusMapping>`

.. code-block:: python
    :linenos:

    import pandas as pd
    from mesmerize.plotting.utils import get_colormap

    # Load dataframe from CSV
    df = pd.read_csv('/share/data/longterm/4/kushal/crcns_datasets/pvc-7/122008_140124_windowmix/stimulus.csv')

    # Sort according to time (stimulus "start" frame column)
    df.sort_values(by='start').reset_index(drop=True, inplace=True)

    # Trim off the periods that are not in the current image sequence
    # This is just because this example doesn't use the whole experiment
    trim = get_image().shape[2]
    df = df[df['start'] <= trim]

    # Remove the unused columns
    df.drop(columns=['sf', 'tf', 'contrast'])

    # Rename the stimulus column of interest to "name"
    df.rename(columns={'ori': 'name'}, inplace=True)

    # Get the names of the stimulus periods to create a colormap for illustration in the curves plot area
    oris = df['name'].unique()
    oris.sort()

    # Create colormap to visualize the stimuli in the viewer's curve plots area
    oris_cmap = get_colormap(oris, 'tab10', output='pyqt', alpha=0.6)

    # Create a column with colors that correspond to the orientations column values
    df['color'] = df['name'].map(oris_cmap)

    # name column must be str type for stimulus mapping module
    # the ori data from the original csv is integers so you must change it
    df['name'] = df['name'].apply(str)

    # Get the stimulus mapping module
    smm = get_module('stimulus_mapping')

    # Set the ori colormap
    smm.maps['ori'].set_data(df)
    
