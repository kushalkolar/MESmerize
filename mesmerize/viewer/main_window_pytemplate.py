# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window_pytemplate.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuModules = QtWidgets.QMenu(self.menubar)
        self.menuModules.setObjectName("menuModules")
        self.menuLoad_images = QtWidgets.QMenu(self.menuModules)
        self.menuLoad_images.setObjectName("menuLoad_images")
        self.menuCaImAn_toolbox = QtWidgets.QMenu(self.menuModules)
        self.menuCaImAn_toolbox.setObjectName("menuCaImAn_toolbox")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuCustom_Modules = QtWidgets.QMenu(self.menubar)
        self.menuCustom_Modules.setObjectName("menuCustom_Modules")
        self.menuImage = QtWidgets.QMenu(self.menubar)
        self.menuImage.setObjectName("menuImage")
        self.menuProjections = QtWidgets.QMenu(self.menuImage)
        self.menuProjections.setObjectName("menuProjections")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockConsole = QtWidgets.QDockWidget(MainWindow)
        self.dockConsole.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockConsole.setObjectName("dockConsole")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.dockConsole.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockConsole)
        self.actionOpen_work_environment = QtWidgets.QAction(MainWindow)
        self.actionOpen_work_environment.setObjectName("actionOpen_work_environment")
        self.actionSave_work_environment = QtWidgets.QAction(MainWindow)
        self.actionSave_work_environment.setObjectName("actionSave_work_environment")
        self.actionMesfile = QtWidgets.QAction(MainWindow)
        self.actionMesfile.setCheckable(False)
        self.actionMesfile.setObjectName("actionMesfile")
        self.actionTiff_file = QtWidgets.QAction(MainWindow)
        self.actionTiff_file.setCheckable(False)
        self.actionTiff_file.setObjectName("actionTiff_file")
        self.actionMotion_Correction = QtWidgets.QAction(MainWindow)
        self.actionMotion_Correction.setCheckable(False)
        self.actionMotion_Correction.setObjectName("actionMotion_Correction")
        self.actionCNMF = QtWidgets.QAction(MainWindow)
        self.actionCNMF.setCheckable(False)
        self.actionCNMF.setObjectName("actionCNMF")
        self.actionROI_Manager = QtWidgets.QAction(MainWindow)
        self.actionROI_Manager.setCheckable(False)
        self.actionROI_Manager.setObjectName("actionROI_Manager")
        self.actionManual_motion_correction = QtWidgets.QAction(MainWindow)
        self.actionManual_motion_correction.setCheckable(False)
        self.actionManual_motion_correction.setObjectName("actionManual_motion_correction")
        self.actionScript_Editor = QtWidgets.QAction(MainWindow)
        self.actionScript_Editor.setObjectName("actionScript_Editor")
        self.actionReload_list = QtWidgets.QAction(MainWindow)
        self.actionReload_list.setObjectName("actionReload_list")
        self.actionCNMF_E = QtWidgets.QAction(MainWindow)
        self.actionCNMF_E.setObjectName("actionCNMF_E")
        self.actionBatch_Manager = QtWidgets.QAction(MainWindow)
        self.actionBatch_Manager.setObjectName("actionBatch_Manager")
        self.actionDump_Work_Environment = QtWidgets.QAction(MainWindow)
        self.actionDump_Work_Environment.setObjectName("actionDump_Work_Environment")
        self.actionAdd_to_project = QtWidgets.QAction(MainWindow)
        self.actionAdd_to_project.setObjectName("actionAdd_to_project")
        self.actionResize = QtWidgets.QAction(MainWindow)
        self.actionResize.setObjectName("actionResize")
        self.actionCrop = QtWidgets.QAction(MainWindow)
        self.actionCrop.setObjectName("actionCrop")
        self.actionView_info = QtWidgets.QAction(MainWindow)
        self.actionView_info.setObjectName("actionView_info")
        self.actionChange_dtype = QtWidgets.QAction(MainWindow)
        self.actionChange_dtype.setObjectName("actionChange_dtype")
        self.actionReset_Scale = QtWidgets.QAction(MainWindow)
        self.actionReset_Scale.setObjectName("actionReset_Scale")
        self.actionMeta_data = QtWidgets.QAction(MainWindow)
        self.actionMeta_data.setObjectName("actionMeta_data")
        self.actionMeasure = QtWidgets.QAction(MainWindow)
        self.actionMeasure.setObjectName("actionMeasure")
        self.actionStimulus_Mapping = QtWidgets.QAction(MainWindow)
        self.actionStimulus_Mapping.setObjectName("actionStimulus_Mapping")
        self.actionConsole = QtWidgets.QAction(MainWindow)
        self.actionConsole.setCheckable(True)
        self.actionConsole.setObjectName("actionConsole")
        self.actionWork_Environment_Info = QtWidgets.QAction(MainWindow)
        self.actionWork_Environment_Info.setObjectName("actionWork_Environment_Info")
        self.actionMean = QtWidgets.QAction(MainWindow)
        self.actionMean.setObjectName("actionMean")
        self.actionMax = QtWidgets.QAction(MainWindow)
        self.actionMax.setObjectName("actionMax")
        self.actionStandard_Deviation = QtWidgets.QAction(MainWindow)
        self.actionStandard_Deviation.setObjectName("actionStandard_Deviation")
        self.actionClose_all_projection_windows = QtWidgets.QAction(MainWindow)
        self.actionClose_all_projection_windows.setObjectName("actionClose_all_projection_windows")
        self.actionOpen_docs = QtWidgets.QAction(MainWindow)
        self.actionOpen_docs.setObjectName("actionOpen_docs")
        self.actionSuite2p_Importer = QtWidgets.QAction(MainWindow)
        self.actionSuite2p_Importer.setObjectName("actionSuite2p_Importer")
        self.actionCNMF_3D = QtWidgets.QAction(MainWindow)
        self.actionCNMF_3D.setObjectName("actionCNMF_3D")
        self.actionCaimanImportHDF5 = QtWidgets.QAction(MainWindow)
        self.actionCaimanImportHDF5.setObjectName("actionCaimanImportHDF5")
        self.menuFile.addAction(self.actionAdd_to_project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_work_environment)
        self.menuFile.addAction(self.actionSave_work_environment)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionDump_Work_Environment)
        self.menuLoad_images.addAction(self.actionMesfile)
        self.menuLoad_images.addAction(self.actionTiff_file)
        self.menuCaImAn_toolbox.addAction(self.actionMotion_Correction)
        self.menuCaImAn_toolbox.addAction(self.actionCNMF)
        self.menuCaImAn_toolbox.addAction(self.actionCNMF_E)
        self.menuCaImAn_toolbox.addAction(self.actionCNMF_3D)
        self.menuCaImAn_toolbox.addAction(self.actionCaimanImportHDF5)
        self.menuModules.addAction(self.menuLoad_images.menuAction())
        self.menuModules.addAction(self.menuCaImAn_toolbox.menuAction())
        self.menuModules.addAction(self.actionROI_Manager)
        self.menuModules.addAction(self.actionSuite2p_Importer)
        self.menuModules.addAction(self.actionStimulus_Mapping)
        self.menuModules.addAction(self.actionManual_motion_correction)
        self.menuModules.addAction(self.actionScript_Editor)
        self.menuModules.addSeparator()
        self.menuModules.addAction(self.actionBatch_Manager)
        self.menuModules.addSeparator()
        self.menuEdit.addAction(self.actionMeta_data)
        self.menuProjections.addAction(self.actionMean)
        self.menuProjections.addAction(self.actionMax)
        self.menuProjections.addAction(self.actionStandard_Deviation)
        self.menuProjections.addSeparator()
        self.menuProjections.addAction(self.actionClose_all_projection_windows)
        self.menuImage.addAction(self.actionReset_Scale)
        self.menuImage.addAction(self.actionResize)
        self.menuImage.addAction(self.actionCrop)
        self.menuImage.addSeparator()
        self.menuImage.addAction(self.actionMeasure)
        self.menuImage.addSeparator()
        self.menuImage.addAction(self.actionChange_dtype)
        self.menuImage.addSeparator()
        self.menuImage.addAction(self.menuProjections.menuAction())
        self.menuView.addAction(self.actionWork_Environment_Info)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionConsole)
        self.menuHelp.addAction(self.actionOpen_docs)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuImage.menuAction())
        self.menubar.addAction(self.menuModules.menuAction())
        self.menubar.addAction(self.menuCustom_Modules.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.actionConsole.toggled['bool'].connect(self.dockConsole.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuModules.setTitle(_translate("MainWindow", "&Modules"))
        self.menuLoad_images.setTitle(_translate("MainWindow", "&Load images"))
        self.menuCaImAn_toolbox.setTitle(_translate("MainWindow", "&CaImAn toolbox"))
        self.menuEdit.setTitle(_translate("MainWindow", "&Edit"))
        self.menuCustom_Modules.setTitle(_translate("MainWindow", "&Plugins"))
        self.menuImage.setTitle(_translate("MainWindow", "&Image"))
        self.menuProjections.setTitle(_translate("MainWindow", "&Projections"))
        self.menuView.setTitle(_translate("MainWindow", "&View"))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help"))
        self.dockConsole.setWindowTitle(_translate("MainWindow", "&Console: viewer"))
        self.actionOpen_work_environment.setText(_translate("MainWindow", "&Open work environment"))
        self.actionSave_work_environment.setText(_translate("MainWindow", "&Save work environment"))
        self.actionMesfile.setText(_translate("MainWindow", "&Mesfile"))
        self.actionTiff_file.setText(_translate("MainWindow", "&Tiff file"))
        self.actionMotion_Correction.setText(_translate("MainWindow", "&Motion Correction"))
        self.actionCNMF.setText(_translate("MainWindow", "&CNMF"))
        self.actionROI_Manager.setText(_translate("MainWindow", "&ROI Manager"))
        self.actionROI_Manager.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.actionManual_motion_correction.setText(_translate("MainWindow", "&Manual motion correction"))
        self.actionScript_Editor.setText(_translate("MainWindow", "Script &Editor"))
        self.actionReload_list.setText(_translate("MainWindow", "&Reload list"))
        self.actionCNMF_E.setText(_translate("MainWindow", "CNMF-&E"))
        self.actionBatch_Manager.setText(_translate("MainWindow", "&Batch Manager"))
        self.actionDump_Work_Environment.setText(_translate("MainWindow", "&Clear Work Environment"))
        self.actionAdd_to_project.setText(_translate("MainWindow", "&Add to project"))
        self.actionResize.setText(_translate("MainWindow", "Re&size"))
        self.actionCrop.setText(_translate("MainWindow", "&Crop"))
        self.actionView_info.setText(_translate("MainWindow", "View info"))
        self.actionChange_dtype.setText(_translate("MainWindow", "Change &dtype"))
        self.actionReset_Scale.setText(_translate("MainWindow", "&Reset Scale"))
        self.actionMeta_data.setText(_translate("MainWindow", "&Meta data"))
        self.actionMeasure.setText(_translate("MainWindow", "&Measure"))
        self.actionStimulus_Mapping.setText(_translate("MainWindow", "&Stimulus Mapping"))
        self.actionConsole.setText(_translate("MainWindow", "&Console"))
        self.actionWork_Environment_Info.setText(_translate("MainWindow", "&Work Environment Editor"))
        self.actionMean.setText(_translate("MainWindow", "&Mean"))
        self.actionMax.setText(_translate("MainWindow", "Ma&x"))
        self.actionStandard_Deviation.setText(_translate("MainWindow", "&Standard Deviation"))
        self.actionClose_all_projection_windows.setText(_translate("MainWindow", "&Close all projection windows"))
        self.actionOpen_docs.setText(_translate("MainWindow", "&Open docs"))
        self.actionSuite2p_Importer.setText(_translate("MainWindow", "Suite&2p Importer"))
        self.actionCNMF_3D.setText(_translate("MainWindow", "CNMF &3D"))
        self.actionCaimanImportHDF5.setText(_translate("MainWindow", "&Import HDF5 result file"))

