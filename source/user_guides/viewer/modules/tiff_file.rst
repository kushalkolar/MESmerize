Tiff file module
****************

To open a tiff file go to Modules -> Load Images -> Tiff files.

.. note:: You can also use this module through the console and scripts. See :ref:`API_TiffModule`

To open tiff files just click the “Select file” button and choose your file.

.. image:: ./2.png

When you choose a tiff file it will automatically find the associated .json meta data if it has the same filename.

.. image:: ./4.png

Finally, select an appropriate load method (see next section) and click "Load into workEnv"

.. warning:: If the name of the tiff file and .json meta data file are different, you must specify the .json meta data file using the *Select meta data* button.

.. warning:: **You cannot perform any analysis without the meta data file since you need the sampling rate of the video and it is specified in the meta data file.**

Load Method
===========

The options for "Load Method" correspond to the `tifffile <https://pypi.org/project/tifffile/>`_ library method that is used for loading the images.

If you are not sure which method you should use, try all of them and see which one loads your data appropriately. If none of them work, contact us and I may be able to add more methods.

.. note:: If you have an unsaved work environment open (such as a video with ROIs for example) it will prompt you to confirm that you want to clear the work environment before loading the chosen image into the work environment.

asarray
-------

Should work for most tiff files, fast method

asarray - multi series
----------------------

Also fast. Use this if it is a multi-page tiff. For example if the tiff file was created by a program that appends each frame to a file as they are being acquired by the camera.

imread
------

Usually slower, should work for most tiff files.
