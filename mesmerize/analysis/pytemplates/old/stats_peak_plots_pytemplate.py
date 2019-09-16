# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stats_peak_plots_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_stats_peak_plots_template(object):
    def setupUi(self, stats_peak_plots_template):
        stats_peak_plots_template.setObjectName("stats_peak_plots_template")
        stats_peak_plots_template.resize(709, 402)
        self.gridLayout = QtWidgets.QGridLayout(stats_peak_plots_template)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(stats_peak_plots_template)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(stats_peak_plots_template)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.curve_plot_all_group_peaks = PlotWidget(stats_peak_plots_template)
        self.curve_plot_all_group_peaks.setObjectName("curve_plot_all_group_peaks")
        self.gridLayout.addWidget(self.curve_plot_all_group_peaks, 1, 0, 1, 1)
        self.curve_plot_group_peaks = GraphicsLayoutWidget(stats_peak_plots_template)
        self.curve_plot_group_peaks.setObjectName("curve_plot_group_peaks")
        self.gridLayout.addWidget(self.curve_plot_group_peaks, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(stats_peak_plots_template)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.headmap_all_group_peaks = QtWidgets.QWidget(stats_peak_plots_template)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.headmap_all_group_peaks.sizePolicy().hasHeightForWidth())
        self.headmap_all_group_peaks.setSizePolicy(sizePolicy)
        self.headmap_all_group_peaks.setMinimumSize(QtCore.QSize(250, 190))
        self.headmap_all_group_peaks.setObjectName("headmap_all_group_peaks")
        self.gridLayout.addWidget(self.headmap_all_group_peaks, 3, 0, 1, 1)

        self.retranslateUi(stats_peak_plots_template)
        QtCore.QMetaObject.connectSlotsByName(stats_peak_plots_template)

    def retranslateUi(self, stats_peak_plots_template):
        _translate = QtCore.QCoreApplication.translate
        stats_peak_plots_template.setWindowTitle(_translate("stats_peak_plots_template", "Form"))
        self.label.setText(_translate("stats_peak_plots_template", "Peak traces - all groups. x0 = peak maxima"))
        self.label_2.setText(_translate("stats_peak_plots_template", "Peak traces - one subplot per group"))
        self.label_3.setText(_translate("stats_peak_plots_template", "Heatmaps of peaks - all groups, center = peak maxima"))

from pyqtgraphCore import GraphicsLayoutWidget, PlotWidget
