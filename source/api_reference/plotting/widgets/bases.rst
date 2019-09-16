.. API_PlotBases::

Plot Bases
**********

AbstractBasePlotWidget
======================

.. autoclass:: mesmerize.plotting.widgets.base._AbstractBasePlotWidget
    :members: transmission, set_input, update_plot, get_plot_opts, set_plot_opts, save_plot, open_plot
    :member-order: bysource
    
BasePlotWidget
==============

Inherit from this to create interactive plots that can be saved and restored.

.. autoclass:: mesmerize.plotting.widgets.base.BasePlotWidget
    :show-inheritance:
    :members: __init__, block_signals_list, transmission, set_input, fill_control_widget, update_plot, get_plot_opts, set_plot_opts, signal_blocker, save_plot_dialog, save_plot, open_plot_dialog, open_plot
    :member-order: bysource
