.. _plot_ScatterPlot:

Scatter
*******

:ref:`API Reference <API_ScatterPlot>`

**Interactive scatter plot**

.. note::
    :ref:`This plot can be saved in an interactive form <save_ptrn>`


Layout
======

.. thumbnail:: ./scatter.png

**Left:** Controls

    =================== ===================================================================
    Control
    =================== ===================================================================
    Data Column         Data column containing numerical arrays of size 2, X & Y values [x, y]
    X                   Data column containing only X values
    Y                   Data column containing only Y values
    log x               Use :math:`log_{10}` of the X data
    log y               Use :math:`log_{10}` of the Y data
    Colors based on     Set spot colors based on categorical labels in this column
    Choose colormap     Colromap for the the spot colors
    Shapes based on     Set spot shapes based on categorical labels in this column
    UUID Column         Column containing UUIDs that correspond to the plot data
    DPT Curve column    Data column containing numerical arrays to show in the :ref:`Datapoint Tracer <DatapointTracer>`
    Spot size           Size of the spots
    Alpha               Not implemented yet
    Live update...      Update the plot with live inputs from the flowchart
    Update Plot         Update the plot according to the input data from the flowchart and the parameters
    Save                :ref:`Save the plot as a ptrn file <save_ptrn>`
    Load                :ref:`Load a saved ptrn file <save_ptrn>`
    Export to ma...     Not implemented yet
    Export data         Not implemented yet
    =================== ===================================================================

**Below the plot:** Status label that display plotting issues. Click the label to see more information.
    
**Right:** :ref:`Datapoint Tracer <DatapointTracer>`. Click datapoints in the plot to set the Datapoint Tracer.

**Bottom:** :ref:`Console <ConsoleOverview>`
