.. NusetSegmentation::

Nuset Segmentation
******************

Deep learning based segmentation, useful for nuclear localized indicators. ROIs segmented through this module can be imported into the Viewer Work Environment.

.. note:: If you use this tool, please cite the Nuset paper in addition to citing Mesmerize: Yang L, Ghosh RP, Franklin JM, Chen S, You C, Narayan RR, et al. (2020) NuSeT: A deep learning tool for reliably separating and analyzing crowded cells. PLoS Comput Biol 16(9): e1008193. https://doi.org/10.1371

Parameters
==========

Projection
----------

Choose a projection which maximizes the visibility of your regions of interest

Pre-process
-----------

=================   =================
Parameter           Description
=================   =================
do_preprocess       perform pre-processing
do_sigmoid          perform `sigmoid correction <https://scikit-image.org/docs/0.15.x/api/skimage.exposure.html#skimage.exposure.adjust_sigmoid>`_
sigmoid_cutoff      cutoff, lower values will increase the exposure
sigmoid_gain        gain, high values can be thought of as increasing contrast
sigmoid_invert      invert the image if necessary. Regions of interesting should be bright, background should be dark
do_equalize         perform `adaptive histogram equalization <https://scikit-image.org/docs/0.15.x/api/skimage.exposure.html#skimage.exposure.equalize_adapthist>`_
equalize_lower      Set a lower limit, this helps remove background & increase contrast
equalize_upper      Upper limit for the histogram
equalize_kernel     kernel size, increase if the pre-processed image is grainy. Start with a value ~1/16-1/8 the size of the image
=================   =================

NuSeT
-----

===============     ============================================
Parameter           Description
===============     ============================================
watershed           `wastershed the image <https://en.wikipedia.org/wiki/Watershed_(image_processing)>`_, useful if your cells are tightly packed. Uncheck if cells are large and/or sparse.
min_score           Decreasing this value will cause more regions to be found, i.e. cells tend to split more
nms_threshold       Increasing this value will cause more regions to be found, i.e. cells tend to split more
rescale_ratio       Use smaller values less than 1.0 if you have large bright cells, If you have smaller or dim cells use values higher than 1.0
===============     ============================================

.. note:: min_score & nms_threshold work in opposing ways

.. note:: Segmentation will utilize all threads available on your system (regardless of the value set in your System Configuration). However it only takes a few seconds or a few minutes if segmenting a large 3D stack.

.. note:: high **rescale_ratio** values will increase the time required for segmentation. Values around 3.0 take about ~1 minute for 512x512 sized images on ~16 core CPUs.

Post-process
------------

Export
======

If you export using a Convex Hull masks containing only a few pixels, which may be noise, will be removed.

.. note:: Segmentation will utilize all threads available on your system (regardless of the value set in your System Configuration). However it only takes a few seconds if exporting a 2D image, and make take ~10 minutes if exporting a large 3D stack.
