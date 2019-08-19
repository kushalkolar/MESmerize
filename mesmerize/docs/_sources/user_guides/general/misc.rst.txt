.. _ConsoleOverview:

Consoles
========

A Python console is embedded in many parts of Mesmerize. You can use it to perform very specific operations more quickly than with a GUI, save an analysis object in between something, format plots, etc.

The console is accessible in many windows through View -> Console. The namespace of the console is usually the same as that of the window that it is embedded in (the instance is usually named as "this"). A list of useful object references and helper functions are listed when you open most consoles.

You can run entire scripts within the console. You can also use import statements to import libraries that you have in your Python environment.

Keyboard controls:

**Execute:** Shift + Enter

**New line:** Enter

**Scroll up through history**: Page Up

**Scroll down through history:** Page Down

The history is stored in ~/.mesmerize


.. _save_ptrn:

Saving plots
============

Some plots allow you to save them in an interactive form, along with the plot data and the plot state as a ".ptrn" file. If you save the file in the "plots" directory of your project it will be listed in the :ref:`WelcomeWindow` when you open your project.

This is currently possible with the following plots: :ref:`plot_Heatmap`, :ref:`plot_KShape` and :ref:`plot_Proportions`.


.. _plot_Navbar:

Plot Navbar
===========

Many plots have a navigation toolbar which you can use to zoom, pan, configure plots, and export plots as images.

Official matplotlib docs about the navigation toolbar: https://matplotlib.org/2.1.2/users/navigation_toolbar.html

**Home:** Reset the plot (not applicable for all plots)

**Pan:** Pan the plot

**Zoom:** Zoom in/out a selection using the left/right mouse button respectively

**Subplot-configuration:** Options to adjust spacing, borders, set tight layout.

**Edit axis, curve...:** For some plots. Options for formating x & y axis limits, labels, select line style, color, etc.

**Save:** Export the figure as an image.  **This is not the same as saving an interactive plot, see "Saving Plots" above**.

