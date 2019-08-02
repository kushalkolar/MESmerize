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
