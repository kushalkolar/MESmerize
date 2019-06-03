from ..Qt import QtGui, QtCore
from ast import literal_eval


class KwargPlainTextEdit(QtGui.QPlainTextEdit):
    """Just a plain text entry widget with helper functions to use for passing kwargs"""
    def __init__(self, parent=None, *args, **kwargs):
        QtGui.QPlainTextEdit.__init__(self, parent, *args, **kwargs)

    def get_kwargs(self) -> dict:
        t = self.toPlainText()

        if t == '':
            return dict()

        return dict((k, literal_eval(v)) for k, v in (pair.split('=') for pair in t))

    def set_kwargs(self, d: dict):
        t = ', '.join("%s=%r" % (k, v) for (k, v) in d.items())
        self.setPlainText(t)
