.. NusetSegmentation::

Nuset Segmentation
******************


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
equalize_kernel     kernel size, increase if the pre-processed image is grainy. Use a value ~1/16-1/8 the size of the image
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

.. warning:: high **rescale_ratio** values will increase the time required for segmentation. Values around 3.0 take about 1 minute for 512x512 sized images on a 16 core AMD Ryzen CPU.

.. note:: min_score & nms_threshold work in opposing ways


Post-process
------------

Export
======

