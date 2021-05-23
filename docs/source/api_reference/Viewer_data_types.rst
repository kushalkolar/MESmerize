.. _API_ViewerCore:

Viewer Core
***********

Video Tutorial
==============

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/a1UO2-OhIHw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


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

Examples
========

.. include:: ./viewer_core_api_examples.rst
