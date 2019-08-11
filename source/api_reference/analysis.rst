Analysis
********

Analysis back-ends

Cross correlation
=================

functions
---------

**Helper functions. Uses tslearn.cycc**

.. automodule:: mesmerize.analysis.math.cross_correlation
    :members:
    :member-order: bysource

CC_Data
--------------

**Data container**

.. warning:: All arguments MUST be numpy.ndarray type for CC_Data for the save to be saveable as an hdf5 file. Set ``numpy.unicode`` as the **dtype** for the ``curve_uuids`` and ``labels`` arrays. If the **dtype** is ``'O'`` (object) the **to_hdf5()** method will fail.

.. autoclass:: mesmerize.analysis.math.cross_correlation.CC_Data
    :members: __init__, ccs, lag_matrix, epsilson_matrix, curve_uuids, labels, get_threshold_matrix, from_dict, to_hdf5, from_hdf5
    :member-order: bysource
