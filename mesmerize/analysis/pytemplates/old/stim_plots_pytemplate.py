# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stim_plots_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_stim_plots_template(object):
    def setupUi(self, stim_plots_template):
        stim_plots_template.setObjectName("stim_plots_template")
        stim_plots_template.resize(767, 411)
        self.gridLayout = QtWidgets.QGridLayout(stim_plots_template)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(stim_plots_template)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(stim_plots_template)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1)
        self.stim_plots_overlays = PlotWidget(stim_plots_template)
        self.stim_plots_overlays.setObjectName("stim_plots_overlays")
        self.gridLayout.addWidget(self.stim_plots_overlays, 1, 0, 1, 1)
        self.stim_plots_groups = GraphicsLayoutWidget(stim_plots_template)
        self.stim_plots_groups.setObjectName("stim_plots_groups")
        self.gridLayout.addWidget(self.stim_plots_groups, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(stim_plots_template)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.headmaps_widget = QtWidgets.QWidget(stim_plots_template)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.headmaps_widget.sizePolicy().hasHeightForWidth())
        self.headmaps_widget.setSizePolicy(sizePolicy)
        self.headmaps_widget.setMinimumSize(QtCore.QSize(250, 190))
        self.headmaps_widget.setObjectName("headmaps_widget")
        self.gridLayout.addWidget(self.headmaps_widget, 3, 0, 1, 1)

        self.retranslateUi(stim_plots_template)
        QtCore.QMetaObject.connectSlotsByName(stim_plots_template)

    def retranslateUi(self, stim_plots_template):
        _translate = QtCore.QCoreApplication.translate
        stim_plots_template.setWindowTitle(_translate("stim_plots_template", "Form"))
        self.label_4.setText(_translate("stim_plots_template", "All groups"))
        self.label_5.setText(_translate("stim_plots_template", "Group subplots"))
        self.label_6.setText(_translate("stim_plots_template", "Heatmaps all groups"))

from pyqtgraphCore import GraphicsLayoutWidget, PlotWidget
