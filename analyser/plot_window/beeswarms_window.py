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
from .beeswarms import *


class ControlWidget(QtWidgets.QWidget, Ui_BeeswarmControls):
    signal_changed = QtCore.pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super(ControlWidget, self).__init__(parent)#parent)
        self.setupUi(parent)

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

        # self.plot_obj = BeeswarmPlot(self.ui.graphicsView, self)
        # self.plot_obj.signal_spot_clicked.connect(print)

        self.ui.groupBoxSpecific.setLayout(QtWidgets.QVBoxLayout())
        self.control_widget = ControlWidget(self.ui.groupBoxSpecific)
        self.ui.groupBoxSpecific.layout().addWidget(self.control_widget)

        self.add_plot_tab('Beeswarm')
        self.beeswarm_plot = BeeswarmPlot(self.graphicsViews['Beeswarm'])
        self.add_plot_tab('Violins')

        self.beeswarm_plot.signal_spot_clicked.connect(print)

    def update_params(self):
        super(BeeswarmPlotWindow, self).update_params()
        spot_size = self.control_widget.horizontalSliderSpotSize.value()
        self.update_beeswarm()
        self.update_violins()

    def update_beeswarm(self):
        self.beeswarm_plot.clear_plot()
        colors = self.auto_colormap(len(self.groups))
        for i, data_column in enumerate(self.data_columns):
            msg = 'Progress: ' + str((i / len(self.data_columns)) * 100) + ' % ,Plotting data column: ' + data_column
            self.status_bar.showMessage(msg)
            self.beeswarm_plot.add_plot(data_column)
            for ii, (dataframe, group) in enumerate(zip(self.group_dataframes, self.groups)):
                self.status_bar.showMessage(msg + ', plotting group: ' + group)
                self.beeswarm_plot.add_data_to_plot(i, data_series=dataframe[data_column],
                                                    uuid_series=dataframe[self.uuid_column],
                                                    name=group, color=colors[ii])

        # for ix, column in enumerate(data_columns):
        #     self.plot_obj.add_plot(column)
        #     self.add_data_to_plot(ix)
        #     # TODO: THINK ABOUT GROUPING. PROBABLY PUT IT IN THE PARENT CLASS!!!
        #     # TODO: PROBABLY CREATE A COMMON CONTROL WIDGET, AND DIFFERENT PLOT TYPES HAVE THEIR OWN ON TOP OF THAT!!

    def update_violins(self):
        pass

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    bpw = BeeswarmPlotWindow()
    bpw.show()
    app.exec_()
