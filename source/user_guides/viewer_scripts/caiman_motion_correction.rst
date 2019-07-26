CaImAn motion correction batch items can be added through the use of a script, this is much faster than using a GUI.

This example shows how to add all tiff files (of image sequences) from a directory as motion correction batch items with 3 different variants of parameters.

.. code-block:: python

	# Import glob so we can get all tiff files in a dir
	from glob import glob
	# Import os to get filenames from paths
	import os

	# Just get a shortcut reference to the auto_crop function
	auto_crop = image_utils.auto_crop

	# Parameters for cropping, these should work for everything
	# These worked well for various different constructs
	# If you get non-specific cropping (too much black) try "method" as "spectral_saliency" (See below)
	crop_params = {"projection":	"max+std",
		    "method": 	"threshold",
		    "denoise_params": (32, 32),
		    }

	# Spectral saliency is another method
	# You can try and play around with the parameters
	# If the cropping is insufficient, you can set "projection" to just "max" or "std"
	# If you get too much junk blackness around the animal try increasing denoise_params
	# or reduce padding. Default padding is 30 (when nothing is specified like above) 
	crop_params_salient=	{"projection": 	"max+std",
			 "method": 	"spectral_saliency",
			 "denoise_params":	(16, 16),
			 "padding":	40
			 }

	# Motion correction params.
	# Param names are same as in the GUI
	mc_params = 	{"max_shifts_x": 		10,
			"max_shifts_y": 		10,
			"iters_rigid": 		2,
			"name_rigid":		"Does not matter",
			"max_dev": 		3,
			"strides": 		196,
			"overlaps": 		98,
			"upsample": 		4,
			"name_elas": 		"will set later per file",
			"output_bit_depth":		"Do not convert"
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

	# If you want to also process the batch after adding the items uncomment the following lines
	#bm = get_batch_manager()
	#bm.process_batch(clear_viewers=True)