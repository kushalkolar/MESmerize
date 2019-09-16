.. _module_CaimanMotionCorrection:

Caiman Motion Correction
************************

Perform motion correction using the NoRMCorre implementation in the CaImAn library.

**I highly recommend going through the following before using this module**

    - NoRMCorre paper
        `Pnevmatikakis, E. A., & Giovannucci, A. (2017). NoRMCorre: An online algorithm for piecewise rigid motion correction of calcium imaging data. Journal of Neuroscience Methods, 291, 83–94. <https://doi.org/10.1016/j.jneumeth.2017.07.031>`_

    - The CaImAn demo notebook, the implementation in Mesmerize is basically from the demo
        https://github.com/flatironinstitute/CaImAn/blob/master/demos/notebooks/demo_motion_correction.ipynb

.. image:: ./caiman_motion_correction.png

**Parameters**

Output bit depth: The motion corrected image sequences are of float32 type. You can optionally convert the output to 8 or 16 bit uint types to save disk space. **This doesn't always work from my experience, values might get clipped**.

For all other parameters please see the demo notebook mentioned above.

Usage
=====

This module adds a "caiman motion correction" *item* to the batch. Set the desired parameters (see demo notebook) and then enter a name to add it as an *item* to the batch. After the batch item is processed, double-click the batch item to open the motion corrected image sequence in the viewer. You can then use this motion corrected image sequence for further analysis, such as :ref:`CNMF <module_CNMF>` or :ref:`CNMFE <module_CNMFE>`.

.. seealso:: This modules uses the :ref:`Batch Manager <module_BatchManager>`.

.. note:: The parameters used for motion correction are stored in the work environment of the viewer and this log is carried over and saved in the :ref:`Project Sample <ProjectSample>` as well. To see the parameters that were used for motion correction in the viewer, execute ``get_workEnv().history_trace`` in the viewer console and look for the ``caiman_motion_correction`` entry.

Script Usage
============

A script can be used to add caiman motion correction batch items. This is much faster than using the GUI.

.. seealso:: :ref:`Script Editor <module_ScriptEditor>`

Add items
---------

This example shows how to add all tiff files (of image sequences) from a directory as batch items with 3 different variants of parameters.

.. seealso:: This example uses the :ref:`ViewerWorkEnv API <API_ViewerWorkEnv>` and :ref:`Batch Manager API <API_BatchManager>`

.. code-block:: python
    :linenos:
    
    # Import glob so we can get all tiff files in a dir
    from glob import glob
    # Import os to get filenames from paths
    import os

    # Motion correction params.
    # Params are identical to the GUI ones
    
    mc_params = {
                "max_shifts_x":         6,
                "max_shifts_y":         6,
                "iters_rigid":          2,
                "name_rigid":           "Does not matter",
                "max_dev":              3,
                "strides":              196,
                "overlaps":             98,
                "upsample":             4,
                "name_elas":            "will set later per file",
                "output_bit_depth":     "Do not convert"
                }

    # Path to the dir containing images
    files = glob("/full_path_to_raw_images/*.tiff")
    # Sort in alphabetical order (should also work for numbers)
    files.sort()

    # Open each file, crop, and add to batch with 3 diff mot cor params
    for i, path in enumerate(files):
        print("Working on file " + str(i + 1) + " / " + str(len(files)))
        
        # get json file path for the meta data
        meta_path = path[:-5] + ".json"
        
        # Create a new work environment with this image sequence
        work_env = ViewerWorkEnv.from_tiff(path, "asarray-multi", meta_path)
        
        # Get caiman motion correction module, hide=False to not show GUI
        mc_module = get_module("caiman_motion_correction", hide=True)
        
        # Set name for this video file
        name = os.path.basename(path)[:-5]
        mc_params["name_elas"] = name	
        
        # Set the input work environment
        mc_module.set_input_workEnv(work_env)
        
        # First variant of params
        mc_params["strides"] = 196
        mc_params["overlaps"] = 98
        # Add one variant of params for this video to the batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()
        
        # Try another variant of params	
        mc_params["strides"] = 256
        mc_params["overlaps"] = 128
        # Set these params and add to batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()
        
        # Try one more variant of params	
        mc_params["strides"] = 296
        mc_params["overlaps"] = 148
        # Set these params and add to batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()
        
    # If you want to process the batch after adding the items uncomment the following lines
    #bm = get_batch_manager()
    #bm.process_batch(clear_viewers=True)
    

