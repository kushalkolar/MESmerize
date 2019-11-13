.. _module_CNMF:

CNMF
****

Perform CNMFE using the implementation provided by the CaImAn library. This modules basically provides a GUI for parameter entry.

**I highly recommend going through the following before using this module**
        
    - CNMFE builds upon CNMF
        `Pnevmatikakis, E. A., Gao, Y., Soudry, D., Pfau, D., Lacefield, C., Poskanzer, K., … Paninski, L. (2014). A structured matrix factorization framework for large scale calcium imaging data analysis, 1–16. <https://arxiv.org/abs/1409.2903>`_
        
        
        `Pnevmatikakis, E. A., Soudry, D., Gao, Y., Machado, T. A., Merel, J., Pfau, D., … Paninski, L. (2016). Simultaneous Denoising, Deconvolution, and Demixing of Calcium Imaging Data. Neuron, 89(2), 285. <https://doi.org/10.1016/j.neuron.2015.11.037>`_
    
    - CaImAn demo notebook, the implementation in Mesmerize is basically from the demo. The second half of the notebook describes CNMF
        https://github.com/flatironinstitute/CaImAn/blob/master/demos/notebooks/demo_pipeline.ipynb

.. image:: ./cnmfe.png

**Parameters**

Please see the CaImAn demo notebook mentioned above to understand the parameters.


Console
=======

A script can be used to add CNMFE batch items. This is much faster than using the GUI. This example sets the work environment from the output of a batch item. See the :ref:`Caiman Motion Correction script usage examples <MotCorScripts>` for how to load images if you want to add CNMF items from images that are not in a batch.

.. seealso:: :ref:`Script Editor <module_ScriptEditor>`, :ref:`CNMF module API


.. code-block:: python
    :linenos:
    
    # CNMF Params that we will use for each item
    params =   {'Input': 'Current Work Environment',
                'p': 2, 
                'gnb': 1, 
                'merge_thresh': 0.25, 
                'rf': 70, 
                'stride_cnmf': 40, 
                'k': 16, 
                'gSig': 8, 
                'min_SNR': 2.5, 
                'rval_thr': 0.8, 
                'cnn_thr': 0.8, 
                'decay_time': 20, 
                'name_cnmf': 'set_later_per_file', 
                'refit': True
                }

    # Get the batch manager
    bm = get_batch_manager()
    cnmf_mod = get_module('cnmf')
    
    # Start index if we want to start processing the new items after they have been added
    start_ix = bm.df.index.size + 1

    for ix, r in bm.df.iterrows():
        # Use output of items 6 - 12
        if ix < 6:
            continue
        if ix > 12:
            break
            
        # Get the name of the mot cor item	
        name = r['name']

        # Set the name for the new cnmf item
        params['name_cnmf'] = name
        
        # Load the mot cor output
        bm.load_item_output(module='caiman_motion_correction', viewers=viewer, UUID=r['uuid'])
        
        # Set the CNMF params and add to batch
        cnmf_mod.set_params(params)
        cnmf_mod.add_to_batch_cnmf()
    
    # Cleanup the work environment
    vi._clear_workEnv()
    
    # Uncomment the last two lines to start the batch as well
    #bm.process_batch(start_ix, clear_viewers=True)
    
