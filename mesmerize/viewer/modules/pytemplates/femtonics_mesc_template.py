# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './femtonics_mesc_template.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName("DockWidget")
        DockWidget.resize(639, 697)
        DockWidget.setFloating(True)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_mesc_file = QtWidgets.QWidget()
        self.tab_mesc_file.setObjectName("tab_mesc_file")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_mesc_file)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_open_file = QtWidgets.QPushButton(self.tab_mesc_file)
        self.pushButton_open_file.setObjectName("pushButton_open_file")
        self.horizontalLayout.addWidget(self.pushButton_open_file)
        self.label_current_file_name = QtWidgets.QLabel(self.tab_mesc_file)
        self.label_current_file_name.setText("")
        self.label_current_file_name.setObjectName("label_current_file_name")
        self.horizontalLayout.addWidget(self.label_current_file_name)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.pushButton_close_file = QtWidgets.QPushButton(self.tab_mesc_file)
        self.pushButton_close_file.setObjectName("pushButton_close_file")
        self.horizontalLayout_4.addWidget(self.pushButton_close_file)
        spacerItem1 = QtWidgets.QSpacerItem(37, 33, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.tab_mesc_file)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidget_session = ListWidget(self.tab_mesc_file)
        self.listWidget_session.setObjectName("listWidget_session")
        self.verticalLayout.addWidget(self.listWidget_session)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.tab_mesc_file)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.listWidget_unit = ListWidget(self.tab_mesc_file)
        self.listWidget_unit.setObjectName("listWidget_unit")
        self.verticalLayout_2.addWidget(self.listWidget_unit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.tab_mesc_file)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.listWidget_channel = ListWidget(self.tab_mesc_file)
        self.listWidget_channel.setObjectName("listWidget_channel")
        self.verticalLayout_3.addWidget(self.listWidget_channel)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.tab_mesc_file)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.lineEdit_comment = QtWidgets.QLineEdit(self.tab_mesc_file)
        self.lineEdit_comment.setReadOnly(True)
        self.lineEdit_comment.setObjectName("lineEdit_comment")
        self.horizontalLayout_5.addWidget(self.lineEdit_comment)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.label_4 = QtWidgets.QLabel(self.tab_mesc_file)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_import_image = QtWidgets.QPushButton(self.tab_mesc_file)
        self.pushButton_import_image.setObjectName("pushButton_import_image")
        self.horizontalLayout_3.addWidget(self.pushButton_import_image)
        self.pushButton_import_stim_map = QtWidgets.QPushButton(self.tab_mesc_file)
        self.pushButton_import_stim_map.setObjectName("pushButton_import_stim_map")
        self.horizontalLayout_3.addWidget(self.pushButton_import_stim_map)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab_mesc_file, "")
        self.tab_stimulus_mapping = QtWidgets.QWidget()
        self.tab_stimulus_mapping.setObjectName("tab_stimulus_mapping")
        self.tabWidget.addTab(self.tab_stimulus_mapping, "")
        self.verticalLayout_4.addWidget(self.tabWidget)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)
        DockWidget.setTabOrder(self.tabWidget, self.pushButton_open_file)
        DockWidget.setTabOrder(self.pushButton_open_file, self.pushButton_close_file)
        DockWidget.setTabOrder(self.pushButton_close_file, self.listWidget_session)
        DockWidget.setTabOrder(self.listWidget_session, self.listWidget_unit)
        DockWidget.setTabOrder(self.listWidget_unit, self.listWidget_channel)
        DockWidget.setTabOrder(self.listWidget_channel, self.lineEdit_comment)
        DockWidget.setTabOrder(self.lineEdit_comment, self.pushButton_import_image)
        DockWidget.setTabOrder(self.pushButton_import_image, self.pushButton_import_stim_map)

    def retranslateUi(self, DockWidget):
        _translate = QtCore.QCoreApplication.translate
        DockWidget.setWindowTitle(_translate("DockWidget", "Doc&kWidget"))
        self.pushButton_open_file.setText(_translate("DockWidget", "Open .mesc file"))
        self.pushButton_close_file.setToolTip(_translate("DockWidget", "Close the file handle, allows the file to be accessible by other programs"))
        self.pushButton_close_file.setText(_translate("DockWidget", "Close file"))
        self.label.setText(_translate("DockWidget", "Session"))
        self.label_2.setText(_translate("DockWidget", "Unit"))
        self.label_3.setText(_translate("DockWidget", "Channel"))
        self.label_5.setText(_translate("DockWidget", "Comment:"))
        self.lineEdit_comment.setToolTip(_translate("DockWidget", "Comment stored in the selected MUnit"))
        self.label_4.setText(_translate("DockWidget", "Import:"))
        self.pushButton_import_image.setText(_translate("DockWidget", "Image"))
        self.pushButton_import_stim_map.setText(_translate("DockWidget", "Stim Map"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_mesc_file), _translate("DockWidget", "MESc File"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_stimulus_mapping), _translate("DockWidget", "Stimulus Mapping"))

from ....pyqtgraphCore.widgets.ListWidget import ListWidget
