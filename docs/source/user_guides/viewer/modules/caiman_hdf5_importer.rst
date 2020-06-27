.. _module_CaimanHDF5Importer:

Caiman HDF5 Importer
********************

You can import HDF5 files containing CNMF results that were produced externally by Caiman. The ROIs produced by CNMF, 3D-CNMF or CNMFE will be imported into the current :ref:`work environment <ViewerWorkEnv>` and placed onto the image that is currently open.

.. image:: ./caiman_hdf5_importer.png

You can also use this module through the :ref:`viewer console <ViewerConsole>`, or in the :ref:`Script Editor <module_ScriptEditor>` instead of clicking buttons.

**Example**

.. code-block:: python
    :linenos:
    
    # get the module, hide the GUI
    caiman_importer = get_module('caiman_importer', hide=True)
    
    # import the file
    caiman_importer.import_file('/path/to/file.hdf5')
