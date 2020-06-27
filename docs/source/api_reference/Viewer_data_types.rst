.. _API_ViewerCore:

Viewer Core
***********

.. _API_ViewerWorkEnv:

ViewerWorkEnv
=======================

This objects stores the data that the :ref:`Viewer <ViewerOverview>` interacts with.

.. autoclass:: mesmerize.viewer.core.ViewerWorkEnv
    :special-members:
    :members:
    :private-members:

.. _API_ImgData:

ImgData
=======

.. autoclass:: mesmerize.viewer.core.data_types.ImgData
    :members: __init__
    
.. _API_ViewerUtils:

ViewerUtils
===========

The :ref:`Viewer <ViewerOverview>` is usually not interacted with directly from modules outside of the viewer (such as viewer modules. They instead use the ViewerUtils class which includes helper functions and a reference to the viewer.

.. autoclass:: mesmerize.viewer.core.ViewerUtils
  :special-members:
  :members:
  :private-members:
  
.. _API_Mesfile:

Mesfile
=======
.. autoclass:: mesmerize.viewer.core.mesfile.MES
    :special-members:
    :members:
    :private-members:
