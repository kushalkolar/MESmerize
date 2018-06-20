# -*- coding: utf-8 -*-
'''
Modified ImageView class from the original pyqtgraph ImageView class.
This provides all the UI functionality of the Mesmerize viewer.


ImageView.py -  Widget for basic image dispay and analysis
Copyright 2010  Luke Campagnola
Distributed under MIT/X11 license. See license.txt for more infomation.

Widget used for displaying 2D or 3D data. Features:
  - float or int (including 16-bit int) image display via ImageItem
  - zoom/pan via GraphicsView
  - black/white level controls
  - time slider for 3D data sets
  - ROI plotting
  - Image normalization through a variety of methods
'''

import os
from ..Qt import QtCore, QtGui, QtWidgets

# if USE_PYSIDE:
#     from .ImageViewTemplate_pyside import *
# else:
#     from .ImageViewTemplate_pyqt import *


from .ImageView_pytemplate import *
from ..graphicsItems.ImageItem import *
from ..graphicsItems.ROI import *
from ..graphicsItems.LinearRegionItem import *
from ..graphicsItems.InfiniteLine import *
from ..graphicsItems.ViewBox import *
from ..graphicsItems.GradientEditorItem import addGradientListToDocstring
from .. import ptime as ptime
from .. import debug as debug
from ..SignalProxy import SignalProxy
from .. import getConfigOption
from pyqtgraph import plot as pgplot
from multiprocessing import Process, Queue
import numpy as np
from MesmerizeCore import stimMapWidget
from viewer.core.viewer_work_environment import ViewerWorkEnv
from common import configuration
from MesmerizeCore import misc_widgets
import MesmerizeCore.Export
# from viewer.modules.batch_manager import ModuleGUI as BatchModuleGUI
import time
from functools import partial

try:
    from bottleneck import nanmin, nanmax
except ImportError:
    from numpy import nanmin, nanmax

if configuration.IS_WINDOWS:
    from MesmerizeCore.caimanMotionCorrect_threading import caimanPipeline
else:
    from MesmerizeCore.caimanMotionCorrect import caimanPipeline


