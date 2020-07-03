Viewer Work Environment
***********************

The Viewer Work Environment mainly consists of the following pieces of data (attributes).

=========== ======================================================  ====================================================================================================================================
Attribute   Type                                                    Description
=========== ======================================================  ====================================================================================================================================
sample_id   ``str``                                                 The Sample ID assigned by the user, a combination of Animal ID & Trial ID. Does not have a value unless the work environment is opened from an existing project.
UUID        ``uuid.UUID``                                           The unique identifier for this Sample.
imgdata     :ref:`ImgData <concept_ImgData>`                        Image data and image-specific meta data. See subsection for details
roi_manager :ref:`ROI Manager <concept_ROIManager>`                 The back-end ROI manager. Each ROI contains, curve data, spatial data, tags etc. See subsection for details
stim_maps   ``dict`` with dataframes                                A dictionary of dataframes that contain temporal maps to stimulus or behavior events.
custom_cols ``dict``                                                A dictionary of categorial data with keys that correspond to the custom columns in the user's :ref:`project configuration <CustomColumns>`
=========== ======================================================  ====================================================================================================================================

Some of the attributes are "more complex" and are described in the various subsections below.

.. _concept_ImgData:

Image Data
==========

Console accessor: ``get_workEnv().imgdata``
Class: ``mesmerize.viewer.data_types.ImgData``

The ImgData object mainly consists of:

=========   =============   ==============================================================================
Attribute   Type            Description
=========   =============   ==============================================================================
``seq``     numpy.ndarray   The image data, array with dimensions of: 2D + time, or 3D + time
``meta``    dict            Meta data that corresponds to the recording ONLY. Not ROIs, stimulus data etc.
=========   =============   ==============================================================================

In addition to the above attributes, max & standard deviation projections are also stored in the ``image`` directory of a project when the Sample is added to a project. For 3D data the projections are stored per imaging plane.

.. seealso:: :ref:`API docs <API_ImgData>`

.. _concept_ROIManager:

ROI Manager
===========

Console accessor: ``get_workEnv().roi_manager``
Class: One of the classes in ``mesmerize.viewer.modules.roi_manager.managers``

The ROI Manager mainly contains a list of ROIs. Each ROI In this list has the following pieces of data:

==============      =============   ==============================================================================
Attribute           Type            Description
==============      =============   ==============================================================================
``curve_data``      numpy.ndarray   The curve data for the ROI, [x_values, y_values]
spatial data        N/A             Depends on ROI Type. ``roi_xs`` and ``roi_ys``
``_tags``           dict            Categorical tags, usually ``str`` labels
``metadata``        dict            Any additional metadata
==============      =============   ==============================================================================
