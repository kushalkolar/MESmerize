.. _DatapointTracer:

Datapoint Tracer
****************

:ref:`API Reference <API_DatapointTracer>`

The Datapoint Tracer is attached to many plots, allowing you to interactively explore the data associated to the datapoints. You can explore the analysis history, the spatial localization of the ROI it originates from, associated numerical or categorical data, and view an additional numerical column (such as the raw trace).

The Datapoint Tracer is embedded in some plots, and in others you can open it by going to View -> Live Datapoint Tracer.

**Datapoint Tracer Layout**

.. thumbnail:: ./datapoint_tracer.png

**Top right**: Max Projection or Standard Deviation Project of the image sequence.

**Bottom right**: Numerical data, based on the *"DPT Curve column"* that the user has specified in the plot controls. If exploring peak feature based data the temporal span of the peak will be highlighted.

**Top left**: Analysis log, a ordered list of operations and their parameters.

**Bottom left**: All other data associated with this datapoint (the data present in the other columns of the row this datapoint is present in, see :ref:`concept_Transmission`)

**Open in viewer button**: Open the parent Sample of the current datapoint in the viewer.
