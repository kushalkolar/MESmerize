.. _develop_ViewerModules:

Viewer Modules
**************

Viewer modules appear as either QDockWidgets or QWidgets to the user. They must consist of a main ``ModuleGUI`` class which inherits from either QDockWidget or QWidget. They can utilize any additional python modules, classes, etc.

Instructions
============

#. Create a directory plugins directory if you don't have one. If you are using a snap installation this has to be within your home folder. Set this plugins directory in the :ref:`SystemConfiguration`. This directory can contain as many custom modules as you want. All python modules within the plugins directory are automatically imported.

#. Download the `__init__.py <https://github.com/kushalkolar/MESmerize/raw/master/mesmerize/viewer/modules/custom_modules/__init__.py>`_ and place it within the plugins directory.

#. Create the main module file for your custom module. This file can be named as you wish and must use the struture outlined below. In addition to this main module file you can create a directory to house any other modules, files etc. You can create Qt templates using Qt Creator and convert them to .py template files using pyuic5 and use them for your custom module.
    
    **Basic Structure**
    
    .. code-block:: python
        :linenos:
        
        from PyQt5 import QtWidgets
        
        module_name = 'Example Module'
        
        # You must define module_name.
        # This is the name that will be displayed in the "Plugins" menu of the Viewer Window.
        # You can use this to reference the ModuleGUI instance through the Viewer Console via ``get_module(<module_name>)``


        # The main GUI class MUST be named ModuleGUI.
        # You can have other classes and more GUIs however ModuleGUI is the one that the Viewer Window directly calls.
        
        class ModuleGUI(QtWidgets.QDockWidget):
            # The Viewer MainWindow will pass its Viewer instance that can be used to interact with the viewer and work environment.
            def __init__(self, parent, viewer_instance):
                QtWidgets.QDockWidget.__init__(self, parent)
                self.setFloating(True) # Must be floating

#. The module will be accessible through the Viewer Window's "Plugins" menu. The names in the plugins menu will correspond to the aforementioned ``module_name`` variable.
