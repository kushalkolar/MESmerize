.. _API_ScatterPlot:

Scatter Plot
************

.. _API_ScatterPlotWidget:

ScatterPlotWidget
=================

Higher level widget that is directly used by the end-user.
Scatter plot with docked Control Widget, :ref:`Datapoint Tracer <API_DatapointTracer>`, and Console.

.. autoclass:: mesmerize.plotting.ScatterPlotWidget
    :show-inheritance:
    :members: set_update_live, set_current_datapoint, set_input, get_plot_opts, set_plot_opts, update_plot, transmission, save_plot_dialog, save_plot, open_plot_dialog, open_plot, live_datapoint_tracer
    :member-order: bysource
    
.. _API_Variant_PgScatterPlot:

Variant
=======

Lower level widget that interfaces with pqytgraph.ScatterPlotItem and has some helper methods.

.. autoclass:: mesmerize.plotting.variants.PgScatterPlot
    :show-inheritance:
    :members: __init__, add_data, _clicked, set_legend, clear_legend, clear
    :member-order: bysource
    
    .. autoattribute:: signal_spot_clicked
    