class ImageView(QtWidgets.QWidget):
    """
    Widget used for display and analysis of image data.
    Implements many features:

    * Displays 2D and 3D image data. For 3D data, a z-axis
      slider is displayed allowing the user to select which frame is displayed.
    * Displays histogram of image data with movable region defining the dark/light levels
    * Editable gradient provides a color lookup table
    * Frame slider may also be moved using left/right arrow keys as well as pgup, pgdn, home, and end.
    * Basic analysis features including:

        * ROI and embedded plot for measuring image values across frames
        * Image normalization / background subtraction

    Basic Usage::

        imv = pg.ImageView()
        imv.show()
        imv.setImage(data)

    **Keyboard interaction**

    * left/right arrows step forward/backward 1 frame when pressed,
      seek at 20fps when held.
    * up/down arrows seek at 100fps
    * pgup/pgdn seek at 1000fps
    * home/end seek immediately to the first/last frame
    * space begins playing frames. If time values (in seconds) are given
      for each frame, then playback is in realtime.
    """
    sigTimeChanged = QtCore.Signal(object, object)
    sigProcessingChanged = QtCore.Signal(object)

    def __init__(self, parent=None, name="ImageView", view=None, imageItem=None, *args):
        """
        By default, this class creates an :class:`ImageItem <pyqtgraph.ImageItem>` to display image data
        and a :class:`ViewBox <pyqtgraph.ViewBox>` to contain the ImageItem.

        ============= =========================================================
        **Arguments**
        parent        (QWidget) Specifies the parent widget to which
                      this ImageView will belong. If None, then the ImageView
                      is created with no parent.
        name          (str) The name used to register both the internal ViewBox
                      and the PlotItem used to display ROI data. See the *name*
                      argument to :func:`ViewBox.__init__()
                      <pyqtgraph.ViewBox.__init__>`.
        view          (ViewBox or PlotItem) If specified, this will be used
                      as the display area that contains the displayed image.
                      Any :class:`ViewBox <pyqtgraph.ViewBox>`,
                      :class:`PlotItem <pyqtgraph.PlotItem>`, or other
                      compatible object is acceptable.
        imageItem     (ImageItem) If specified, this object will be used to
                      display the image. Must be an instance of ImageItem
                      or other compatible object.
        ============= =========================================================

        Note: to display axis ticks inside the ImageView, instantiate it
        with a PlotItem instance as its view::

            pg.ImageView(view=pg.PlotItem())
        """
        # Just setup the pyqtgraph stuff
        QtWidgets.QWidget.__init__(self, parent, *args)
        self.levelMax = 4096
        self.levelMin = 0
        self.name = name
        self.image = None
        self.axes = {}
        self.imageDisp = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.scene = self.ui.graphicsView.scene()
        # self.ui.btnResetScale.clicked.connect(self.resetImgScale)

        # Set the main viewer objects to None so that proceeding methods know that these objects
        # don't exist for certain cases.
        self.workEnv = ViewerWorkEnv()
        self.currBatch = None

        # Initialize list of bands that indicate stimulus times
        self.currStimMapBg = []
        self.stimMapWin = None

        self.ui.BtnSetROIDefs.clicked.connect(self.addROITag)

        self.ui.listwROIs.itemClicked.connect(self.setSelectedROI)
        self.ui.checkBoxShowAllROIs.clicked.connect(self.setSelectedROI)
        self.priorlistwROIsSelection = None

        self.ROIcolors=['m','r','y','g','c']

        # Connect many UI signals
        self.ui.btnTiffPage.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.btnSplitsPage.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.btnMesPage.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))

        # self.ui.btnMCPage.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(1))
        # self.ui.btnDenPage.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(2))
        # self.ui.btnBatchPage.clicked.connect(lambda: self.ui.stackedWidget_2.setCurrentIndex(0))

        self.ui.btnPlot.clicked.connect(self.plotAll)

        # self.ui.btnOpenMesFiles.clicked.connect(self.promptFileDialog)
        # self.ui.btnOpenTiff.clicked.connect(self.promTiffFileDialog)
        self.ui.btnImportSMap.clicked.connect(self.importCSVMap)

        # self.ui.btnSplitSeq.clicked.connect(self.enterSplitSeqMode)
        self.ui.btnPlotSplits.clicked.connect(lambda: self.splits_hstack(plot=True))
        self.splitSeqMode = False
        # self.ui.btnDoneSplitSeqs.clicked.connect(self.splits_seq_mode_done)

        self.ui.btnEditMetaData.clicked.connect(self.edit_meta_data)
        self.ui.btnExportWorkEnv.clicked.connect(self.init_export_gui)

        self.mesfileMap = None
        self.ui.listwMesfile.itemDoubleClicked.connect(lambda selection:
                                                        self.updateWorkEnv(selection, origin='mesfile'))
        # self.ui.listwTiffs.itemDoubleClicked.connect(lambda selection:
        #                                                 self.updateWorkEnv(selection, origin='tiff'))
        self.ui.listwSplits.itemDoubleClicked.connect(lambda selection:
                                                        self.updateWorkEnv(selection, origin='splits'))
        # self.ui.listwMotCor.itemDoubleClicked.connect(lambda selection:
        #                                               self.updateWorkEnv(selection, origin='MotCor'))

        # self.ui.btnCrop.clicked.connect(self.crop_img_seq)

        self.ui.btnAddROI.clicked.connect(self.addROI)
        self.ui.btnAddROI.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.btnAddROI.customContextMenuRequested.connect(self.addROI_options)
        # self.ui.listwBatch.itemSelectionChanged.connect(self.setSelectedROI)

        # self.ui.btnSetID.clicked.connect(self.setSampleID)
        # self.ui.btnMeasureDistance.clicked.connect(self.drawMeasureLine)
        # self.measureLine = None
        # self.measureLine_A = None
        # self.ui.btnStartBatch.clicked.connect(self.startBatch)
        # self.ui.btnRemoveFromBatch.clicked.connect(self.removeFromBatch)
        #
        # self.ui.btnMotCorSearchDir.clicked.connect(self.searchMotCorFiles)

        self.ui.comboBoxStimMaps.setDisabled(True)
        self.ui.comboBoxStimMaps.currentIndexChanged[str].connect(self.displayStimMap)

        self.ui.stackedWidget.setCurrentIndex(0)

        #self.ui.resetscaleBtn.clicked.connect(self.autoRange())

        self.ignoreTimeLine = False

        if view is None:
            self.view = ViewBox()
        else:
            self.view = view
        self.ui.graphicsView.setCentralItem(self.view)
        self.view.setAspectLocked(True)
        self.view.invertY()

        if imageItem is None:
            self.imageItem = ImageItem()
        else:
            self.imageItem = imageItem
        self.view.addItem(self.imageItem)
        self.currentIndex = 0

        self.ui.histogram.setImageItem(self.imageItem)

        self.menu = None

        self.ui.roiPlot.registerPlot(self.name + '_ROI')  # I don't know what this does, It was included with the original ImageView class
        self.view.register(self.name)

        self.noRepeatKeys = [QtCore.Qt.Key_Right, QtCore.Qt.Key_Left, QtCore.Qt.Key_Up,
                             QtCore.Qt.Key_Down, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown]

        self.watcherStarted = False

        # This is the splitter separating the ImageView and ROI Plot
        self.ui.splitter.setEnabled(False)

        # Set starting sizes of the other splitters
        self.ui.splitterHighest.setSizes([700, 160])
        self.ui.splitterFilesImage.setSizes([200, 500])

        # List for holding the linear regions that are used to illustrate the stimulus timings on the background
        # of the timeline in the ROI plot
        self.currStimMapBg = []

        self.initROIPlot()
        self.enableUI(False)

        self.update_from_config()

        # For illustrating the quilt on the image to assist with setting motion correction parameters
        # self.ui.sliderOverlaps.valueChanged.connect(self.drawStrides)
        # self.ui.sliderStrides.valueChanged.connect(self.drawStrides)
        # self.overlapsV = []
        # self.overlapsH = []
        # self.ui.btnShowQuilt.clicked.connect(self.drawStrides)
        # self.ui.btnShowQuilt.clicked.connect(self.removeStrides)

    @property
    def status_bar_label(self):
        return self._status_bar_label

    @status_bar_label.setter
    def status_bar_label(self, status_bar_label: QtWidgets.QLabel):
        self._status_bar_label = status_bar_label

    # Called from __main__ when btnSave in ConfigWindow is clicked.
    def update_from_config(self):
        self.ui.listwROIDefs.clear()
        # self.ui.listwROIDefs.addItems([roi_def + ': ' for roi_def in configuration.cfg.options('ROI_DEFS')])
        self.setSelectedROI()

    #Initialize ROI Plot
    def initROIPlot(self):
        self.timeLine = InfiniteLine(0, movable=True, hoverPen=None)
        self.timeLine.setPen((255, 255, 0, 200))
        self.timeLine.setZValue(100)
        self.timeLineBorder = InfiniteLine(0, movable=False, hoverPen=None)
        self.timeLineBorder.setPen(color=(0,0,0,115), width=7)
        self.timeLineBorder.setZValue(99)

        self.ui.roiPlot.addItem(self.timeLineBorder)
        self.ui.roiPlot.addItem(self.timeLine)
        self.ui.splitter.setSizes([self.height()-35, 35])
        self.ui.roiPlot.hideAxis('left')

        self.keysPressed = {}
        self.playTimer = QtCore.QTimer()
        self.playRate = 0
        self.lastPlayTime = 0
        self.playTimer.timeout.connect(self.timeout)


        ## wrap functions from view box
        for fn in ['addItem', 'removeItem']:
            setattr(self, fn, getattr(self.view, fn))

        ## wrap functions from histogram
        for fn in ['setHistogramRange', 'autoHistogramRange', 'getLookupTable', 'getLevels']:
            setattr(self, fn, getattr(self.ui.histogram, fn))

        self.timeLine.sigPositionChanged.connect(self.timeLineChanged)

    '''##############################################################################################################
                                Work Environment Creation & open file dialogs
       ##############################################################################################################'''

    def updateWorkEnv(self, selection, origin, iterate=False, qtsig=True):
        ''' ======================================================================================
            Set the ImgData object and pass the .seq of the ImgData object to setImage().
            :param selection:   Item object that is send from the Qt listwidget's signal

            :param origin:      Type of origin to determine the classmethod decorator that should be used to create an
                                instance of workEnv

            :param iterate:     Disable GUI popups, for performing iterations over many workEnv instances created in
                                succession. For example useful for stitching ROI plots of all splits in splitseq mode

            :param qtsig:       When false, it will interpret the selection as not coming from a Qt signal.

            :return:            None
            =======================================================================================
        '''
        # Prevent losing unsaved workEnv
        if origin == 'splits':
            clear_sample_id = False
        else:
            clear_sample_id = True
        if not self.workEnv.isEmpty and self.DiscardWorkEnv(clear_sample_id) is False:
            return

        # if mesfile listwidget item is clicked
        # if origin == 'mesfile':
        #     try:
        #         self.workEnv = viewerWorkEnv.from_mesfile(self.mesfile, selection.text().split('//')[0])
        #     except Exception as e:
        #         QtGui.QMessageBox.information(self, 'Error', 'Error opening the selected '+\
        #                                       'image in the currently open mes file.\n' + str(e), QtGui.QMessageBox.Ok)
        #         return
        #     if self.mesfileMap is not None:
        #         self.workEnv.imgdata.stimMaps = (self.mesfileMap, 'mesfile')
        #
        # # if motion correction listwidget item is clicked
        # elif origin == 'MotCor':
        #     print(selection.text())
        #     self.workEnv = viewerWorkEnv.from_pickle(selection.text()[:-7]+'.pik', selection.text())
        #     self.workEnv.imgdata.isMotCor = True
        #     if self.workEnv.imgdata.stimMaps is not None:
        #         self.populateStimMapComboBox()
        #         self.displayStimMap()
        #     self.ui.tabWidget.setCurrentWidget(self.ui.tabROIs)

        # # For loading from tiff files
        # elif origin == 'tiff':
        #     if iterate is False:
        #         self.workEnv = viewerWorkEnv.from_tiff(selection.text())
        #         if QtGui.QMessageBox.question(self, 'Open Stimulus Maps?',
        #                                    'Would you like to open stimulus maps for this file?',
        #                                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
        #             self.importCSVMap()
        #     else:
        #         # Just here if someone wants to process many tiff files in the same way they can iterate over them
        #         # without having the QMessageBox show up every time.
        #         self.workEnv = viewerWorkEnv.from_tiff(selection)

        # For loading splits of a sequence in splitseq mode
        elif origin == 'splits':
            # TODO: THERE HAS TO BE A BETTER WAY TO DO THIS!! CHECK IF TYPE IS QTSIGNAL OR SOMETHING, & IF SO INTERPRET
            # TODO: IT AS PLAIN STRING?? <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            if qtsig == False:
                self.workEnv = ViewerWorkEnv.from_pickle(pikPath=self.splitsDir + '/' + selection + '.pik', tiffPath=self.splitsDir + '/' + selection + '.tiff')
            else:
                self.workEnv = ViewerWorkEnv.from_pickle(pikPath=self.splitsDir + '/' + selection.text() + '.pik', tiffPath=self.splitsDir + '/' + selection.text() + '.tiff')

        elif origin == 'pandas':
            self.workEnv = ViewerWorkEnv.from_pickle(pikPath=selection[0], tiffPath=selection[1])

        # Set the image
        self.setImage(self.workEnv.imgdata.seq.T, pos=(0,0), scale=(1,1),
                      xvals=np.linspace(1, self.workEnv.imgdata.seq.T.shape[0],
                                        self.workEnv.imgdata.seq.T.shape[0]))

        # If the newly spawned workEnv has any ROI states saved, then load them all.
        # Use for example in splitseq mode
        for ID in range(0, len(self.workEnv.roi_states)):
            self.addROI(load=self.workEnv.roi_states[ID])
            # self.view.addItem(self.workEnv.ROIList[-1])
            # self.updatePlot(ID, force=True)

        # Get image dimensions to set limits on the sliders for motion correction parameters
        x = self.workEnv.imgdata.seq.shape[0]
        # y = self.workEnv.imgdata.seq.shape[1]
        # self.ui.sliderStrides.setMaximum(int(max(x, y)/2))
        # self.ui.sliderOverlaps.setMaximum(int(max(x, y)/2))

        # Activate the stimulus illustration GUI stuff if the newly spawed work environment has a stimulus map.
        if self.workEnv.imgdata.stimMaps is not None:
            self.populateStimMapComboBox()
            self.displayStimMap()

        self.workEnv.saved = True
        # self._workEnv_checkSaved() # Connect signals of many Qt UI elements to a method that sets workEnv.save = False
        if origin == 'splits':
            self.enableUI(True, clear_sample_id=False)
        else:
            self.enableUI(True)

    def enableUI(self, b, clear_sample_id=True):
        self.ui.splitter.setEnabled(b)  # Enable stuff in the image & curve working area
        # self.ui.tabBatchParams.setEnabled(b)
        self.ui.tabROIs.setEnabled(b)
        self.ui.toolBox.setEnabled(b)
        self.ui.btnAddCurrEnvToProj.setEnabled(b)


        # if clear_sample_id:
            # self.ui.lineEdAnimalID.clear()
            # self.ui.lineEdTrialID.clear()
            # self.ui.lineEdGenotype.clear()
    #
    # def resetImgScale(self):
    #     '''
    #     Reset the current image to the center of the scene and reset the scale
    #     doesn't work as intended in some weird circumstances when you repeatedly right click on the scene
    #     and set the x & y axis to 'Auto' a bunch of times. But this bug is hard to recreate.'''
    #     self.setImage(self.workEnv.imgdata.seq.T, pos=(0,0), scale=(1,1),
    #                       xvals=np.linspace(1, self.workEnv.imgdata.seq.T.shape[0],
    #                                         self.workEnv.imgdata.seq.T.shape[0]))

    # def promptFileDialog(self):
    #     if self.workEnv is not None and self.DiscardWorkEnv() is False:  # If workEnv is not saved, warn the user.
    #         return
    #     self.ui.listwMesfile.clear()
    #     # self.ui.listwSplits.clear()
    #     # self.ui.listwTiffs.clear()
    #     filelist = QtGui.QFileDialog.getOpenFileNames(self, 'Choose ONE mes file',
    #                                                   '.', '(*.mes)')
    #     if len(filelist) == 0:
    #         return
    #     try:
    #         # Creates an instance of MES, see MesmerizeCore.FileInput
    #         self.mesfile = viewerWorkEnv.load_mesfile(filelist[0][0])
    #         self.ui.listwMesfile.setEnabled(True)
    #
    #         # Get the references of the images, their descriptions, and add them to the list
    #         for i in self.mesfile.images:
    #             j = self.mesfile.image_descriptions[i]
    #             self.ui.listwMesfile.addItem(i+'//'+j)
    #
    #         # If Auxiliary voltage info is found in the mes file, ask the user if they want to map these to stimuli
    #         if len(self.mesfile.voltDict) > 0:
    #             self.initMesStimMapGUI()
    #             self.ui.btnChangeSMap.setEnabled(True)
    #             if QtGui.QMessageBox.question(self, '', 'This .mes file contains auxilliary output voltage ' + \
    #                           'information, would you like to apply a Stimulus Map now?',
    #                            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
    #
    #                 self.ui.btnResetSMap.setEnabled(True)
    #                 self.stimMapWin.show()
    #         else:
    #             self.ui.btnResetSMap.setDisabled(True)
    #             self.ui.btnChangeSMap.setDisabled(True)
    #
    #     except (IOError, IndexError) as e:
    #        QtGui.QMessageBox.warning(self,'IOError or IndexError', "There is an problem with the files you've selected:\n" + str(e), QtGui.QMessageBox.Ok)
    #     return
    #
    # # def promTiffFileDialog(self):
    # #     if self.workEnv is not None and self.DiscardWorkEnv() is False:
    # #         return
    # #     self.ui.listwMesfile.clear()
    # #     # self.ui.listwSplits.clear()
    # #     # self.ui.listwTiffs.clear()
    # #     filelist = QtGui.QFileDialog.getOpenFileNames(self, 'Choose file(s)',
    # #                                                   '.', '(*.tif *tiff)')
    # #     if len(filelist[0]) == 0:
    # #         return
    # #
    # #     files = filelist[0]
    # #
    # #     self.ui.listwTiffs.addItems(files)
    # #     self.ui.listwTiffs.setEnabled(True)

    def edit_meta_data(self):
        if hasattr(self, '_meta_data_editor'):
            self._meta_data_editor.close()
            self._meta_data_editor = None

        self._meta_data_editor = misc_widgets.MetaDataEditor(self)
        self._meta_data_editor.fill_widget(self.workEnv.imgdata.meta)
        self._meta_data_editor.btnSave.clicked.connect(self.set_meta_data)

    def set_meta_data(self):
        try:
            d = self._meta_data_editor.get_data()
            self.workEnv.imgdata.meta.update(d)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Error', 'The following error occured while trying to save the meta-data:\n'
                                                     + str(e))
        self._meta_data_editor.close()

    def init_export_gui(self):
        if hasattr(self, 'export_gui'):
            self.export_gui.close()
            self.export_gui = None
        self.export_gui = misc_widgets.Exporter()
        self.export_gui.btnExport.clicked.connect(self.export_workEnv)

    def export_workEnv(self):
        path = self.export_gui.lineEdPath.text()

        if self.export_gui.comboBoxFormat.currentText() != 'tiff':
            if self.export_gui.radioAuto.isChecked():
                mi = self.workEnv.imgdata.meta['vmin']
                mx = self.workEnv.imgdata.meta['vmax']
                histLevels = (mi, mx)
            elif self.export_gui.radioFromViewer.isChecked():
                histLevels = self.ui.histogram.item.getLevels()

        if self.export_gui.comboBoxFormat.currentText() == 'tiff':
            try:
                MesmerizeCore.Export.Exporter(self.workEnv.imgdata, path + '.tiff')
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Export Error', 'The following error occured while exporting the work '
                                                                'environment: \n' + str(e))
            return

        if self.export_gui.labelSlider != '1.0':
            fscale = float(self.export_gui.labelSlider.text())
            f = self.workEnv.imgdata.meta['fps'] * fscale
        else:
            f = self.workEnv.imgdata.meta['fps']

        if self.export_gui.comboBoxFormat.currentText() == 'MJPG':
            ex = '.avi'
        elif self.export_gui.comboBoxFormat.currentText() == 'X264':
            ex = '.mp4'
        elif self.export_gui.comboBoxFormat.currentText() == 'gif':
            ex = '.gif'

        try:
            MesmerizeCore.Export.Exporter(self.workEnv.imgdata, path + ex, levels=histLevels, fps=f)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Export Error', 'The following error occured while exporting the work '
                                                            'environment: \n' + str(e))

    '''##################################################################################################################
                                            Split Seq Mode methods
    ##################################################################################################################'''

    def split_seq_ui_toggle(self, b):
        # Disable a lot of buttons for functions that shouldn't be used in splitseq mode
        self.ui.btnAddROI.setDisabled(b)
        # self.ui.btnCrop.setDisabled(b)
        self.ui.btnChangeSMap.setDisabled(b)
        self.ui.btnResetSMap.setDisabled(b)
        self.ui.btnImportSMap.setDisabled(b)

        self.ui.listwSplits.setEnabled(b)
        self.ui.btnPlotSplits.setEnabled(b)
        self.ui.btnDoneSplitSeqs.setEnabled(b)

    def enterSplitSeqMode(self):
        if self.splitSeqMode is False:
            if QtWidgets.QMessageBox.question(self, 'Enter Split Seq Mode?', 'Are you sure you want to enter split-seq mode? ' +\
                                      'You CANNOT add any more ROIs in split-seq mode and many other functins are '
                                      ' disabled.\n\nAlso make sure you have tagged ALL your ROIs and applied any stimulus'
                                      ' maps you may be interested in. You will loose everything if you tag ROIs after '
                                      'exiting split-seq mode', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)\
                                        == QtWidgets.QMessageBox.No:
                return
            self.splitSeqMode = True
            # Create temp dir to hold the splits
            self.splitsDir = configuration.projPath + '/tmp/splits/' + str(time.time())
            os.makedirs(self.splitsDir)

            self.split_seq_ui_toggle(True)

            # Each split is portrayed as an index item on the ui.listwSplits Qt widget
            currentSplit = 0
            self.ui.listwSplits.addItems([str(currentSplit).zfill(3)])
            self.ui.listwSplits.setCurrentRow(0)
            self.ui.stackedWidget.setCurrentIndex(2)

        # Cannot split at zero because there is nothing before the 0th index of an image seq
        if self.currentIndex == 0:
            QtWidgets.QMessageBox.warning(self, 'Index = 0!', 'You cannot slice at the 0th index! '+\
                                      'What\'s the point in that?!', QtWidgets.QMessageBox.Ok)
            return

        # Store the next sequence to spawn the next workEnv
        nextseq = self.workEnv.imgdata.seq[:, :, self.currentIndex:]
        print(self.workEnv.imgdata.seq.shape)
        # Set current workEnv.seq up to the current index in the image sequence
        self.workEnv.imgdata.seq = self.workEnv.imgdata.seq[:, :, :self.currentIndex]
        print(self.workEnv.imgdata.seq.shape)

        # Set index of this current split of the current WorkEnv.seq to the index of the listwidget
        currentSplit = int(self.ui.listwSplits.currentItem().text())

        print('currentSplit is: ' + str(currentSplit))

        self.splitSeq(currentSplit)  # Save this split by basically using workEnv.to_pickle

        # Spawn new workEnv from the just saved sequence which is the rest of the image sequence after the
        # previous once was cut-off
        self.workEnv.imgdata.seq = nextseq

        # Get the number of splits that have currently been done
        num_splits = int(self.ui.listwSplits.count())
        print('Number of splits is: ' + str(num_splits))

        # See if the split we had just saved to disk was a "middle split"
        # I.e. if it was a split of a sequence that itself was already a split.
        # In other terms, if it was not a terminal split, or basically it that split
        # was not from the end of the image.
        if int(self.ui.listwSplits.count()) > int(currentSplit) + 1:
            print('middle split!!')
            # If it was a middle split, rename all splits after that one so that we make space to not
            # overwrite the new split, i.e. nextseq
            for fname in reversed(range(currentSplit + 2, num_splits + 1)):
                dst = self.splitsDir + '/' + str(fname).zfill(3)
                src = self.splitsDir + '/' + str(fname - 1).zfill(3)
                print('Renamed: ' + src + ' to :' + dst)
                os.rename(src + '.pik', dst + '.pik')
                os.rename(src + '.tiff', dst + '.tiff')

        # Add references for all the splits to the list widget
        l = list(range(num_splits + 1))
        print('new list items are: ' + str(l))
        self.ui.listwSplits.clear()
        self.ui.listwSplits.addItems([str(i).zfill(3) for i in l])

        # Save nextseq to disk
        self.splitSeq(currentSplit + 1)
        self.ui.listwSplits.setCurrentRow(currentSplit + 1)

    def splitSeq(self, splitNum):
        self.resetImgScale()  # New splits are a spawned instance of workEnv. Calling resetImgScale() will set the image
                              # in the imageview so that plots can updated from the ROIs.
        for ID in range(0, len(self.workEnv.ROIList)):
            self.updatePlot(ID, force=True)  # Force update of the plot to get intensity values for each ROI.
        fn = str(splitNum).zfill(3)
        print('Saving to disk! ' + fn)
        self.workEnv.to_pickle(self.splitsDir, filename=fn)  # Save the split

    # Just a function that ultimately stiches together ROI plotting under all the splits
    def splits_hstack(self, plot=False):
        self.masterCurvesList = []
        self.masterROIList = []

        for i in range(0, self.ui.listwSplits.count()):
            self.workEnv.saved = True
            self.updateWorkEnv(str(i).zfill(3), origin='splits', iterate=True, qtsig=False)

            for ID in range(0, len(self.workEnv.ROIList)):
                self.updatePlot(ID, force=True)
                self.masterROIList.append([self.workEnv.ROIList])

            for ID in range(0, len(self.workEnv.CurvesList)):
                if i == 0:
                    self.masterCurvesList.append(self.workEnv.CurvesList[ID].getData())
                else:
                    self.masterCurvesList[ID] = np.hstack((self.masterCurvesList[ID],
                                                           self.workEnv.CurvesList[ID].getData()))
        if plot:
            for curve in self.masterCurvesList:
                pgplot(curve[1])

    def splits_seq_mode_done(self):
        if QtWidgets.QMessageBox.question(self, 'Warning!', "Are you sure you're done?",
                                          QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return

        self.splits_hstack()
        self.workEnv.CurvesList = self.masterCurvesList
        # self.workEnv.ROIList = self.masterROIList
        self.exit_split_seq_mode()

    def exit_split_seq_mode(self):
        self.ui.listwSplits.clear()
        self.split_seq_ui_toggle(False)

    '''##################################################################################################################
                                            Stimulus Maps methods
    ##################################################################################################################'''

    # Just a simple method to load stimulus maps from a CSV file.
    def importCSVMap(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, 'Choose map file(s)',
                                                   '.', '(*.csv)')
        if len(paths[0]) == 0:
            return

        csvfiles = paths[0]

        new_channels = []
        for file in csvfiles:
            if file.split('/')[-1].split('.csv')[0] not in configuration.proj_cfg.options('STIM_DEFS'):
                new_channels.append(file.split('/')[-1].split('.csv')[0])

        if len(new_channels) > 0:
            QtWidgets.QMessageBox.warning(self, 'Stimulus Definition not in project!', 'The following stimulus ' + \
                  ' definitions were not found in your project configuration.\n' + \
                  '\n'.join(new_channels) + '\nYou must add these' + \
                  ' stimulus definitions to your project configuration before you can proceed.\nOn the Menubar go to ' + \
                  '"Edit" -> "Project Configuration" and add this new stimulus, click Save in the config window, and ' + \
                  'then click "Set ALL Maps" again in this window', QtWidgets.QMessageBox.Ok)
            return

        self.workEnv.imgdata.stimMaps = (csvfiles, 'csv')
        if self.workEnv.imgdata.stimMaps is not None:
            self.populateStimMapComboBox()
            self.displayStimMap()

    # Just the StimMap GUI stuff
    def initMesStimMapGUI(self):
        if self.stimMapWin is not None:
            self.stimMapWin.close()
            self.stimMapWin = None
        # Initialize stimMapWidget module in the background
        self.stimMapWin = stimMapWidget.Window(self.mesfile.voltDict)
        self.stimMapWin.resize(520, 120)
        for i in range(0, self.stimMapWin.tabs.count()):
            self.stimMapWin.tabs.widget(i).ui.setMapBtn.clicked.connect(self.storeMesStimMap)
            self.stimMapWin.tabs.widget(i).ui.btnRefresh.clicked.connect(self.initMesStimMapGUI)
        # If user wants to change the map for this particular ImgData object
        self.ui.btnChangeSMap.clicked.connect(self.stimMapWin.show)
        # If user wants to set the map back to the one for the entire mes file
        self.ui.btnResetSMap.clicked.connect(self.resetStimMap)

    # Reset stimulus maps to the one set for the entire mesfile, if the user has set a map for the entire mesfile.
    def resetStimMap(self):
        self.workEnv.imgdata.stimMaps = (self.mesfileMap, 'mesfile')
        self.displayStimMap()

    # Set stimulus maps that were set via the stimMapWidget GUI for a mesfile obj/image
    # Basically sends a dict to the ImgData class' stimMaps property decorator's setter. See MesmerizeCore.DataTypes
    def storeMesStimMap(self):
        empty_channels = []
        new_channels = []

        for i in range(0, self.stimMapWin.tabs.count()):
            # Check if the user has left some chanels blank
            if self.stimMapWin.tabs.widget(i).ui.lineEdChannelName.text() == '':
                empty_channels.append(self.stimMapWin.tabs.widget(i).ui.titleLabelChannel.objectName())
            # Check if the user has entered any stimulus definitions that aren't a part of the project.
            elif self.stimMapWin.tabs.widget(i).ui.lineEdChannelName.text() not in configuration.proj_cfg.options('STIM_DEFS'):
                new_channels.append(self.stimMapWin.tabs.widget(i).ui.lineEdChannelName.text())

        if len(empty_channels) > 0:
            empty_channels = '\n'.join(empty_channels)
            if QtWidgets.QMessageBox.No == QtWidgets.QMessageBox.warning(self, 'Undefined channels!',
                                      'You have not entered a name for the following channels:\n' +
                                      empty_channels + '\nWould you like to discard these channels' +\
                                      ' and continue?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No):
                return
            else:
                self.stimMapWin.activateWindow()
        if len(new_channels) > 0:
            QtWidgets.QMessageBox.warning(self, 'Stimulus Definition not in project!', 'The following stimulus ' +\
                ' definitions were not found in your project configuration.\n' +\
                '\n'.join(new_channels) + '\nYou must add these' +\
                ' stimulus definitions to your project configuration before you can proceed.\nOn the Menubar go to ' +\
                '"Edit" -> "Project Configuration" and add this new stimulus, click Save in the config window, and ' +\
                'then click "Set ALL Maps" again in this window', QtWidgets.QMessageBox.Ok)
            self.stimMapWin.activateWindow()
            return

        self.stimMapWin.hide()

        dmaps = self.stimMapWin.getAllStimMaps()  # Get the stim maps as a dict from the GUI

        # Ask the user if they want to apply these stimulus maps for the whole mesfile
        if self.workEnv is not None:
            if QtWidgets.QMessageBox.question(self, 'Apply for whole mes file?', 'Would you like to load these maps ' +\
                        'for the entire mes file?', QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                self.mesfileMap = dmaps

            self.workEnv.imgdata.stimMaps = (dmaps, 'mesfile')  # Set stimMap via the property decorator
            self.populateStimMapComboBox()
            return
        self.mesfileMap = dmaps

    # Add stimulus choices that already exist in the project to the comboboxes in the stimMapWidget GUI
    def populateStimMapComboBox(self):
        self.ui.comboBoxStimMaps.clear()
        self.ui.comboBoxStimMaps.addItems(list(self.workEnv.imgdata.stimMaps.keys()))
        self.ui.comboBoxStimMaps.setCurrentIndex(0)
        self.ui.comboBoxStimMaps.setEnabled(True)

    # Create and show the linear regions to illustrate stimulus timings
    def displayStimMap(self, map_name=None):
        """
        :param map_name: Name of the stimulus map (dict key of ImgData.stimMaps property) to illustrate.
                         Passed by the comboBox Qt signal.
        """
        print(map_name)
        if self.workEnv is None:
            return
        if map_name == -1:
            return
        if map_name is None:
            map_name = self.ui.comboBoxStimMaps.currentText()
        if map_name == '':
            return

        stims = self.workEnv.imgdata.stimMaps[map_name]

        # Remove any stimulus illustrations that're already displayed on the plot
        if len(self.currStimMapBg) > 0:
            for item in self.currStimMapBg:
                self.ui.roiPlot.removeItem(item)

            self.currStimMapBg = []

        # Draw the linear regions according to the stimulus timings
        for stim in stims:
            definitions = stim[0][0]
            color = stim[0][-1]

            frameStart = stim[-1][0]
            frameEnd = stim[-1][1]

            linReg = LinearRegionItem(values=[frameStart, frameEnd],
                            brush=color, movable=False, bounds=[frameStart, frameEnd])
            linReg.setZValue(0)  # Set it so that all other plot items (the curve/traces and the timeline are above the illustration)
            linReg.lines[0].setPen(color)
            linReg.lines[1].setPen(color)

            self.currStimMapBg.append(linReg)

        for linReg in self.currStimMapBg:
            self.ui.roiPlot.addItem(linReg)

    '''#################################################################################################################
                                    Mildly altered pyqtgraph methods
    #################################################################################################################'''

    def setImage(self, img, autoRange=True, autoLevels=True, levels=None, axes=None, xvals=None, pos=None, scale=None, transform=None, autoHistogramRange=True):
        """
        Set the image to be displayed in the widget.

        ================== ===========================================================================
        **Arguments:**
        img                (numpy array) the image to be displayed. See :func:`ImageItem.setImage` and
                           *notes* below.
        xvals              (numpy array) 1D array of z-axis values corresponding to the third axis
                           in a 3D image. For video, this array should contain the time of each frame.
        autoRange          (bool) whether to scale/pan the view to fit the image.
        autoLevels         (bool) whether to update the white/black levels to fit the image.
        levels             (min, max); the white and black level values to use.
        axes               Dictionary indicating the interpretation for each axis.
                           This is only needed to override the default guess. Format is::

                               {'t':0, 'x':1, 'y':2, 'c':3};

        pos                Change the position of the displayed image
        scale              Change the scale of the displayed image
        transform          Set the transform of the displayed image. This option overrides *pos*
                           and *scale*.
        autoHistogramRange If True, the histogram y-range is automatically scaled to fit the
                           image data.
        ================== ===========================================================================

        **Notes:**

        For backward compatibility, image data is assumed to be in column-major order (column, row).
        However, most image data is stored in row-major order (row, column) and will need to be
        transposed before calling setImage()::

            imageview.setImage(imagedata.T)

        This requirement can be changed by the ``imageAxisOrder``
        :ref:`global configuration option <apiref_config>`.

        """

        profiler = debug.Profiler()

        if hasattr(img, 'implements') and img.implements('MetaArray'):
            img = img.asarray()

        if not isinstance(img, np.ndarray):
            required = ['dtype', 'max', 'min', 'ndim', 'shape', 'size']
            if not all([hasattr(img, attr) for attr in required]):
                raise TypeError("Image must be NumPy array or any object "
                                "that provides compatible attributes/methods:\n"
                                "  %s" % str(required))

        self.image = img
        self.imageDisp = None

        profiler()

        if axes is None:
            x,y = (0, 1) if self.imageItem.axisOrder == 'col-major' else (1, 0)

            if img.ndim == 2:
                self.axes = {'t': None, 'x': x, 'y': y, 'c': None}
            elif img.ndim == 3:
                # Ambiguous case; make a guess
                if img.shape[2] <= 4:
                    self.axes = {'t': None, 'x': x, 'y': y, 'c': 2}
                else:
                    self.axes = {'t': 0, 'x': x+1, 'y': y+1, 'c': None}
            elif img.ndim == 4:
                # Even more ambiguous; just assume the default
                self.axes = {'t': 0, 'x': x+1, 'y': y+1, 'c': 3}
            else:
                raise Exception("Can not interpret image with dimensions %s" % (str(img.shape)))
            max_sval = max(x, y)
        elif isinstance(axes, dict):
            self.axes = axes.copy()
        elif isinstance(axes, list) or isinstance(axes, tuple):
            self.axes = {}
            for i in range(len(axes)):
                self.axes[axes[i]] = i
        else:
            raise Exception("Can not interpret axis specification %s. Must be like {'t': 2, 'x': 0, 'y': 1} or ('t', 'x', 'y', 'c')" % (str(axes)))



        for x in ['t', 'x', 'y', 'c']:
            self.axes[x] = self.axes.get(x, None)
        axes = self.axes

        if xvals is not None:
            self.tVals = xvals
        elif axes['t'] is not None:
            if hasattr(img, 'xvals'):
                try:
                    self.tVals = img.xvals(axes['t'])
                except:
                    self.tVals = np.arange(img.shape[axes['t']])
            else:
                self.tVals = np.arange(img.shape[axes['t']])

        profiler()

        self.currentIndex = 0
        self.updateImage(autoHistogramRange=autoHistogramRange)
        if levels is None and autoLevels:
            self.autoLevels()
        if levels is not None:  ## this does nothing since getProcessedImage sets these values again.
            self.setLevels(*levels)

        profiler()

        if self.axes['t'] is not None:
            #self.ui.roiPlot.show()
            self.ui.roiPlot.setXRange(self.tVals.min(), self.tVals.max())
            self.timeLine.setValue(0)
            #self.ui.roiPlot.setMouseEnabled(False, False)
            if len(self.tVals) > 1:
                start = self.tVals.min()
                stop = self.tVals.max() + abs(self.tVals[-1] - self.tVals[0]) * 0.02
            elif len(self.tVals) == 1:
                start = self.tVals[0] - 0.5
                stop = self.tVals[0] + 0.5
            else:
                start = 0
                stop = 1
#            for s in [self.timeLine, self.normRgn]:
#                s.setBounds([start, stop])
        profiler()

        self.imageItem.resetTransform()
        if scale is not None:
            self.imageItem.scale(*scale)
        if pos is not None:
            self.imageItem.setPos(*pos)
        if transform is not None:
            self.imageItem.setTransform(transform)

        profiler()

        if autoRange:
            self.autoRange()

        profiler()

        self.ui.roiPlot.showAxis('left')
        mn = self.tVals.min()
        mx = self.tVals.max()
        self.ui.roiPlot.setXRange(mn, mx, padding=0.01)
        self.timeLine.show()
        self.timeLine.setBounds([mn, mx])

    def clear(self):
        self.image = None
        self.imageItem.clear()

    def play(self, rate):
        """Begin automatically stepping frames forward at the given rate (in fps).
        This can also be accessed by pressing the spacebar."""
        #print "play:", rate
        self.playRate = rate
        if rate == 0:
            self.playTimer.stop()
            return

        self.lastPlayTime = ptime.time()
        if not self.playTimer.isActive():
            self.playTimer.start(16)

    def autoLevels(self):
        """Set the min/max intensity levels automatically to match the image data."""
        self.setLevels(self.levelMin, self.levelMax)

    def setLevels(self, min, max):
        """Set the min/max (bright and dark) levels."""
        self.ui.histogram.setLevels(min, max)

    def autoRange(self):
        """Auto scale and pan the view around the image such that the image fills the view."""
        image = self.getProcessedImage()
        self.view.autoRange()

    def getProcessedImage(self):
        """Returns the image data after it has been processed by any normalization options in use.
        This method also sets the attributes self.levelMin and self.levelMax
        to indicate the range of data in the image."""
        if self.imageDisp is None:
            self.imageDisp = self.image
            self.levelMin, self.levelMax = list(map(float, self.quickMinMax(self.imageDisp)))

        return self.imageDisp

    def close(self):
        """Closes the widget nicely, making sure to clear the graphics scene and release memory."""
        self.ui.roiPlot.close()
        self.ui.graphicsView.close()
        self.scene.clear()
        del self.image
        del self.imageDisp
        super(ImageView, self).close()
        self.setParent(None)

    def keyPressEvent(self, ev):
        #print ev.key()
        if ev.key() == QtCore.Qt.Key_Space:
            if self.playRate == 0:
                fps = (self.getProcessedImage().shape[0]-1) / (self.tVals[-1] - self.tVals[0])
                self.play(fps)
                #print fps
            else:
                self.play(0)
            ev.accept()
        elif ev.key() == QtCore.Qt.Key_Home:
            self.setCurrentIndex(0)
            self.play(0)
            ev.accept()
        elif ev.key() == QtCore.Qt.Key_End:
            self.setCurrentIndex(self.getProcessedImage().shape[0]-1)
            self.play(0)
            ev.accept()
        elif ev.key() in self.noRepeatKeys:
            ev.accept()
            if ev.isAutoRepeat():
                return
            self.keysPressed[ev.key()] = 1
            self.evalKeyState()
        else:
            QtGui.QWidget.keyPressEvent(self, ev)

    def keyReleaseEvent(self, ev):
        if ev.key() in [QtCore.Qt.Key_Space, QtCore.Qt.Key_Home, QtCore.Qt.Key_End]:
            ev.accept()
        elif ev.key() in self.noRepeatKeys:
            ev.accept()
            if ev.isAutoRepeat():
                return
            try:
                del self.keysPressed[ev.key()]
            except:
                self.keysPressed = {}
            self.evalKeyState()
        else:
            QtGui.QWidget.keyReleaseEvent(self, ev)

    def evalKeyState(self):
        if len(self.keysPressed) == 1:
            key = list(self.keysPressed.keys())[0]
            if key == QtCore.Qt.Key_Right:
                self.play(20)
                self.jumpFrames(1)
                self.lastPlayTime = ptime.time() + 0.2  ## 2ms wait before start
                                                        ## This happens *after* jumpFrames, since it might take longer than 2ms
            elif key == QtCore.Qt.Key_Left:
                self.play(-20)
                self.jumpFrames(-1)
                self.lastPlayTime = ptime.time() + 0.2
            elif key == QtCore.Qt.Key_Up:
                self.play(-100)
            elif key == QtCore.Qt.Key_Down:
                self.play(100)
            elif key == QtCore.Qt.Key_PageUp:
                self.play(-1000)
            elif key == QtCore.Qt.Key_PageDown:
                self.play(1000)
        else:
            self.play(0)

    def timeout(self):
        now = ptime.time()
        dt = now - self.lastPlayTime
        if dt < 0:
            return
        n = int(self.playRate * dt)
        if n != 0:
            self.lastPlayTime += (float(n)/self.playRate)
            if self.currentIndex+n > self.image.shape[0]:
                self.play(0)
            self.jumpFrames(n)

    def setCurrentIndex(self, ind):
        """Set the currently displayed frame index."""
        self.currentIndex = np.clip(ind, 0, self.getProcessedImage().shape[self.axes['t']]-1)
        self.updateImage()
        self.ignoreTimeLine = True
        self.timeLine.setValue(self.tVals[self.currentIndex])
        self.ignoreTimeLine = False

    def jumpFrames(self, n):
        """Move video frame ahead n frames (may be negative)"""
        if self.axes['t'] is not None:
            self.setCurrentIndex(self.currentIndex + n)

    def hasTimeAxis(self):
        return 't' in self.axes and self.axes['t'] is not None

    def getMouseClickPos(self):
        pass

    '''################################################################################################################
                                            ROI Methods
       ################################################################################################################
    '''

    def addROI(self, ev=None, load=None):
        ''' Method for adding PolyROI's to the plot '''
        # self._workEnv_changed()
        #self.polyROI = PolyLineROI([[0,0], [10,10], [10,30], [30,10]], closed=True, pos=[0,0], removable=True)
        #self.ROICurve = self.ui.roiPlot.plot()

        # Create polyROI instance
        self.workEnv.ROIList.append(PolyLineROI([[0,0], [10,10], [30,10]],
                                                closed=True, pos=[0,0], removable=True))

        self.workEnv.ROIList[-1].tags = dict.fromkeys(configuration.proj_cfg.options('ROI_DEFS'), '')
        # Create new plot instance for plotting the newly created ROI
        self.curve = self.ui.roiPlot.plot()
        self.workEnv.CurvesList.append(self.curve)
        self.workEnv.CurvesList[-1].setZValue(len(self.workEnv.CurvesList))
        # Just some plot initializations, these are these from the original pyqtgraph ImageView class
        self.ui.roiPlot.setMouseEnabled(True, True)
        self.ui.splitter.setSizes([self.height()*0.6, self.height()*0.4])
        self.ui.roiPlot.show()

        # Connect signals to the newly created ROI
        self.workEnv.ROIList[-1].sigRemoveRequested.connect(self.delROI)
        # self.workEnv.ROIList[-1].sigRemoveRequested.connect(self._workEnv_changed)
        self.workEnv.ROIList[-1].sigRegionChanged.connect(self.updatePlot)# This is how the curve is plotted to correspond to this ROI
        # self.workEnv.ROIList[-1].sigRegionChanged.connect(self._workEnv_changed)
        self.workEnv.ROIList[-1].sigHoverEvent.connect(self.boldPlot)
        self.workEnv.ROIList[-1].sigHoverEvent.connect(self.setSelectedROI)
        self.workEnv.ROIList[-1].sigHoverEnd.connect(self.resetPlot)

        # Add the ROI to the scene so it can be seen
        self.view.addItem(self.workEnv.ROIList[-1])

        if load is not None:
            self.workEnv.ROIList[-1].setState(load)

        self.ui.listwROIs.addItem(str(len(self.workEnv.ROIList)-1))
#        self.ROIlist.append(self.polyROI)
#        d = self.ROItagDict.copy()
#        self.ROItags.append(d)
        # Update the plot to include this ROI which was just added
        self.updatePlot(len(self.workEnv.ROIList)-1)
        self.ui.listwROIs.setCurrentRow(len(self.workEnv.ROIList)-1)
        # So that ROI.tags is never = {}, which would result in NaN's
        self.setSelectedROI(len(self.workEnv.ROIList)-1)

    def addROI_options(self):
        pass

    def setSelectedROI(self, roi=None):
        if type(roi) == PolyLineROI:
            ID = self.workEnv.ROIList.index(roi)
            self.ui.listwROIs.setCurrentRow(ID)
        else:
            if self.ui.listwROIs.currentRow() != -1:
                ID = self.ui.listwROIs.currentRow()
            else:
                return

        self.ui.lineEdROIDef.clear()

        self.checkShowAllROIs()

        self.workEnv.ROIList[ID].show()

        if self.priorlistwROIsSelection is not None:
            try:
                self.workEnv.ROIList[self.priorlistwROIsSelection].setMouseHover(False)
            except IndexError:
                pass

        self.priorlistwROIsSelection = ID

        self.resetPlot()
        self.workEnv.ROIList[ID].setMouseHover(True)
        self.boldPlot(ID)

        if self.ui.listwROIDefs.count() > 0:
            for def_id in range(0, self.ui.listwROIDefs.count()):
                self.setROITagListText(ID, def_id)
            self.ui.listwROIDefs.setCurrentRow(0)

    def checkShowAllROIs(self):
        if self.ui.checkBoxShowAllROIs.isChecked() == False:
            for roi in self.workEnv.ROIList:
                roi.hide()
            return

        elif self.ui.checkBoxShowAllROIs.isChecked() == True:
            for roi in self.workEnv.ROIList:
                roi.show()

    def addROITag(self):
        if self.ui.listwROIDefs.currentRow() == -1 or self.ui.listwROIs.currentRow() == -1:
            QtWidgets.QMessageBox.question(self, 'Message',
                                           'Select an ROI Definition from the list if you want to add tags ',
                                           QtWidgets.QMessageBox.Ok)
            return

        ROI_ID = self.ui.listwROIs.currentRow()
        tag = self.ui.lineEdROIDef.text()
        definition = self.ui.listwROIDefs.currentItem().text().split(': ')[0]

        self.workEnv.ROIList[ROI_ID].tags[definition] = tag

        self.setROITagListText(ROI_ID, self.ui.listwROIDefs.currentRow())

        self.ui.lineEdROIDef.clear()
        print(self.workEnv.ROIList[ROI_ID].tags)

    def setROITagListText(self, ROI_ID, DEF_ID):
        if self.ui.listwROIDefs.currentRow() == -1 or self.ui.listwROIs.currentRow() == -1:
            return
        definition = self.ui.listwROIDefs.item(DEF_ID).text().split(': ')[0]

        try:
            tag = self.workEnv.ROIList[ROI_ID].tags[definition]
        except KeyError:
            tag = ''
            self.workEnv.ROIList[ROI_ID].tags[definition] = tag

        self.ui.listwROIDefs.item(DEF_ID).setText(definition + ': ' + tag)
        self.ui.listwROIDefs.setCurrentRow(min(DEF_ID + 1, self.ui.listwROIDefs.count() - 1))

    def delROI(self,roiPicked):
        ''' Pass in the roi object from ROI.sigRemoveRequested()
        gets the index position of this particular ROI from the ROIlist
        removes that ROI from the scene and removes it from the list
        AND removes the corresponding curve.'''

        ID = self.workEnv.ROIList.index(roiPicked)

        self.view.removeItem(self.workEnv.ROIList[ID])
        del self.workEnv.ROIList[ID]

#        del self.ROItags[ID]

        self.ui.listwROIs.takeItem(ID)


        for i in range(0, len(self.ui.listwROIs)):
            self.ui.listwROIs.item(i).setText(str(i))

        if isinstance(self.workEnv.CurvesList[ID], np.ndarray) is False:
            self.workEnv.CurvesList[ID].clear()
        del self.workEnv.CurvesList[ID]

         # Resets the color in the order of a bright rainbow, kinda.
         # ***** SHOULD REPLACE BY USING COLORMAP METHOD FROM PYQTGRAPH
        self.resetPlot()
        for ix in range(0,len(self.workEnv.ROIList)):
            self.updatePlot(ix)

    '''
    ###############################################################################################################
                                            Plot methods
    ###############################################################################################################
    '''

    # Pass the index of the ROI OR the ROI object itself for which you want to update the plot
    def updatePlot(self, ID, force=False):
        ''' If the index of the ROI in the ROIlist isn't passed as an argument to this function
         it will find the index of the ROI object which was passed. This comes from the Qt signal
         from the ROI: PolyLineROI.sigRegionChanged.connect'''
        if force is False and self.ui.btnPlot.isChecked() is False:
            return

        if type(ID) != int:
            ID = self.workEnv.ROIList.index(ID)

        color = self.ROIcolors[ID%(len(self.ROIcolors))]
        self.workEnv.ROIList[ID].setPen(color)

        # This stuff is from pyqtgraph's original class
        image = self.getProcessedImage()
        if image.ndim == 2:
            axes = (0, 1)
        elif image.ndim == 3:
            axes = (1, 2)
        else:
            return

        # Get the ROI region
        data = self.workEnv.ROIList[ID].getArrayRegion((image.view(np.ndarray)), self.imageItem, axes)#, returnMappedCoords=True)
        #,returnMappedCoords=True)
        if data is not None:
            while data.ndim > 1:
                data = data.mean(axis=1)
            if image.ndim == 3:
                # Set the curve
                # Fo = np.mean(np.take(data, np.arange(0, 300)))
                # data = np.divide(np.subtract(data, Fo), Fo)
                self.workEnv.CurvesList[ID].setData(y=data, x=self.tVals)
                self.workEnv.CurvesList[ID].setPen(color)
                self.workEnv.CurvesList[ID].show()
            else:
                while coords.ndim > 2:
                    coords = coords[:,:,0]
                coords = coords - coords[:,0,np.newaxis]
                xvals = (coords**2).sum(axis=0) ** 0.5
                self.workEnv.CurvesList[ID].setData(y=data, x=xvals)

    ''' SHOULD ADD TO PLOT CLASS ITSELF SO THAT THESE METHODS CAN BE USED ELSEWHERE OUTSIDE OF IMAGEVIEW '''
    # Make the curve bold & white. Used here when mouse hovers over the ROI. called by PolyLineROI.sigHoverEvent
    def boldPlot(self, ID):
        if type(ID) is not int:
            ID = self.workEnv.ROIList.index(ID)
        self.workEnv.CurvesList[ID].setPen(width=2)

    ''' SHOULD ADD TO PLOT CLASS ITSELF SO THAT THESE METHODS CAN BE USED ELSEWHERE OUTSIDE OF IMAGEVIEW '''
    # Used to un-bold and un-white, called by PolyLineROI.sigHoverEnd
    def resetPlot(self): #Set plot color back to what it was before
        for ID in range(0,len(self.workEnv.ROIList)):
            color = self.ROIcolors[ID%(len(self.ROIcolors))]
            self.workEnv.ROIList[ID].setPen(color)
            self.workEnv.CurvesList[ID].setPen(color)

    def plotAll(self):
        if self.ui.btnPlot.isChecked() == False:
            return
        for ID in range(0, len(self.workEnv.ROIList)):
            self.updatePlot(ID)


    '''
    ################################################################################################################
                                    Original pyqtgraph methods
    ################################################################################################################
    '''

    def quickMinMax(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        while data.size > 1e6:
            ax = np.argmax(data.shape)
            sl = [slice(None)] * data.ndim
            sl[ax] = slice(None, None, 2)
            data = data[sl]
        return nanmin(data), nanmax(data)

    def timeLineChanged(self):

        #(ind, time) = self.timeIndex(self.ui.timeSlider)
        if self.ignoreTimeLine:
            return
        self.play(0)
        (ind, time) = self.timeIndex(self.timeLine)
        if ind != self.currentIndex:
            self.currentIndex = ind
            self.updateImage()
        self.timeLineBorder.setPos(time)
        #self.timeLine.setPos(time)
        #self.emit(QtCore.SIGNAL('timeChanged'), ind, time)
        self.sigTimeChanged.emit(ind, time)

    def updateImage(self, autoHistogramRange=True):
        ## Redraw image on screen
        if self.image is None:
            return

        image = self.getProcessedImage()

        if autoHistogramRange:
            self.ui.histogram.setHistogramRange(self.levelMin, self.levelMax)

        # Transpose image into order expected by ImageItem
        if self.imageItem.axisOrder == 'col-major':
            axorder = ['t', 'x', 'y', 'c']
        else:
            axorder = ['t', 'y', 'x', 'c']
        axorder = [self.axes[ax] for ax in axorder if self.axes[ax] is not None]
        image = image.transpose(axorder)

        # Select time index
        if self.axes['t'] is not None:
            self.ui.roiPlot.show()
            image = image[self.currentIndex]

        self.imageItem.updateImage(image)


    def timeIndex(self, slider):
        ## Return the time and frame index indicated by a slider
        if self.image is None:
            return (0,0)

        t = slider.value()

        xv = self.tVals
        if xv is None:
            ind = int(t)
        else:
            if len(xv) < 2:
                return (0,0)
            totTime = xv[-1] + (xv[-1]-xv[-2])
            inds = np.argwhere(xv < t)
            if len(inds) < 1:
                return (0,t)
            ind = inds[-1,0]
        return ind, t

    def getView(self) -> ViewBox:
        """Return the ViewBox (or other compatible object) which displays the ImageItem"""
        return self.view

    def getImageItem(self):
        """Return the ImageItem for this ImageView."""
        return self.imageItem

    def getRoiPlot(self):
        """Return the ROI PlotWidget for this ImageView"""
        return self.ui.roiPlot

    def getHistogramWidget(self):
        """Return the HistogramLUTWidget for this ImageView"""
        return self.ui.histogram

    def export(self, fileName):
        """
        Export data from the ImageView to a file, or to a stack of files if
        the data is 3D. Saving an image stack will result in index numbers
        being added to the file name. Images are saved as they would appear
        onscreen, with levels and lookup table applied.
        """
        img = self.getProcessedImage()
        if self.hasTimeAxis():
            base, ext = os.path.splitext(fileName)
            fmt = "%%s%%0%dd%%s" % int(np.log10(img.shape[0])+1)
            for i in range(img.shape[0]):
                self.imageItem.setImage(img[i], autoLevels=False)
                self.imageItem.save(fmt % (base, i, ext))
            self.updateImage()
        else:
            self.imageItem.save(fileName)

    def setColorMap(self, colormap):
        """Set the color map.

        ============= =========================================================
        **Arguments**
        colormap      (A ColorMap() instance) The ColorMap to use for coloring
                      images.
        ============= =========================================================
        """
        # self.ui.histogram.gradient.setColorMap(colormap)
        self.setPredefinedGradient('flame')

    @addGradientListToDocstring()
    def setPredefinedGradient(self, name):
        """Set one of the gradients defined in :class:`GradientEditorItem <pyqtgraph.graphicsItems.GradientEditorItem>`.
        Currently available gradients are:
        """
        self.ui.histogram.gradient.loadPreset(name)
