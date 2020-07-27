Viewer Modules
**************

.. _API_BatchManager:

Batch Manager
=============

.. autoclass:: mesmerize.viewer.modules.batch_manager.ModuleGUI
    :special-members:
    :members:
    :private-members:


.. _API_TiffModule:

Tiff Module
===========

**Uses the tifffile package created by Christoph Gohlke:** https://pypi.org/project/tifffile/

Can be used with scripts within Mesmerize for loading tiff files without using the API of :ref:`API_ViewerCore`

.. autoclass:: mesmerize.viewer.modules.tiff_io.ModuleGUI
    :members:


.. _API_CaimanMotionCorrection:

Caiman Motion Correction
========================

Front-end for `Caiman <https://doi.org/10.7554/eLife.38173>`_ NoRMCorre parameters entry

Can be used with scripts for adding batch items.

.. seealso:: :ref:`User guide <module_CaimanMotionCorrection>`

.. autoclass:: mesmerize.viewer.modules.caiman_motion_correction.ModuleGUI
    :members:
    :member-order: bysource


.. _API_CNMF:

CNMF
====

Front-end for `Caiman <https://doi.org/10.7554/eLife.38173>`_ CNMF parameter entry

Can be used with scripts for adding batch items.

.. seealso:: :ref:`User guide <module_CNMF>`

.. autoclass:: mesmerize.viewer.modules.cnmf.ModuleGUI
    :members:
    :member-order: bysource


.. _API_CNMFE:

CNMFE
=====

Front-end for `Caiman <https://doi.org/10.7554/eLife.38173>`_ CNMFE parameter entry

Can be used with scripts for adding batch items.

.. seealso:: :ref:`User guide <module_CNMFE>`
    
.. autoclass:: mesmerize.viewer.modules.cnmfe.ModuleGUI
    :members:
    :member-order: bysource
    
MESc Importer
=============

MESc importer for exploring & importing image sequences from .mesc HDF5 files.

ModuleGUI
---------

.. autoclass:: mesmerize.viewer.modules.femtonics_mesc.ModuleGUI
    :members:
    :member-order: bysource

MEScNavigator
-------------

Takes care of navigating through the HDF5 data structure of the .mesc file.

.. autoclass:: mesmerize.viewer.modules.femtonics_mesc.MEScNavigator
    :members:
    :member-order: bysource
    
