.. _plot_SpaceMap:

SpaceMap
********

:ref:`API Reference <API_SpaceMap>`

.. note::
	This plot can be saved in an interactive form, see :ref:`Saving plots <save_ptrn>`

Spatially map a categorical variable onto a projection of a Sample's image sequence

.. thumbnail:: ./spacemap.png

.. note:: Image produced from the following dataset:
    Garner, Aleena (2014): In vivo calcium imaging of layer 4 cells in the mouse using sinusoidal grating stimuli. CRCNS.org.
    http://dx.doi.org/10.6080/K0C8276G


Controls
========

=================   ==============================================================
Parameter           Description
=================   ==============================================================
Patch labels        Categorical column to use for the patch labels
Image Colormap      Colormap for the image
Patches Colormap    Colormap for the patches
Projection          Show the image as a "Max" or "Standard Deviation" projection
Fill Patches        Fill the patches
Line width          Line width of the patches
Alpha               Alpha level of the patches
Samples             Click on the sample to plot
Save                `Save the plot data and state in an interactive form <save_ptrn>`
Load                Load a plot that has been saved as a ".ptrn" file.
=================   ==============================================================


Console
=======

.. seealso:: :ref:`API Reference <API_SpaceMap>`

Namespace
---------

=====================       ========================================================================================
reference                   Description
=====================       ========================================================================================
this                        The :ref:`SpaceMapWidget <API_SpaceMap>` instance, i.e. the entire widget
this.transmission           Current input :ref:`Transmission <concept_Transmission>`
get_plot()                  Returns the plot area
get_plot().fig              Returns the matplotlib `Figure <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib-figure-figure>`_ instance
get_plot().ax               Returns the Axes for the current plot `matplotlib Axes <https://matplotlib.org/2.1.2/api/axes_api.html>`_
=====================       ========================================================================================


Examples
--------

Export
^^^^^^

.. seealso:: matplotlib API for: `Figure.savefig <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.savefig>`_, `Figure.set_size_inches <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.set_size_inches>`_, `Figure.get_size_inches <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.get_size_inches>`_


.. code-block:: python
    :linenos:
    
    # Desired size (width, height)
    size = (6,5)
    
    # Get the figure
    fig = get_plot().fig
    
    # original size to reset the figure after we save it
    orig_size = fig.get_size_inches()
    
    #Set the desired size
    fig.set_size_inches(size)
    
    # Save the figure as a png file with 600 dpi
    fig.savefig('/share/data/temp/kushal/spacemap.png', dpi=600, bbox_inches='tight', pad_inches=0)
    
    # Reset to original size and draw
    fig.set_size_inches(orig_size)
    get_plot().draw()
    
.. note:: The entire plot area might go gray after the figure is reset to the original size. I think this is a Qt-matplotlib issue. Just resize the window a bit and the plot will be visible again!

Legend Title
^^^^^^^^^^^^

.. seealso:: matplotlib API for `matplotlib.axes.Axes.get_legend <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.axes.Axes.get_legend.html>`_

.. code-block:: python

    get_plot().ax.get_legend().set_title('New Title')
    get_plot().draw()

Hide Axis Borders
^^^^^^^^^^^^^^^^^

.. seealso:: matplotlib API for `matplotlib.axes.Axes.axis <https://matplotlib.org/2.1.2/api/_as_gen/matplotlib.axes.Axes.axis.html>`_

.. code-block:: python

    get_plot().ax.axis('off')
    get_plot().draw()
