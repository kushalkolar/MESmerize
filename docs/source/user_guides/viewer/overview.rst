.. _ViewerOverview:

Viewer overview
***************

Based on the `pyqtgraph ImageView <http://www.pyqtgraph.org/documentation/widgets/imageview.html>`_ widget.

**The Viewer allows you to do the following things:**

* Examine your calcium movies
* Use modules to perform things like motion correction, CNMF(E), ROI labeling, and stimulus mapping. See their respective guides for details.
* You can also make modifications to an existing Sample in your project by opening it in the Viewer. See Modify Sample and Overwrite guide.

Video Tutorial
==============

This tutorial shows how to create a New Project, open images in the Viewer, use the Stimulus Mapping module and perform Caiman motion correction

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/D9zKhFkcKTk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Layout
======

.. image:: ./overview/1.png

To access Viewer modules choose the module you want to run from the Modules menu at the top. All modules, except the Batch Manager, are small floating windows which you can dock into the Viewer by dragging them to an edge of the viewer.

3D data
-------

When viewing 3D data a slider on the left allows you to move through the z axis.

.. image:: ./overview/viewer_3d.png

The image stack shown above is from Martin Haesemeyer's dataset from the following paper:

    Haesemeyer M, Robson DN, Li JM, Schier AF, Engert F. A Brain-wide Circuit Model of Heat-Evoked Swimming Behavior in Larval Zebrafish. Neuron. 2018;98(4):817-831.e6. doi:10.1016/j.neuron.2018.04.013



.. _ViewerWorkEnv:

Work Environment
================

Everything in the viewer is stored in a Work Environment object. The main data attributes of the viewer work environment are outlined below.

.. seealso:: :ref:`ViewerWorkEnv API <API_ViewerWorkEnv>`

==================  =============================================================
Attribute           Description
==================  =============================================================
imgdata             :ref:`ImgData object <API_ImgData>` containing the Image Sequence and meta data from the imaging source
roi_manager         The back-end :ref:`ROI Manager <API_ROIManagers>` that is currently in use
sample_id           SampleID, if opened from a project Sample
stim_maps           Stimulus maps, if any are defined
history_trace       History log, currently used for logging :ref:`caiman motion correction <module_CaimanMotionCorrection>`, :ref:`CNMF <module_CNMF>` and :ref:`CNMFE <module_CNMFE>` history.
UUID                If opened from a project Sample, it refers to the ImgUUID
==================  =============================================================

You can view everything in the current work environment by going to View -> Work Environment Editor. You cannot edit through this GUI at this time.

Menubar
=======

File
----

Add to Project
^^^^^^^^^^^^^^

Add the current :ref:`work environment <ViewerWorkEnv>` as a Sample to the project.

Open Work Environment
^^^^^^^^^^^^^^^^^^^^^

Deprecated

Save Work Environment
^^^^^^^^^^^^^^^^^^^^^

Deprecated

Clear Work Environment
^^^^^^^^^^^^^^^^^^^^^^

Clear the current :ref:`work environment <ViewerWorkEnv>`. Useful for freeing up RAM.

Edit
----

Deprecated

Image
-----

Reset Scale
^^^^^^^^^^^

Reset the scale of the image ViewBox

Resize
^^^^^^

Resize the image sequence using interpolation.

Crop
^^^^

Crop the image sequence. 

**Usage**

#. When you click this option a square crop region will appear in the top left corner of the image sequence.

#. You can change its shape using the handle in the bottom right corner.

#. To crop to the selection, in the menubar go to Image -> Crop. To cancel cropping right click in the crop region and click "Remove ROI".

Measure
^^^^^^^

Measure the distance (in pixels) between two points in the image sequence.

**Usage**

#. After clicking this option in the menubar, click on a point in the image sequence. You will not see anything yet.

#. Click on a second point in the image sequence, a line will appear connecting the first and second point that you clicked.

#. You can use the handles at the endpoints of the line to change the line.

#. The displacement in the x, y, and along the line will be displayed in the status bar (bottom left corner of the Viewer Window) when you hover over a measuring line.

#. You can create as many measuring lines as you want.

#. To remove a measuring line, right click on a handle and click "Remove ROI"

Change dtype
^^^^^^^^^^^^

Not implemented yet. You can change the dtype through the console.

Projections
^^^^^^^^^^^

View Mean, Max, and Standard Deviation projections of the current image sequence in the work environment. If the data are 3D, the projection is of the current plane.

Modules
-------

Default Viewer Modules. These are explained in more details in the Viewer Modules chapters.

Plugins
-------

Custom viewer modules.

View
----

Work Envionment Editor
^^^^^^^^^^^^^^^^^^^^^^

Explore the data in your work environment using a GUI.

.. image:: ./overview/8.png

.. note:: This is read only, you cannot edit via this GUI.

For example if you want to see your meta data, double click on “imgdata” and then you can see that “imgdata” has two things, the image sequence (i.e. your video) and the meta data.
    
.. image:: ./overview/9.png

If you double click on “meta” above you can see your meta data.

.. image:: ./overview/10.png

You can view your meta data more quickly using the console.

Console
^^^^^^^

View/hide the viewer console

Help
----

Open docs
^^^^^^^^^

Open these docs

.. _ViewerConsole:

Console
=======

Open the console by going to View -> Console.
You can then call ``get_meta()`` to print the meta data dict.

.. image:: ./overview/11.png

You can interact directly with the :ref:`work environment <ViewerWorkEnv>` using the console.

.. seealso:: :ref:`Viewer Core API <API_ViewerCore>`, :ref:`Overview on consoles <ConsoleOverview>`

Namespace
---------

=====================   ====================================================================
Reference               Description
=====================   ====================================================================
vi                      Instance of :ref:`ViewerUtils <API_ViewerUtils>`. Use this to interact with the viewer.
all_modules             List all available modules (includes default and any available plugins/custom modules)
ViewerWorkEnv           Use for creating new instances of :ref:`ViewerWorkEnv <API_ViewerWorkEnv>`
ImgData                 Use for creating new instances of :ref:`ImgData <API_ImgData>`
get_workEnv()           Get the current viewer :ref:`work environment <ViewerWorkEnv>` (instance of :ref:`ViewerWorkEnv <API_ViewerWorkEnv>`)
get_image()             Get the current image sequence (returns current :ref:`ViewerWorkEnv.imgdata.seq <API_ViewerWorkEnv>`). If the data are 3D it returns the current plane only.
get_meta()              Get the current meta data
get_module(<name>)      Pass the name of a module as a string. Returns that module if it is available.
get_batch_manager()     Get the batch manager.
update_workEnv()        Update the viewer GUI with the viewer work environment (vi.viewer.workEnv)
clear_workEnv()         Clear the current work envionment, cleanup the GUI and free the RAM
=====================   ====================================================================

Video Tutorial
--------------

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/a1UO2-OhIHw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Examples
--------

.. include:: ../../api_reference/viewer_core_api_examples.rst
