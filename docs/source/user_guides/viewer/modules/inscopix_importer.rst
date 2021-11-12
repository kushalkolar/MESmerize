.. _module_InscopixImporter:

Inscopix Importer
*****************

The Inscopix Importer module can be used to open ``.isxd`` movies created by Inscopix acquisition software

.. note:: You must have your own license for activating/running the Inscopix Data Processing Software (IDPS) and downloading the IDPS API and ``isx`` library. Mesmerize only provides an implementation of ``isx`` to read ``.isxd`` movies into the application.

In order to use the importer you will need to add the path to the parent dir containing the ``isx`` library to your ``PYTHONPATH`` environment variable.

For example if your ``isx`` dir is located at:

```
/home/user/Inscopix Data Processing 1.6.0/Inscopix Data Processing.linux/Contents/API/Python/isx``
```

Then you will need to add the path to the parent dir, for example:

```
export PYTHONPATH="/home/user/Inscopix Data Processing 1.6.0/Inscopix Data Processing.linux/Contents/API/Python:$PYTHONPATH"
```

**Usage:**

1. Enter the path to the ``.isxd`` or click the ``...`` and choose the file.

2. Click the button to load the file into the :ref:`Viewer Work Environment <ViewerWorkEnv>`.

The sampling rate (framerate) of the video is automatically imported from the ``isxd`` file.

.. note:: Memory usage is quite high when loading files, you will need at least twice as much RAM as the size of the file you're trying to open.