Crop and add items
------------------

This example shows how to crop videos prior to adding them as batch items. This is useful if you want to crop-out large unchanging regions of your movides. It uses either simple thresholding or spectral salieny on a standard deviation projection to determine the bounding box for cropping.

.. code-block:: python
    :linenos:

    # Import glob so we can get all tiff files in a dir
    from glob import glob
    # Import os to get filenames from paths
    import os
    
    # Just get a shortcut reference to the auto_crop function
    auto_crop = image_utils.auto_crop
    
    # Parameters for cropping, these should work for everything
    # These worked well for various different constructs
    # If you get non-specific cropping (too much black) try "method" as "spectral_saliency" (See below)
    crop_params = {
                    "projection":       "max+std",
                    "method":           "threshold",
                    "denoise_params":   (32, 32),
                    }
                
    # Spectral saliency is another method
    # You can try and play around with the parameters
    # If the cropping is insufficient, you can set "projection" to just "max" or "std"
    # If you get too much junk blackness around the animal try increasing denoise_params
    # or reduce padding. Default padding is 30 (when nothing is specified like above) 
    crop_params_salient = {
                            "projection":    "max+std",
                            "method": 	"spectral_saliency",
                            "denoise_params":	(16, 16),
                            "padding":	40
                            }

    # Motion correction params.
    # Params are identical to the GUI ones
        mc_params = {
                "max_shifts_x":         6,
                "max_shifts_y":         6,
                "iters_rigid":          2,
                "name_rigid":           "Does not matter",
                "max_dev":              3,
                "strides":              196,
                "overlaps":             98,
                "upsample":             4,
                "name_elas":            "will set later per file",
                "output_bit_depth":     "Do not convert"
                }

    # Path to the dir containing images
    files = glob("/full_path_to_raw_images/*.tiff")
    # Sort in alphabetical order (should also work for numbers)
    files.sort()
    
    # Open each file, crop, and add to batch with 3 diff mot cor params
    for i, path in enumerate(files):
        print("Working on file " + str(i + 1) + " / " + str(len(files)))

        # get json file path for the meta data
        meta_path = path[:-5] + ".json"
        
        # Create a new work environment with this image sequence
        work_env = ViewerWorkEnv.from_tiff(path, "asarray-multi", meta_path)
        
        print("Cropping file: " + str(i + 1))
        
        raw_seq = work_env.imgdata.seq	
        # Auto crop the image sequence
        cropped = auto_crop.crop(raw_seq, crop_params)	
        # Set work env img seq to the cropped one and update
        work_env.imgdata.seq = cropped
        
        # Get caiman motion correction module, hide=False to not show GUI
        mc_module = get_module("caiman_motion_correction", hide=True)
        
        # Set name for this video file
        name = os.path.basename(path)[:-5]
        mc_params["name_elas"] = name	
        
        # Set the input work environment
        mc_module.set_input_workEnv(work_env)
        
        # First variant of params
        mc_params["strides"] = 196
        mc_params["overlaps"] = 98
        # Add one variant of params for this video to the batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()
        
        # Try another variant of params	
        mc_params["strides"] = 256
        mc_params["overlaps"] = 128
        # Set these params and add to batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()
        
        # Try one more variant of params	
        mc_params["strides"] = 296
        mc_params["overlaps"] = 148
        # Set these params and add to batch
        mc_module.set_params(mc_params)
        mc_module.add_to_batch()

    # If you want to process the batch after adding the items uncomment the following lines
    #bm = get_batch_manager()
    #bm.process_batch(clear_viewers=True)
