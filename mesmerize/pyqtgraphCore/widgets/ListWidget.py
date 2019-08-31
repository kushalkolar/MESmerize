from PyQt5 import QtCore, QtWidgets


class ListWidget(QtWidgets.QListWidget):
    """QListWidget with a signal blocker for set_items"""

    def blockSignals(func, *args):
        def fn(self, *args, **kwds):
            blocked = self.signalsBlocked()
            self.blockSignals(True)
            try:
                ret = func(self, *args, **kwds)
            finally:
                self.blockSignals(blocked)

            return ret

        return fn

    @blockSignals
    def setItems(self, items: list):
        previous_items = [self.item(ix).text() for ix in range(self.count())]
        if set(items) == previous_items:
            return

        selected_items = [item.text() for item in self.selectedItems()]

        self.clear()
        self.addItems(items)

        for selected_item in selected_items:
            item = self.findItems(selected_item, QtCore.Qt.MatchExactly)
            if len(item) == 0:
                continue
            item = item[0]
            item.setSelected(True)

    def getSelectedItems(self) -> list:
        return [item.text() for item in self.selectedItems()]

    def setSelectedItems(self, items: list):
        for item in items:
            item = self.findItems(item, QtCore.Qt.MatchExactly)
            if len(item) == 0:
                continue
            item = item[0]
            item.setSelected(True)
