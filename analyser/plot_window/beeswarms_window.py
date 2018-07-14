#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .window import *
from .pytemplates.beeswarm_plot_controls_pytemplate import *
from .beeswarms_universal import *


class ControlWidget(QtWidgets.QWidget, Ui_BeeswarmControls):
    signal_changed = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(ControlWidget, self).__init__(parent)
        self.setupUi(parent)

        self.btnApply.clicked.connect(self.apply_all_settings)

    def apply_all_settings(self):
        data_columns = self.listWidgetDataColumns.selectedItems()
        if self.radioButtonGroupBySingleColumn.isChecked():
            if self.comboBoxGrouping.currentText() == '':
                QtWidgets.QMessageBox.warning(None, 'Invalid parameters', 'Invalid grouping option')
                return
            grouping = {'type': 'column', 'column_name': self.comboBoxGrouping.currentText()}

        elif self.radioButtonGroupByTransmissions.isChecked():
            grouping = {'type': 'transmissions'}

        else:
            QtWidgets.QMessageBox.warning(None, 'Invalid parameters', 'No grouping selected')
            return

        self.signal_changed.emit(data_columns, grouping)


class BeeswarmPlotWindow(PlotWindow):
    def __init__(self, parent=None):
        super(BeeswarmPlotWindow, self).__init__(parent)

        self.control_widget = ControlWidget(parent=self.ui.tabWidget.widget(0))
        self.control_widget.signal_changed.connect(self.set_plot)
        self.plot_obj = BeeswarmPlot(self.ui.graphicsView, self)

    @QtCore.pyqtSlot(str, dict)
    def set_plot(self, data_columns: str, grouping: dict):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bpw = BeeswarmPlotWindow()
    bpw.show()
    app.exec_()