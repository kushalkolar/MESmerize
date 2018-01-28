# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ProjBrowser_template.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial

class Ui_Form(object):
    def setupUi(self, Form, df, exclude, special):
        Form.setObjectName("Form")
        Form.resize(931, 775)
        self.BtnConsole = QtWidgets.QPushButton(Form)
        self.BtnConsole.setGeometry(QtCore.QRect(10, 740, 80, 26))
        self.BtnConsole.setObjectName("BtnConsole")
        self.BtnJupyter = QtWidgets.QPushButton(Form)
        self.BtnJupyter.setGeometry(QtCore.QRect(100, 740, 101, 26))
        self.BtnJupyter.setObjectName("BtnJupyter")
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(11, 460, 911, 262))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.BtnPlot = QtWidgets.QPushButton(self.layoutWidget)
        self.BtnPlot.setEnabled(False)
        self.BtnPlot.setObjectName("BtnPlot")
        self.horizontalLayout_3.addWidget(self.BtnPlot)
        self.BtnCopyFilters = QtWidgets.QPushButton(self.layoutWidget)
        self.BtnCopyFilters.setEnabled(False)
        self.BtnCopyFilters.setObjectName("BtnCopyFilters")
        self.BtnCopyFilters.setText('Copy Filters')
        self.horizontalLayout_3.addWidget(self.BtnCopyFilters)
        self.BtnResetFilters = QtWidgets.QPushButton(self.layoutWidget)
        self.BtnResetFilters.setEnabled(False)
        self.BtnResetFilters.setObjectName("BtnResetFilters")
        self.horizontalLayout_3.addWidget(self.BtnResetFilters)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.progressBar = QtWidgets.QProgressBar(self.layoutWidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.curvesPlotWidget = PlotWidget(self.layoutWidget)
        self.curvesPlotWidget.setObjectName("curvesPlotWidget")
        self.horizontalLayout.addWidget(self.curvesPlotWidget)
        self.boxPlotPlotWidget = PlotWidget(self.layoutWidget)
        self.boxPlotPlotWidget.setObjectName("boxPlotPlotWidget")
        self.horizontalLayout.addWidget(self.boxPlotPlotWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        colContainerWidth = 241 * (len(df.columns) - len(exclude))
        
        self.widgetMasterColumnsContainer = QtWidgets.QWidget(Form)
        self.widgetMasterColumnsContainer.setGeometry(QtCore.QRect(0, 0, colContainerWidth, 331))
        self.widgetMasterColumnsContainer.setObjectName("widgetMasterColumnsContainer")
        
        
        self.widget = []
        self.gridLayout = []
        self.labelColumn_ = []
        self.rad_ =[]
        self.listw_ =[]
        self.lineEdFilter_ =[]
        self.BtnApply_ =[]
        self.BtnReset_ =[]
        
        
        
        colNum = -1
        
        for col in df.columns:
            if col not in exclude:
                colNum += 1
                self.widget.append(QtWidgets.QWidget(self.widgetMasterColumnsContainer))
                self.widget[colNum].setGeometry(QtCore.QRect((10 + colNum * 231), 10, 225, 321))
                self.widget[colNum].setObjectName("widget"+str(colNum))
                self.gridLayout.append(QtWidgets.QGridLayout(self.widget[colNum]))
                self.gridLayout[colNum].setContentsMargins(0, 0, 0, 0)
                self.gridLayout[colNum].setObjectName("gridLayout"+str(colNum))
                self.labelColumn_.append(QtWidgets.QLabel(self.widget[colNum]))
                font = QtGui.QFont()
                font.setBold(True)
                font.setWeight(75)
                self.labelColumn_[colNum].setFont(font)
                self.labelColumn_[colNum].setAccessibleDescription("")
                self.labelColumn_[colNum].setObjectName("labelColumn_"+str(colNum))
                self.gridLayout[colNum].addWidget(self.labelColumn_[colNum], 0, 0, 1, 1)
                self.rad_.append(QtWidgets.QRadioButton(self.widget[colNum]))
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.rad_[colNum].sizePolicy().hasHeightForWidth())
                self.rad_[colNum].setSizePolicy(sizePolicy)
                self.rad_[colNum].setMaximumSize(QtCore.QSize(70, 16777215))
                self.rad_[colNum].setAccessibleDescription("")
                self.rad_[colNum].setChecked(False)
                self.rad_[colNum].setObjectName("rad_"+str(colNum))
                self.gridLayout[colNum].addWidget(self.rad_[colNum], 0, 1, 1, 2)
                self.listw_.append(QtWidgets.QListWidget(self.widget[colNum]))
                self.listw_[colNum].setAccessibleDescription("")
                self.listw_[colNum].setObjectName(str(col))
                self.listw_[colNum].setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
                self.gridLayout[colNum].addWidget(self.listw_[colNum], 1, 0, 1, 3)
                self.lineEdFilter_.append(QtWidgets.QLineEdit(self.widget[colNum]))
                self.lineEdFilter_[colNum].setAccessibleDescription("")
                self.lineEdFilter_[colNum].setInputMask("")
                self.lineEdFilter_[colNum].setObjectName("lineEdFilter_"+str(colNum))
                self.lineEdFilter_[colNum].setToolTip('Separate multiple filters using  ( | )')
                
                self.listw_[colNum].itemSelectionChanged.connect(partial(self.setLineEdFilter, colNum))
                
                self.gridLayout[colNum].addWidget(self.lineEdFilter_[colNum], 2, 0, 1, 1)
                self.BtnApply_.append(QtWidgets.QPushButton(self.widget[colNum]))
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.BtnApply_[colNum].sizePolicy().hasHeightForWidth())
                self.BtnApply_[colNum].setSizePolicy(sizePolicy)
                self.BtnApply_[colNum].setMaximumSize(QtCore.QSize(45, 16777215))
                self.BtnApply_[colNum].setAccessibleDescription("")
                self.BtnApply_[colNum].setObjectName("BtnApply_"+str(colNum))
                self.gridLayout[colNum].addWidget(self.BtnApply_[colNum], 2, 1, 1, 1)
                self.BtnReset_.append(QtWidgets.QPushButton(self.widget[colNum]))
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.BtnReset_[colNum].sizePolicy().hasHeightForWidth())
                self.BtnReset_[colNum].setSizePolicy(sizePolicy)
                self.BtnReset_[colNum].setMaximumSize(QtCore.QSize(50, 16777215))
                self.BtnReset_[colNum].setAccessibleDescription("")
                self.BtnReset_[colNum].setObjectName("BtnReset_"+str(colNum))
                self.BtnReset_[colNum].clicked.connect(partial(self.resetLineEdFilter, colNum))
                self.gridLayout[colNum].addWidget(self.BtnReset_[colNum], 2, 2, 1, 1)
                
                self.labelColumn_[colNum].setText(str(col))
                self.rad_[colNum].setText("Unique")
                self.lineEdFilter_[colNum].setPlaceholderText("Filter")
                self.BtnApply_[colNum].setText("Apply")
                self.BtnReset_[colNum].setText("Reset")
                
                # Just support for one timing based column now
                if col in special['Timings']:
                    self.widgetSetx0Container = QtWidgets.QWidget(Form)
                    self.widgetSetx0Container.setGeometry(QtCore.QRect((20 + colNum * 231) , 400, 201, 51))
                    self.widgetSetx0Container.setObjectName("widgetSetx0Container")
                    self.widget1 = QtWidgets.QWidget(self.widgetSetx0Container)
                    self.widget1.setGeometry(QtCore.QRect(0, 0, 196, 50))
                    self.widget1.setObjectName("widget1")
                    self.gridLayout_3 = QtWidgets.QGridLayout(self.widget1)
                    self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
                    self.gridLayout_3.setObjectName("gridLayout_3")
                    self.label_4 = QtWidgets.QLabel(self.widget1)
                    self.label_4.setObjectName("label_4")
                    self.gridLayout_3.addWidget(self.label_4, 0, 1, 1, 1)
                    self.radTStart = QtWidgets.QRadioButton(self.widget1)
                    self.radTStart.setChecked(False)
                    self.radTStart.setObjectName("radTStart")
                    self.gridLayout_3.addWidget(self.radTStart, 1, 0, 1, 1)
                    self.radTEnd = QtWidgets.QRadioButton(self.widget1)
                    self.radTEnd.setObjectName("radTEnd")
                    self.gridLayout_3.addWidget(self.radTEnd, 1, 1, 1, 1)
                    self.radTCenter = QtWidgets.QRadioButton(self.widget1)
                    self.radTCenter.setObjectName("radTCenter")
                    self.gridLayout_3.addWidget(self.radTCenter, 1, 2, 1, 1)
                    self.widget2 = QtWidgets.QWidget(Form)
                    self.widget2.setGeometry(QtCore.QRect((10 + colNum * 231), 340, 231, 62))
                    self.widget2.setObjectName("widget2")
                    self.gridLayout_2 = QtWidgets.QGridLayout(self.widget2)
                    self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
                    self.gridLayout_2.setObjectName("gridLayout_2")
                    self.label_3 = QtWidgets.QLabel(self.widget2)
                    self.label_3.setObjectName("label_3")
                    self.gridLayout_2.addWidget(self.label_3, 0, 0, 2, 1)
                    self.label = QtWidgets.QLabel(self.widget2)
                    self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
                    self.label.setObjectName("label")
                    self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
                    self.spinBoxTStart = QtWidgets.QDoubleSpinBox(self.widget2)
                    self.spinBoxTStart.setMaximum(99900.0)
                    self.spinBoxTStart.setMinimum(-9900.0)
                    self.spinBoxTStart.setObjectName("spinBoxTStart")
                    self.gridLayout_2.addWidget(self.spinBoxTStart, 0, 2, 1, 1)
                    self.label_2 = QtWidgets.QLabel(self.widget2)
                    self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
                    self.label_2.setObjectName("label_2")
                    self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)
                    self.spinBoxTEnd = QtWidgets.QDoubleSpinBox(self.widget2)
                    self.spinBoxTEnd.setMaximum(99900.0)
                    self.spinBoxTEnd.setMinimum(-9900.0)
                    self.spinBoxTEnd.setObjectName("spinBoxTEnd")
                    self.gridLayout_2.addWidget(self.spinBoxTEnd, 1, 2, 1, 1)
                    self.label_4.setText("Set x0 =")
                    self.radTStart.setText("tStart")
                    self.radTEnd.setText("tEnd")
                    self.radTCenter.setText("tCenter")
                    self.label_3.setText("Set offsets: ")
                    self.label.setText("tStart (s): ")
                    self.label_2.setText("tEnd (s): ")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        
    def setLineEdFilter(self, colNum):
        f = ''
        for item in self.listw_[colNum].selectedItems():
            f = f + '|' + item.text()
        f = f[1:]
        self.lineEdFilter_[colNum].setText(f)
    
    def resetLineEdFilter(self, colNum):
        self.lineEdFilter_[colNum].setText('')
        self.listw_[colNum].clearSelection()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.BtnConsole.setText(_translate("Form", "Console"))
        self.BtnJupyter.setText(_translate("Form", "Send to Jupyter"))
        self.BtnPlot.setText(_translate("Form", "Plot!"))
        self.BtnResetFilters.setText(_translate("Form", "Reset Filters"))
        
        
        
        


from pyqtgraphCore import PlotWidget
