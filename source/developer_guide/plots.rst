.. _developer_plots:

Plots
*****

The easiest way to create a plot module is by subclassing the :ref:`BasePlotWidget <API_BasePlotWidget>`. You could also subclass the abstract base if you need to define all the common functionality differently.

General Design
==============

This shows how you can design a plot using the :ref:`SpaceMapPlot <API_SpaceMapPlot>` as a simple example. It will generally consist of a class for the main plot area, plot control, and the plot window which contains the controls and plot area.

Plot Area
=========

A class which holds the actual plot, could be a matplotlib widget or pyqtgraph plot widget for example. In the :ref:`SpaceMapPlot <API_SpaceMapPlot>` this is simply a subclass of the pyqtgraph matplotlib widget with a few more attributes and a helper method. The `error_label` attribute is simply a QLabel used for displaying a plot error summary and is handled by the `exceptions_label` decorator from :ref:`qdialogs <common-qdialogs>`.

Plot Controls
=============

A class which manages the plot controls. Generally useful to use a QDockWidget for this and design the actual GUI layout using QtDesigner. The :ref:`WidgetRegistry <API_WidgetRegistry>` provides a simple way to package the plot control values (plot parameters) into a dict.

Register a widget to the registry using the :ref:`WidgetRegistry <API_WidgetRegistry>` instance's `register()` method. The **getter** method corresponds to the widget's method which will return the value of the widget (such as text or a number) that is set in the parameters dict which is created when `widget_registry.get_state()` is called. Correspondingly, **setter** method is the widget's method that is used to set a value to the widget and is used when saved plots are restored. In essense, **setter** and **getter** must be interoperable.

The Space Map plot uses a `sig_changed` class attribute that simply emits when any of the widgets are changed. This is later used in the main plot window to update the plot.

A `fill_widget()` method is useful for populating the controls in the dock widget when the input data to the plot window changes.

In the Space Map widget, `get_state()` and `set_state()` simply wrap the corresponding methods from the :ref:`WidgetRegistry <API_WidgetRegistry>` instance.

Plot Window
===========

Subclass from QMainWindow and :ref:`BasePlotWidget <API_BasePlotWidget>`. **Mandatory** to specify a `drop_opts` class attribute of type *list*. This list contains the name of any widgets in the dict return from the :ref:`WidgetRegistry <API_WidgetRegistry>` that should be exluded when saving the plot. This should be used if you are using data types that are not JSON serializable, however it is rarely necessary. Support for `drop_opts` may be removed in the future.

In general specifying the methods described below should be sufficient to create a saveable plot. If you need finer control of the data struture for saving/opening plots you can subclass from the :ref:`abstract base class <API_PlotBases>`.

__init__
--------

Setting things up, connection signals, etc. Useful to have a console dock widget.

set_update_live()
-----------------

A method that interacts with a "live update" checkbox in the plot controls.

set_input()
-----------

Set the input transmission for this plot if it is in "live update" mode or if the plot instance is new (has not had input data previously).

Useful to have a `BasePlotWidget.signal_blocker` decorator so that the plot doesn't constantly update while the new data comes in, since it could cause plot options to change etc.

fill_control_widget()
---------------------

Organize the plot options that are available to the user and set the control widgets.


Useful to have a `BasePlotWidget.signal_blocker` decorator here as well for same reasons as described above.

update_plot()
-------------

This is the core of plot. Use the input transmission and the user-selected plot parameters to draw the plot in the plot area. Generally interacts with the Plot Area instance. You can use the `get_state()` method of the control widget's :ref:`WidgetRegistry <API_WidgetRegistry>` to  conveniently get a dict of all the user-selected plot parameters.

Useful to have an `exceptions_label` or `present_exceptions` decorator from the :ref:`qdialogs module <common-qdialogs>`. The `exceptions_label` provides a less annoying way to present exceptions that occured when updating the plot. 


get_plot_opts()
---------------

Usually just returns the dict from the widget registry containing all user-set plot parameters.

set_plot_opts()
---------------

Usually just calls the widget registry's set_state() method to set the plot parameters from a dict.

Useful to have a `BasePlotWidget.signal_blocker` decorator. In general you would use the :ref:`BasePlotWidget <API_BasePlotWidget>`.open_plot() method to open a saved plot and it takes care of updating the plot after the input transmission and plot parameters are set.

show_exception_info()
---------------------

Called when the `exceptions_label` is clicked. Opens a QMessageBox to show the entire stack trace.
