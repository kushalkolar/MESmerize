.. _module_CNMF:

CNMF
****

Console
=======

.. code-block:: python
    :linenos:
    
    # CNMF Params that we will use for each item
    params = {'Input': 'Current Work Environment',
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
    
