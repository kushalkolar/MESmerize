These examples can be run through the viewer console or :ref:`Script editor <module_ScriptEditor>` to interact with the ROIs.

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
