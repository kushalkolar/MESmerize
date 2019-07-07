from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal, QEvent, Qt


class ROITagLineEdit(QLineEdit):
    sig_key_left = pyqtSignal()
    sig_key_right = pyqtSignal()
    sig_key_end = pyqtSignal()
    sig_key_home = pyqtSignal()

    def __init__(self, parent):
        super(ROITagLineEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.type() == QEvent.KeyPress:
            if QKeyEvent.key() == Qt.Key_Left:
                self.sig_key_left.emit()
                QKeyEvent.accept()

            elif QKeyEvent.key() == Qt.Key_Right:
                self.sig_key_right.emit()
                QKeyEvent.accept()

            elif QKeyEvent.key() == Qt.Key_Home:
                self.sig_key_home.emit()
                QKeyEvent.accept()

            elif QKeyEvent.key() == Qt.Key_End:
                self.sig_key_end.emit()
                QKeyEvent.accept()
        
        super(ROITagLineEdit, self).keyPressEvent(QKeyEvent)
