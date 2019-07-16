.. _plot_CrossCorrelation:

Cross Correlation
*****************

Explore `Cross-correlation functions <https://en.wikipedia.org/wiki/Cross-correlation>`_ of all curves from a sample.

This is an interactive widget. You can click on the individual cells in the heatmap to view the individual curves, the cross-correlation function of the two curves, and the spatial localization of the ROI that they originate from.

.. image:: ./cross_cor.gif

Layout
======
 .. image:: ./cross_correlation_layout.png

**Left**: Lag or Maxima Matrix (see below) with thresholds applied and visualized as a heatmap. When you click on the individual cells it will open/update the :ref:`DatapointTracer` according to the two curves the cell corresponds to.

**Top Center**: Parameters.

**Center**: When you click on a cell in the heatmap you will see Curve 1 (x-axis of heatmap), and Curve 2 (y-axis of heatmap) and their cross-correlation function. **The units are in seconds for all of these**

**Right**: List of Samples. Click on a Sample to select it as the current sample.


Lag Matrix
==========

The Lag Matrix is computed by finding the distance between zero and the position of the global maxima in the cross-correlation function.

Maxima Matrix
=============

The Maxima Matrix is computed by 