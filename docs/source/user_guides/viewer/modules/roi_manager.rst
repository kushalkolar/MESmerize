.. _ROIManager:

ROI Manager
***********

:ref:`API Reference <API_ROIManager>`

**Manage and annotate ROIs**

.. thumbnail:: ./roi_manager_viewer.png

The ROI Manager has a manual mode, to draw ROIs manually, and a CNMF(E) mode where ROIs can be imported from CNMF(E) outputs.

.. seealso:: :ref:`CNMF Usage <module_CNMF_Usage>` and :ref:`CNMFE Usage <module_CNMFE_Usage>`.

.. note:: You cannot combine manual and CNMF(E) ROIs in the same sample.


The ImageJ ROI import uses the read-roi package by Hadrien Mary https://pypi.org/project/read-roi/

Layout
======

.. image:: ./roi_manager.png

**Controls**

========================    ==========================================
UI                          Description
========================    ==========================================
Add ROI button              Add Polygon ROI (Manual mode)

                            | Right click this button to add an elliptical ROI
                            
Show all                    Show all ROIs in the viewer
Live plot                   Live update of the curve plot with changes (Manual mode)
Plot                        Plot the curves (Manual mode)
Import from ImageJ          Import ROIs from an ImageJ ROIs zip file (Manual mode)
Switch to manual ...        Switch to Manual mode. Clears CNMF(E) ROIs.

ROIs list                   Color-coded list of ROIs.

                            | Left click to highlight the ROI in the viewer
                            
                            | Right click to show the context menu allowing you to delete the selected ROI
                            
Tags list                   List of tags for the selected ROI

                            | Correspond to the :ref:`ROI Type Columns of the Project Configuration <ROITypeColumns>`
                            
Add Tag to ROI Def...       Set the tag for the current selection in the Tags list
Set ROI Tag                 Click to set the tag, or just press return in the text entry above
========================    ==========================================


.. note:: It is generally advisable to keep your ROI tags short with lowercase letters. When sharing your project you can provide a mapping for all your keys. This helps maintain consistency throughout your project and makes the data more readable.


**Keyboard shortcuts**.

These only work when the ROI manager is docked within the Viewer and while you are typing in the *Add Tag to ROI Definition* text entry.

=============    ==========================================
Key                 Description
=============    ==========================================
Page Up             Select previous ROI
Page Down           Select next ROI
Right Arrow         Play the video at high speed
Left Arrow          Play the video backwards at high speed
Home                Go to the beginning of the video
End                 Go to the end of the video
=============    ==========================================


Manual ROI Mode
===============

When you click the "Add ROI" button to add a Manual Polygon ROI, a new rectangular ROI will be add in the top left corner of the image. You can add new vertices to this polygon by clicking on any of its edges. You can drag the vertices to change the shape of the polygon, and you can drag the entire ROI as well by clicking and dragging within the ROI region. Similarly you can reshape elliptical ROIs.

Hovering over the ROI selects it in the ROI list.

Console
=======

Access the back-end ROI Manager through the viewer console or :ref:`Script editor <ScriptEditor>` to interact with the ROIs.

.. seealso:: :ref:`Back-end ROI Manager APIs <API_ROIManagers>`, :ref:`ROIList API <API_ROIList>`, :ref:`ROI Type APIs <API_ROITypes>`

Get the back-end ROI Manager, see :ref:`ROI Manager APIs <API_ROIManagers>`

.. code-block:: python
    
    >>> get_workEnv().roi_manager
    
    <mesmerize.viewer.modules.roi_manager_modules.managers.ManagerCNMFROI object at 0x7f01b8780668>``
   
Get the ROI List, see :ref:`ROIList API <API_ROIList>`

.. code-block:: python

    >>> get_workEnv().roi_manager.roi_list
    
    [<mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI object at 0x7f01bc78b278>, <mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI object at 0x7f01bc817630>, <mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI object at 0x7f01bc817668>, <mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI object at 0x7f01bc7c5438>, <mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI object at 0x7f01bc7c5208>]
    

Work with an ROI object, see :ref:`ROI Type APIs <API_ROITypes>`

.. code-block:: python

    # Get the curve data of an ROI
    >>> get_workEnv().roi_manager.roi_list[3].curve_data
    
    (array([   0,    1,    2, ..., 2995, 2996, 2997]), array([ -207.00168389,  -161.78229208,  -157.62522988, ..., -1017.73174502,
       -1030.27047731, -1042.26989668]))
       
    # Get the tags of an ROI
    >>> get_workEnv().roi_manager.roi_list[2].get_all_tags()
    
    {'anatomical_location': 'tail', 'cell_name': 'dcen', 'morphology': 'untagged'}
    
    # Get a single tag
    >>> get_workEnv().roi_manager.roi_list[2].get_tag('cell_name')
    
    'dcen'
    
