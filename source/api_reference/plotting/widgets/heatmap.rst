.. _API_Heatmap:

Heatmap
*******

Widgets
=======

Higher level widgets that are directly used by the end-user.
Both Heatmap widgets use the same plot variant.

.. _API_HeatmapSplitterWidget:

HeatmapSplitterWidget
---------------------

Heatmap with a vertical splitter that can be used to house another widget. The plot is compatible with both 'row' and 'item' selection modes.

.. autoclass:: mesmerize.plotting.HeatmapSplitterWidget
    :members: __init__, set_data, _set_sort_order, highlight_row, set_transmission, get_transmission
    :member-order: bysource
    
.. _API_HeatmapTracerWidget:

HeatmapTracerWidget
-------------------

Heatmap with an embedded :ref:`Datapoint Tracer <API_DatapointTracer>` that can be saved and restored.

.. autoclass:: mesmerize.plotting.HeatmapTracerWidget
    :show-inheritance:
    :members: plot_variant, set_update_live, set_current_datapoint, set_input, get_plot_opts, set_plot_opts, update_plot, get_cluster_kwrags, set_data, transmission, set_input, save_plot_dialog, save_plot, open_plot_dialog, open_plot
    :member-order: bysource
    
    .. autoattribute:: drop_opts
    
Variant
=======

Lower level widget that handles the actual plotting and user interaction

.. autoclass:: mesmerize.plotting.variants.Heatmap
    :show-inheritance:
    :members: __init__, set, add_stimulus_indicator, data, selector, plot
    :member-order: bysource
    
    .. autoattribute:: sig_selection_changed
