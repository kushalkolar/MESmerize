.. _ViewerOverview:

Viewer overview
***************

Based on the `pyqtgraph ImageView <http://www.pyqtgraph.org/documentation/widgets/imageview.html>`_ widget.

**The Viewer allows you to do the following things:**

* Examine your calcium movies
* Use modules to perform things like motion correction, CNMF(E), ROI labeling, and stimulus mapping. See their respective guides for details.
* You can also make modifications to an existing Sample in your project by opening it in the Viewer. See Modify Sample and Overwrite guide.

Layout
======

.. thumbnail:: ./overview/1.png

To access Viewer modules choose the module you want to run from the Modules menu at the top. All modules, except the Batch Manager, are small floating windows which you can dock into the Viewer by dragging them to an edge of the viewer.

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

#. Click on a second point in the image sequence, a line will appear connecting the first and second points that you clicked.

#. You can use the handles at the endpoints of the line to change the line.

#. To measure the distance of the line go to Image -> Measure. A window will pop up displaying the change in x, y, and length of the line in pixels.

Change dtype
^^^^^^^^^^^^

Not implemented yet. You can change the dtype through the console.

Projections
^^^^^^^^^^^

View Mean, Max, and Standard Deviation projections of the current image sequence in the work environment.

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

.. thumbnail:: ./overview/8.png

.. note:: This is read only, you cannot edit via this GUI.

For example if you want to see your meta data, double click on “imgdata” and then you can see that “imgdata” has two things, the image sequence (i.e. your video) and the meta data.
    
.. image:: ./overview/9.png

If you double click on “meta” above you can see your meta data.

.. image:: ./overview/10.png

You can view your meta data more quickly using the console.

Open the console by going to View -> Console.
You can then call ``get_meta()`` to print the meta data dict.

.. thumbnail:: ./overview/11.png

Console
^^^^^^^

View/hide the viewer console

Help
----

Open docs
^^^^^^^^^

Open these docs


Console
=======

You can interact directly with the :ref:`work environment <ViewerWorkEnv>` using the console.

.. seealso:: :ref:`Viewer Core API <API_ViewerCore>`

Examples
--------

View meta data
^^^^^^^^^^^^^^

View history trace
^^^^^^^^^^^^^^^^^^

Open image
^^^^^^^^^^

Splice img seq
^^^^^^^^^^^^^^

Running scripts
===============

You can run scripts in the Viewer console to automate tasks such as batch creation. See the scripting guides <ref here> for more detail.
