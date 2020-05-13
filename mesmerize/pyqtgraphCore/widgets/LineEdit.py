"""
Subclass of QLineEdit because for whatever reason
the returnPressed signal causes the entire application
to crash when used in flowchart parameter widgets.
"""


from PyQt5 import QtWidgets


class DummySignal:
    def connect(self, *args, **kwargs):
        pass


class LineEdit(QtWidgets.QLineEdit):
    def returnPressed(self, *args, **kwargs):
        return DummySignal()

    def saveState(self):
        return self.text()

    def restoreState(self, txt):
        self.setText(txt)

    def widgetGroupInterface(self):
        return (self.returnPressed, self.saveState, self.restoreState)
