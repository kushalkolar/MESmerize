.. _module_Suite2pImporter:

Suite2p Importer
****************

You can load Suite2p output files to import ROIs into the current :ref:`work environment <ViewerWorkEnv>`. This places the Suite2p-derived ROIs onto the image that is currently open.

.. image:: ./suite2p_importer.png

You can also use this module through the :ref:`viewer console <ViewerConsole>`, or in the :ref:`Script Editor <module_ScriptEditor>` instead of clicking buttons.

**Example**

.. code-block:: python
    :linenos:
    
    # get the module, hide the GUI
    s2p_importer = get_module('suite2p_importer', hide=True)
    
    # set the path to the dir containing the suite2p output files
    s2p_importer.data.set_dir('/path/to/dir')
    
    # set the amount of neuropil contamination to subtract
    s2p_importer.data.Fneu_sub = 0.7
    
    # import the suite2p data into the current work environment
    s2p_importer.import_rois()
    
    # clear the data from the importer before importing another directory 
    # this doesn't do anything to the viewer work environment, just clears the importer data
    s2p_importer.data.clear()
    
