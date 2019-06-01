from PyQt5 import QtWidgets

# You must define module_name.
# This is the str that will be displayed in the Custom Modules menu.
module_name = 'Example Module'


class ModuleGUI(QtWidgets.QDockWidget):
    # The viewer MainWindow instance will pass a viewer instance
    # that can be used to interact with the viewer and work environment.
    def __init__(self, parent, viewer_instance):
        QtWidgets.QDockWidget.__init__(self, parent)
        self.setFloating(True)
