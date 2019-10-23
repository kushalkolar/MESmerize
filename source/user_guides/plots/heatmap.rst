.. _plot_Heatmap:

Heatmap
*******

:ref:`API Reference <API_HeatmapTracerWidget>`

.. note::
	This plot can be saved in an interactive form, see :ref:`Saving plots <save_ptrn>`

Visualize numerical arrays in the form of a heatmap. Also used for visualization of Hierarchical clusterting dendrograms. :ref:`DatapointTracer` is embedded.

**Layout**

.. thumbnail:: ./heatmap_layout.png

**Left:** The heatmap. Clicking the heatmap highlights the selected row and upates the :ref:`DatapointTracer`. Right click on the heatmap to clear the selection highlight on the heatmap. You can zoom and pan the heatmap using the tools above the plot area. You can zoom/pan in the legend and heatmap. The up and down keys on your keyboard can be used to move the current row selection.

**Bottom left:** Set the row order of the heatmap according to a categorical column.

**Middle:** Plot controls.

**Very bottom:** Status label - displays any issues that were raised while setting the plot data. Click on the status label to see more information.

Parameters
==========

**Data column:** Data column, numerical arrays, that contain the data for the heatmap. Each row of this data column (a 1D array) is represented as a row on the heatmap.

**Labels column:** Column containing categorical labels that are used to create the row legend for the heatmap.

**DPT curve column:** Data column, containing numerical arrays, that is shown in the :ref:`DatapointTracer`.

**Data colormap:** Colormap used for representing the data in the heatmap. Default is 'jet'.

**Legend colormap:** Colormap used for the row legend.

**Live update from input transmission:** If checked this plots receives live updates from the :ref:`flowchart <FlowchartOverview>`.

**Plot:** Updates data input from the flowchart.

**Save:** `Save the plot data and state in an interactive form <save_ptrn>`

**Load:** Load a plot that has been saved as a ".ptrn" file.


**Layout to visualize Hierarchical Clustering**

.. thumbnail:: ./heatmap_clustering.png

This plot widget can also be used to visualize a dendrogram on top of a heatmap of data.

The differences are:

#. There are two legend bars

	- Left: Cluster label
	- Right: Corresponds to Labels column parameter.

#. You can also zoom/pan the dendrogram in addition to the legends and heatmap.

#. Sorting the heatmap rows is disabled because this wouldn't make sense

Console
=======

You can directly access the heatmap widget through the console. This is useful for plot customization and exporting with specific parameters.

Toggle the console's visibility by clicking on the "Show/Hide Console" button at the bottom of the controls.

Namespace
---------

==================  ========================================================================================
reference           Description
==================  ========================================================================================
this                The higher-level :ref:`HeatmapTracerWidget <API_HeatmapTracerWidget>` instance, i.e. the entire widget
get_plot_area()     Returns the lower-level :ref:`Heatmap <API_Variant_Heatmap>` variant instance, basically the actual plot area
get_plot()          Returns the seaborn ClusterGrid instance containing the axes
get_fig()           Returns the matplotlib `Figure <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib-figure-figure>`_ instance
==================  ========================================================================================


Example
-------

**Export as an SVG with specific dimensions and DPI**

.. seealso:: matplotlib API for: `Figure.savefig <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.savefig>`_, `Figure.set_size_inches <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.set_size_inches>`_, `Figure.get_size_inches <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.get_size_inches>`_

.. code-block:: python
    :linenos:
    
    # Desired size (width, height)
    size = (2.0, 2.5)
    
    # Get the figure
    fig = get_fig()
    
    # original size to reset the figure after we save it
    orig_size = fig.get_size_inches()
    
    #Set the desired size
    fig.set_size_inches(size)
    
    # Save the figure as an svg file with 600 dpi
    fig.savefig('/share/data/temp/kushal/amazing_heatmap.svg', dpi=600)
    
    # Reset the figure size
    fig.set_size_inches(orig_size)
    
.. note:: The entire plot area might go gray after the figure is reset to the original size. I suspect this is a Qt-matplotlib issue. Simply resize the window a bit and the plot will be visible again!

