.. _plot_Beeswarm:

Beeswarm
********

Used for visualization of data points using a pseudo-scatter and violin plots.

**Layout**

.. image:: ./beeswarm.png

You can click on individual datapoints and view the associated data using the :ref:`Datapoint Tracer <DatapointTracer>`. To show the Datapoint Tracer, in the menubar go to View -> Live datapoint tracer

Parameters
==========

======================  ==================================================================
Parameter               Description
======================  ==================================================================
Data columns            Multi-select data columns to plot

                        | They must have single numerical values, not arrays

Group based on          Categorical data column used for grouping the data

Datapoint tracer curve  Data column, containing numerical arrays, that is shown in the :ref:`Datapoint Tracer <DatapointTracer>`

UUID column             Column containing the UUIDs that correspond to the data in the selected data column(s)

Apply all               Apply the plot parameters and draw the plot
======================  ==================================================================
