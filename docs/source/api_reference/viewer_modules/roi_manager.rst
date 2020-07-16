.. _API_ROIManager:

ROI Manager
***********

Video Tutorial
==============

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/a1UO2-OhIHw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

ModuleGUI
=========

The GUI QDockWidget that communicates with the :ref:`back-end managers <API_ROIManagers>`

.. autoclass:: mesmerize.viewer.modules.roi_manager.ModuleGUI
    :special-members:
    :members:
    :member-order: bysource

.. _API_ROIManagers:

Managers
========

The back-end managers that are used by the :ref:`ROI Manager ModuleGUI <API_ROIManager>`

The managers hold instances of :ref:`ROIs <API_ROITYPES>` in an instance of :ref:`ROIList <API_ROILIST>`

AbstractBaseManager
-------------------

Subclass this if you want to make your own Manager Back-end.

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.AbstractBaseManager
    :special-members:
    :members:
    :member-order: bysource

ManagerManual
-------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.ManagerManual
    :show-inheritance:
    :special-members:
    :members:
    :member-order: bysource
    
ManagerScatterROI
-----------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.ManagerScatterROI
    :show-inheritance:
    :special-members:
    :members:
    :member-order: bysource
    
ManagerVolROI
-------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.ManagerVolROI
    :show-inheritance:
    :special-members:
    :members:
    :member-order: bysource
    
ManagerVolCNMF
--------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.ManagerVolCNMF
    :show-inheritance:
    :special-members:
    :members:
    :member-order: bysource

ManagerCNMFROI
--------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.managers.ManagerCNMFROI
    :show-inheritance:
    :special-members:
    :members:
    :member-order: bysource


.. _API_ROIList:

ROI List
========

Used for holding instance of :ref:`ROIs <API_ROITypes>`

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_list.ROIList
    :special-members:
    :members:
    :private-members:
    :member-order: bysource

.. _API_ROITypes:

ROI Types
=========

A list of these are held by an instance of :ref:`ROIList <API_ROIList>`

AbstractBaseROI
---------------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types._AbstractBaseROI
    :special-members:
    :members:
    :member-order: bysource

BaseROI
-------

Subclass from this if you want to make your own ROI Type.

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types.BaseROI
    :show-inheritance:
    :members: __init__, get_roi_graphics_object, set_roi_graphics_object, reset_color, set_original_color, get_color, set_color, set_text, set_tag, get_tag, get_all_tags, add_to_viewer, remove_from_viewer, to_state, from_state
    :member-order: bysource
    
ManualROI
---------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types.ManualROI
    :show-inheritance:
    :members: __init__, curve_data, get_roi_graphics_object, set_roi_graphics_object, reset_color, set_original_color, get_color, set_color, set_text, set_tag, get_tag, get_all_tags, add_to_viewer, remove_from_viewer, to_state, from_state
    :member-order: bysource
    
.. _API_ScatterROI:
    
ScatterROI
----------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types.ScatterROI
    :show-inheritance:
    :members: __init__, get_roi_graphics_object, set_roi_graphics_object, reset_color, set_original_color, get_color, set_color, set_text, set_tag, get_tag, get_all_tags, add_to_viewer, remove_from_viewer, to_state, from_state, set_curve_data
    :member-order: bysource

VolCNMF
-------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types.VolCNMF
    :show-inheritance:
    :members: __init__, get_roi_graphics_object, set_roi_graphics_object, reset_color, set_original_color, get_color, set_color, set_text, set_tag, get_tag, get_all_tags, add_to_viewer, remove_from_viewer, to_state, from_state, set_curve_data, check_visible, set_zlevel
    :member-order: bysource

CNMFROI
-------

.. autoclass:: mesmerize.viewer.modules.roi_manager_modules.roi_types.CNMFROI
    :show-inheritance:
    :members: __init__, get_roi_graphics_object, set_roi_graphics_object, reset_color, set_original_color, get_color, set_color, set_text, set_tag, get_tag, get_all_tags, add_to_viewer, remove_from_viewer, to_state, from_state, set_curve_data
    :member-order: bysource
    
