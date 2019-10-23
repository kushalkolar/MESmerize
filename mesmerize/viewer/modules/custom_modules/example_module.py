from PyQt5 import QtWidgets

# You must define module_name.
# This is the name that will be displayed in the Custom Modules menu of the Viewer Window.
# You can also use this to reference ModuleGUI instance through the Viewer Console via ``get_module(<module_name>)``

module_name = 'Example Module'


# The main GUI class MUST be named ModuleGUI.
# You can have other classes and GUIs but this is the one that the viewer directly calls.

class ModuleGUI(QtWidgets.QDockWidget):
# The viewer MainWindow instance will pass a viewer instance
# that can be used to interact with the viewer and work environment.
    def __init__(self, parent, viewer_instance):
        QtWidgets.QDockWidget.__init__(self, parent)
        self.setFloating(True) # Must be floating
