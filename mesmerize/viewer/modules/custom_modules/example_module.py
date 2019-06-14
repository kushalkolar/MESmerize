# This is an example of how to create your own viewer module.
# Simply create a file with this structure and place it in viewer/modules/custom_modules.
# All files in this directory are automatically imported and made accessible

from PyQt5 import QtWidgets

# You must define module_name.
# This is the str that will be displayed in the Custom Modules menu.
# This is also the str you can use to reference this module's ModuleGUI instance
# from the console using get_module().
module_name = 'Example Module'


# The main GUI class MUST be named ModuleGUI.
# You can have other classes and GUIs but this is the one that the viewer directly calls.
class ModuleGUI(QtWidgets.QDockWidget):
    # The viewer MainWindow instance will pass a viewer instance
    # that can be used to interact with the viewer and work environment.
    def __init__(self, parent, viewer_instance):
        QtWidgets.QDockWidget.__init__(self, parent)
        self.setFloating(True)
