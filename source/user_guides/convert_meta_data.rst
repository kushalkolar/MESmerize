Convert Meta Data
*****************

In order for you to use your videos with Mesmerize, each of your videos must have meta data organized in the format below.

The simplest way to use your meta data with Mesmerize is to dump all of it into a single json file with the same name as that of the video it is for. You could also add another elif block to :meth:`mesmerize.viewer.core.ViewerWorkEnv._organize_meta` .

For example if you have a movie named "**xyz.tiff**" the json meta data file for that movie would be "**xyz.json**" for the Tiff input module to automatically recognize it.


Minimal Example
---------------

.. code-block:: javascript

	{
		 "source":    "our_recording_program"
		 "fps":       20.0
		 "date":      20190425_114405
	}

Fields and data types
---------------------
**These fields and their types are mandatory**

- **source** *(str)*: Name of recording program used, for your own record
- **fps** *(float)*: Framerate of the video
- **date** *(str)*: Recording date & time separated by an underscore

If you have other data that you would like to keep for the purpose of custom modules or other analysis you can organize them into a single dict under the "orig_meta" key.

**Example with more fields:**

.. code-block:: javascript

	{
		 "source":    "our_recording_program"
		 "version":   0.1.2
		 "fps":       20.0
		 "date":      20190425_114405
		 "orig_meta":	
				{
					"scanner_info":   [1, 2, 3]
					"other_stuff:     "val"
				}
	}
