# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'beeswarm_plots_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_beeswarm_plots_template(object):
    def setupUi(self, beeswarm_plots_template):
        beeswarm_plots_template.setObjectName("beeswarm_plots_template")
        beeswarm_plots_template.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(beeswarm_plots_template)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = GraphicsLayoutWidget(beeswarm_plots_template)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)

        self.retranslateUi(beeswarm_plots_template)
        QtCore.QMetaObject.connectSlotsByName(beeswarm_plots_template)

    def retranslateUi(self, beeswarm_plots_template):
        _translate = QtCore.QCoreApplication.translate
        beeswarm_plots_template.setWindowTitle(_translate("beeswarm_plots_template", "Form"))

from pyqtgraphCore import GraphicsLayoutWidget
