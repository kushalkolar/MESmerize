# -*- coding: utf-8 -*-

'''
Modified ImageView class from the original pyqtgraph ImageView class.

This provides all the UI functionality of the Mesmerize viewer.
'''
"""
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
"""
import os
import numpy as np

from ..Qt import QtCore, QtGui, USE_PYSIDE
'''
if USE_PYSIDE:
    from .ImageViewTemplate_pyside import *
else:
    from .ImageViewTemplate_pyqt import *
'''

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

from MesmerizeCore import FileInput
from MesmerizeCore.stimMapWidget import *
from MesmerizeCore.caimanMotionCorrect import caimanPipeline
from MesmerizeCore.packager import viewerWorkEnv
import time
import configparser
import pickle
import tifffile
from functools import partial

try:
    from bottleneck import nanmin, nanmax
except ImportError:
    from numpy import nanmin, nanmax


#class PlotROI(ROI):
#    def __init__(self, size):
#        ROI.__init__(self, pos=[0,0], size=size) #, scaleSnap=True, translateSnap=True)
#        self.addScaleHandle([1, 1], [0, 0])
#        self.addRotateHandle([0, 0], [0.5, 0.5])

class ImageView(QtGui.QWidget):
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
        QtGui.QWidget.__init__(self, parent, *args)
        self.levelMax = 4096
        self.levelMin = 0
        self.name = name
        self.image = None
        self.axes = {}
        self.imageDisp = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.scene = self.ui.graphicsView.scene()
        
        
        
        self.ui.btnResetScale.clicked.connect(self.resetImgScale)
        
        # Set the main viewer objects to None so that proceeding methods know that these objects
        # don't exist for certain cases.
        
        self.workEnv = None
#        self.workEnvOrigin = None
#        self.workEnv.imgdata = None
#        self.mesfile = None
#        self.MesfileMap = None
        self.ui.splitter.setEnabled(False)
        self.currBatch = None
        
        # Initialize list of bands that indicate stimulus times
        self.currStimMapBg = []
#        self.bah ={'bah': []}
        

#        self.ui.lineEdROIDef1.textChanged.connect(self.updateROItag)
#        self.ui.lineEdROIDef2.textChanged.connect(self.updateROItag)
#        self.ui.lineEdROIDef3.textChanged.connect(self.updateROItag)
#        self.ui.lineEdROIDef4.textChanged.connect(self.updateROItag)
        
        self.ui.BtnSetROIDefs.clicked.connect(self.updateROItag)
        
        self.ui.listwROIs.itemClicked.connect(self.setSelectedROI)
        
        self.ui.checkBoxShowAllROIs.clicked.connect(self.setSelectedROI)
        self.priorlistwROIsSelection = None

        # ***** SHOULD USE PYQTGRAPH COLORMAP FUNCTION INSTEAD ****
        self.ROIcolors=['m','r','y','g','c']
        
        # Connect all the button signals
        self.ui.btnOpenFiles.clicked.connect(self.promptFileDialog)
        self.mesfileMap = None
        self.ui.listwMesfile.itemDoubleClicked.connect(lambda selection: 
                                                        self.updateWorkEnv(selection, origin='mesfile'))
        self.ui.listwTiffs.itemDoubleClicked.connect(lambda selection: 
                                                        self.updateWorkEnv(selection, origin='tiff'))
                                                     
        self.ui.listwSplits.itemDoubleClicked.connect(lambda selection: 
                                                        self.updateWorkEnv(selection, origin='splits'))
        self.ui.listwMotCor.itemDoubleClicked.connect(lambda selection:
                                                      self.updateWorkEnv(selection, origin='MotCor'))
        self.ui.btnAddROI.clicked.connect(self.addROI)
        self.ui.listwBatch.itemSelectionChanged.connect(self.setSelectedROI)
        self.ui.rigMotCheckBox.clicked.connect(self.checkSubArray)
        
        self.ui.btnSetID.clicked.connect(self.setSampleID)
        
        self.ui.btnStartBatch.clicked.connect(self.startBatch)  
        

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
        
#        self.ui.normGroup.hide()
#        #self.roi = PlotROI(10)
#        #self.roi.setZValue(20)
#        #self.view.addItem(self.roi)
#        #self.roi.hide()
#        self.normRoi = PlotROI(10)
#        self.normRoi.setPen('y')
#        self.normRoi.setZValue(20)
#        self.view.addItem(self.normRoi)
#        self.normRoi.hide()
        
        #self.roiCurve = self.ui.roiPlot.plot()
        
        
        self.timeLine = InfiniteLine(0, movable=True, hoverPen=None)
        self.timeLine.setPen((255, 255, 0, 200))
        self.timeLine.setZValue(2)
        self.timeLineBorder = InfiniteLine(0, movable=False, hoverPen=None)
        self.timeLineBorder.setPen(color=(0,0,0,110), width=5)
        self.timeLineBorder.setZValue(1)
        self.ui.roiPlot.addItem(self.timeLineBorder)
        self.ui.roiPlot.addItem(self.timeLine)
        self.ui.splitter.setSizes([self.height()-35, 35])
        self.ui.roiPlot.hideAxis('left')
        
        self.ui.splitterLeft.setSizes([172,573,160])
        self.ui.splitterBatches.setSizes([1215,221])
        
        self.keysPressed = {}
        self.playTimer = QtCore.QTimer()
        self.playRate = 0
        self.lastPlayTime = 0
        self.playTimer.timeout.connect(self.timeout)
#        self.normRgn = LinearRegionItem()
#        self.normRgn.setZValue(0)
#        self.ui.roiPlot.addItem(self.normRgn)
#        self.normRgn.hide()
            
        ## wrap functions from view box
        for fn in ['addItem', 'removeItem']:
            setattr(self, fn, getattr(self.view, fn))

        ## wrap functions from histogram
        for fn in ['setHistogramRange', 'autoHistogramRange', 'getLookupTable', 'getLevels']:
            setattr(self, fn, getattr(self.ui.histogram, fn))

        self.timeLine.sigPositionChanged.connect(self.timeLineChanged)
        #self.ui.roiBtn.clicked.connect(self.roiClicked)
        
        
        #self.roi.sigRegionChanged.connect(self.roiChanged)
        #self.ui.normBtn.toggled.connect(self.normToggled)
#        self.ui.menuBtn.clicked.connect(self.menuClicked)
#        self.ui.normDivideRadio.clicked.connect(self.normRadioChanged)
#        self.ui.normSubtractRadio.clicked.connect(self.normRadioChanged)
#        self.ui.normOffRadio.clicked.connect(self.normRadioChanged)
#        self.ui.normROICheck.clicked.connect(self.updateNorm)
#        self.ui.normFrameCheck.clicked.connect(self.updateNorm)
#        self.ui.normTimeRangeCheck.clicked.connect(self.updateNorm)
        
        
#        self.normProxy = SignalProxy(self.normRgn.sigRegionChanged, slot=self.updateNorm)
#        self.normRoi.sigRegionChangeFinished.connect(self.updateNorm)
        
        self.ui.roiPlot.registerPlot(self.name + '_ROI')# I don't know what this does,
                                                        # It was included with the original ImageView class
        self.view.register(self.name)
        
        self.noRepeatKeys = [QtCore.Qt.Key_Right, QtCore.Qt.Key_Left, QtCore.Qt.Key_Up, 
                             QtCore.Qt.Key_Down, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown]

        self.watcherStarted = False

    def _workEnv_checkSaved(self):
        if self.watcherStarted:
            return

        for ui_element in self.ui.tabBatchParams.children():
            print(type(ui_element))
            if type(ui_element) != QtWidgets.QLabel:
                if type(ui_element) == QtWidgets.QSpinBox:# or QtWidgets.QPushButton or QtWidgets.QCheckBox or QtWidgets.QSpinBox or QtWidgets.QSlider):
                    ui_element.valueChanged['int'].connect(self._workEnv_changed)
                    print(self.workEnv.saved)
                elif type(ui_element) == QtWidgets.QLineEdit:
                    ui_element.textChanged.connect(self._workEnv_changed)
                elif type(ui_element) == QtWidgets.QSlider:
                    ui_element.valueChanged['int'].connect(self._workEnv_changed)
        for ui_element in self.ui.tabROIs.children():
            if type(ui_element) == QtWidgets.QLineEdit:
                ui_element.textChanged.connect(self._workEnv_changed)
            elif type(ui_element) == QtWidgets.QPlainTextEdit:
                ui_element.textChanged.connect(self._workEnv_changed)
        self.watcherStarted = True

    def _workEnv_changed(self, element=None):
        if self.workEnv is not None:
            self.workEnv.saved = False
        print(str(element) + ' has been changed')
        
    ''' Set the ImgData object and pass the .seq of the ImgData object to setImage().
        Argumments:
            selection : object returned from self.ui.listwMesfile.itemDoubleClicked
    '''
    def updateWorkEnv(self, selection, origin):
        
        '''#################################################################################
        ####################################################################################
        >>>>>>>***** USE A OBSERVER PATTERN TO REGISTER workEnv.register WHEN CREATING WORK ENVIRONMENT?????
        >>>>>>> DE-REGISTER AND SET workEnv = None WHEN DiscardWorkEnv() <<<<<<<<<<<<<<<<<<<<<
        ####################################################################################'''
        if self.workEnv is not None:
            if self.DiscardWorkEnv() is False:
                return

        if origin == 'mesfile':
            self.workEnv = viewerWorkEnv.from_mesfile(self.mesfile, selection.text().split('//')[0])
            if self.workEnv is KeyError:
                QtGui.QMessageBox.information(self, 'KeyError', 'Could not find the selected'+\
                                              'image in the currently open mes file', QtGui.QMessageBox.Ok)
            if self.mesfileMap is not None:
                self.workEnv.stimMaps = (self.mesfileMap, 'mesfile')
                self.displayStimMap()
                # Set the stimulus map to the default one set for the entire mesfile (if any)
        
        elif origin == 'MotCor':
            print(selection.text())
            self.workEnv = viewerWorkEnv.from_pickle(selection.text()[:-7]+'.pik', selection.text())
            self.workEnv.imgdata.isMotCor = True
            if self.workEnv.imgdata.stimMaps is not None:
                self.displayStimMap()
                
        elif origin == 'tiff':
            self.workEnv = viewerWorkEnv.from_tiff()
            pass
        
        elif origin == 'splits':
            pass
        
        self.setImage(self.workEnv.imgdata.seq.T, pos=(0,0), scale=(1,1), 
                      xvals=np.linspace(1, self.workEnv.imgdata.seq.T.shape[0], 
                                        self.workEnv.imgdata.seq.T.shape[0]))

        self._workEnv_checkSaved()
        self.ui.splitter.setEnabled(True) # Enable stuff in the image & curve working area
        self.ui.tabBatchParams.setEnabled(True)
        self.ui.tabROIs.setEnabled(True)
         
    
    def resetImgScale(self):
        ''' 
        Reset the current image to the center of the scene and reset the scale
        doesn't work as intended in some weird circumstances when you repeatedly right click on the scene
        and set the x & y axis to 'Auto' a bunch of times. But this bug is hard to recreate.'''
        self.setImage(self.workEnv.imgdata.seq.T, pos=(0,0), scale=(1,1), 
                          xvals=np.linspace(1, self.workEnv.imgdata.seq.T.shape[0], 
                                            self.workEnv.imgdata.seq.T.shape[0]))
    
    def promptFileDialog(self):
        filelist = QtGui.QFileDialog.getOpenFileNames(self, 'Choose file(s)', 
                                                      '.', '(*.mes *.tif *.tiff)')
        if filelist == '':
            return
#        try:
        if filelist[0][0][-4:] == '.mes':
            self.mesfile = viewerWorkEnv.load_mesfile(filelist[0][0])
#            self.workEnvOrigin = 'mes'
#            self.mesfile = FileInput.MES(filelist[0][0])
            self.ui.listwMesfile.setEnabled(True) # Enable the mesfile list widget
            for i in self.mesfile.images:
                j = self.mesfile.image_descriptions[i]
                self.ui.listwMesfile.addItem(i+'//'+j) # Get the names of the images and add them to the list
            
            # If Auxiliary output information is found in the mes file it will ask if you want to
            # map them to anything
            ''' #######################################################################################
            ###########################################################################################
            ###########################################################################################
            >>>>>> ***** USE A FUNCTION TO GET VOLTAGES FROM ANY ARBITRARY AUX OUT OR AUX IN *** <<<<<<
            >>>>>> CHECK ALL KEYS IN MAIN_DICT WITH KEYS STARTING WITH AUX* 
            >>>>>>>>>>> **DIFFERENT TABS FOR DIFFERENT AUX. ** USER CAN GIVE A NAME TO THE CHANNEL. ***<<<
            >>>>>> HAVE A COMBOBOX THAT THE USER CAN USE TO SET THE CURRENT MAP VISUALIZED ON THE TIMELINE
            >>>>>> COMBOX ENTRY HAS THE NAME THE USER SET FOR THE AUX CHANELL
            >>>>>> **** DATAFRAME COLUMN USES NAME THAT THE USER HAS SET FOR THIS CHANNEL. THEY CAN SET
            >>>>>> **** A DIFFERENT NAME FOR EACH CHANNEL FOR A SINGLE IMG DATA OBJECT.
            >>>>>> **** ImgData.maps has all the different maps as a dict, where each key is the NAME the user has set
            ###########################################################################################
            ###########################################################################################
            ###########################################################################################'''
            if len(self.mesfile.voltDict) > 0:
                self.initMesStimMapGUI(self.mesfile.voltDict)# Init the stimMap GUI
                self.ui.btnChangeSMap.setEnabled(True)
                if QtGui.QMessageBox.question(self, '', 'This .mes file contains auxilliary output voltage ' + \
                              'information, would you like to apply a Stimulus Map now?',
                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                    self.stimmap.ui.checkBoxSetAll.setChecked(True)                    
                    self.stimmap.ui.checkBoxSetAll.setDisabled(True)
                    self.ui.btnResetSMap.setEnabled(True)
                    self.stimmapwindow.show()
            else:
                self.ui.btnResetSMap.setDisabled(True)
                self.ui.btnChangeSMap.setDisabled(True)
                    
    #        if filelist[0][0][-4:] == 'tiff':
    #            # Populate the list widget tiff file names, and store the file names as a var
            # ****** Should look into except IOError and IndexError
#        except IOError:
#            QtGui.QMessageBox.warning(self,'IOError', "There is an problem with the files you've selected", QtGui.QMessageBox.Ok)
    #            print('There''s an issue with the files you''ve selected')
    def initMesStimMapGUI(self, voltList):
        # Initialize stimMapWidget module in the background        
        self.stimMapWin = stimMapWindow(mesfile.voltDict)
        self.stimMapWin.resize(520, 120)
        for i in range(0, self.stimMapWin.tabs.count()):
            self.stimMapWin.tabs.widget(i).ui.setMapBtn.clicked.connect(self.storeMesStimMap)
        self.stimMapWin.show()
        # If user wants to change the map for this particular ImgData object
        self.ui.btnChangeSMap.clicked.connect(stimMapWin.show)
        # If user wants to set the map back to the one for the entire mes file
        self.ui.btnResetSMap.clicked.connect(self.setStimMap)


    def storeMesStimMap(self):
        self.stimMapWin.hide()
        # store a map in memory for the whole mesfile in the current work environment
        if QtGui.QMessageBox.question(self, 'Apply for whole mes file?', 'Would you like to apply these maps' +\
                    'for or the entire mes file?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.mesfileMap = self.stimmap.getStimMap()
        else:
            
    
    # Set stim map for the current ImgData object
    # specify dm if you want a custom map for this particular image which is different to the one
    # set for the whole mesfile
    def setStimMap(self, dm=None):
        if dm is None:
            dm = self.mesfileMap
        self.workEnv.imgdata.stimMaps = (dm, 'mesfile')
        self.displayStimMap()

    def displayStimMap(self):
        self.currStimMapBg = []
        for stim in self.workEnv.imgdata.stimMaps:
            definitions = stim[0][0]
            color = stim[0][-1]
            frameStart = stim[-1][0]
            frameEnd = stim[-1][1]
            
            
            linReg = LinearRegionItem(values=[frameStart, frameEnd], 
                            brush=color, movable=False, bounds=[frameStart, frameEnd])
            linReg.lines[0].setPen(color)
            linReg.lines[1].setPen(color)
            
            self.currStimMapBg.append(linReg)
        
        for linReg in self.currStimMapBg:
            self.ui.roiPlot.addItem(linReg)
            
        for i in range(0,len(self.workEnv.ROIList)):
            self.updatePlot(i)
        #print(self.workEnv.imgdata.Map)
    
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
            self.ui.sliderStrides.setMaximum(max_sval)
            self.ui.sliderOverlaps.setMaximum(max_sval)
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
            
        #if self.ui.roiBtn.isChecked():
        #    self.roiChanged()

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
        #else:
            #self.ui.roiPlot.hide()
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
        #self.roiClicked()

        profiler()

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
            #image = self.normalize(self.image)
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

#    def normRadioChanged(self):
#        self.imageDisp = None
#        self.updateImage()
#        self.autoLevels()
#        #self.roiChanged()
#        self.sigProcessingChanged.emit(self)
#    
#    def updateNorm(self):
#        if self.ui.normTimeRangeCheck.isChecked():
#            self.normRgn.show()
#        else:
#            self.normRgn.hide()
#        
#        if self.ui.normROICheck.isChecked():
#            self.normRoi.show()
#        else:
#            self.normRoi.hide()
#        
#        if not self.ui.normOffRadio.isChecked():
#            self.imageDisp = None
#            self.updateImage()
#            self.autoLevels()
#            #self.roiChanged()
#            self.sigProcessingChanged.emit(self)
#
#    def normToggled(self, b):
#        self.ui.normGroup.setVisible(b)
#        self.normRoi.setVisible(b and self.ui.normROICheck.isChecked())
#        self.normRgn.setVisible(b and self.ui.normTimeRangeCheck.isChecked())

    def hasTimeAxis(self):
        return 't' in self.axes and self.axes['t'] is not None

    def getMouseClickPos(self):
        pass
    
    def checkSubArray(self):
        if self.workEnv.imgdata.isSubArray is False and self.ui.rigMotCheckBox.isChecked() and\
                    QtGui.QMessageBox.question(self, 'Current ImgObj is not a sub-array', 
                   'You haven''t created a sub-array! This might create issues with motion correction. ' + \
                   'Continue anyways?',
                   QtGui.QMessageBox.Yes, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
            self.ui.rigMotCheckBox.setCheckState(False)
        return
    
    ''' Method for adding PolyROI's to the plot '''
    def addROI(self):
        #self.polyROI = PolyLineROI([[0,0], [10,10], [10,30], [30,10]], closed=True, pos=[0,0], removable=True)
        #self.ROICurve = self.ui.roiPlot.plot()
        
        # Create polyROI instance
        self.workEnv.ROIList.append(PolyLineROI([[0,0], [10,10], [30,10]], 
                                                closed=True, pos=[0,0], removable=True))
            
        # Create new plot instance for plotting the newly created ROI
        self.curve = self.ui.roiPlot.plot()
        self.workEnv.CurvesList.append(self.curve)
        
        # Just some plot initializations, these are these from the original pyqtgraph ImageView class
        self.ui.roiPlot.setMouseEnabled(True, True)
        self.ui.splitter.setSizes([self.height()*0.6, self.height()*0.4])        
        self.ui.roiPlot.showAxis('left')
        mn = self.tVals.min()
        mx = self.tVals.max()
        self.ui.roiPlot.setXRange(mn, mx, padding=0.01)
        self.timeLine.show()
        self.timeLine.setBounds([mn, mx])
        self.ui.roiPlot.show()
        
        # Connect signals to the newly created ROI
        self.workEnv.ROIList[-1].sigRemoveRequested.connect(self.delROI)
        self.workEnv.ROIList[-1].sigRemoveRequested.connect(self._workEnv_changed)
        self.workEnv.ROIList[-1].sigRegionChanged.connect(self.updatePlot)# This is how the curve is plotted to correspond to this ROI
        self.workEnv.ROIList[-1].sigRegionChanged.connect(self._workEnv_changed)
        self.workEnv.ROIList[-1].sigHoverEvent.connect(self.boldPlot)
        self.workEnv.ROIList[-1].sigHoverEnd.connect(self.resetPlot)

        # Add the ROI to the scene so it can be seen
        self.view.addItem(self.workEnv.ROIList[-1])

        self.ui.listwROIs.addItem(str(len(self.workEnv.ROIList)-1))
#        self.ROIlist.append(self.polyROI)
#        d = self.ROItagDict.copy()
#        self.ROItags.append(d)
        # Update the plot to include this ROI which was just added
        self.updatePlot(len(self.workEnv.ROIList)-1)
        self.ui.listwROIs.setCurrentRow(len(self.workEnv.ROIList)-1)

    def setSelectedROI(self, reset=True):
        self.ui.lineEdROIDef1.clear()
        ID = self.ui.listwROIs.currentRow()
        self.checkShowAllROIs()
        self.workEnv.ROIList[ID].show()
        if self.priorlistwROIsSelection is not None:
            self.workEnv.ROIList[self.priorlistwROIsSelection].setMouseHover(False)
        self.priorlistwROIsSelection = ID
        self.resetPlot()
        self.workEnv.ROIList[ID].setMouseHover(True)
        self.boldPlot(ID)

    def checkShowAllROIs(self):
        if self.ui.checkBoxShowAllROIs.isChecked() == False:
            for roi in self.workEnv.ROIList:
                roi.hide()
            return

        elif self.ui.checkBoxShowAllROIs.isChecked() == True:
            for roi in self.workEnv.ROIList:
                roi.show()

    
    def updateROItag(self):
        ID = int(self.ui.listwROIs.currentRow())
        if ID == -1:
            QtGui.QMessageBox.question(self, 'Message', 'Select an ROI form the list if you want to add tags ', QtGui.QMessageBox.Ok)
            return

        self.setListwROIsText(ID)
                
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

        self.workEnv.CurvesList[ID].clear()
        del self.workEnv.CurvesList[ID]
        
         # Resets the color in the order of a bright rainbow, kinda.
         # ***** SHOULD REPLACE BY USING COLORMAP METHOD FROM PYQTGRAPH
        self.resetPlot()
        for ix in range(0,len(self.workEnv.ROIList)):
            self.updatePlot(ix)
    
    # Pass the index of the ROI OR the ROI object itself for which you want to update the plot
    def updatePlot(self,ID):
        ''' If the index of the ROI in the ROIlist isn't passed as an argument to this function
         it will find the index of the ROI object which was passed. This comes from the Qt signal
         from the ROI: PolyLineROI.sigRegionChanged.connect'''
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
        #, returnMappedCoords=True)
        if data is not None:
            while data.ndim > 1:
                data = data.sum(axis=1)# Find the sum of pixel intensities
            if image.ndim == 3:
                # Set the curve
                self.workEnv.CurvesList[ID].setData(y=data, x=self.tVals)
                self.workEnv.CurvesList[ID].setPen(color)
                self.workEnv.CurvesList[ID].show()
                #self.ui.roiPlot.addItem(self.roiCurve)
                #self.ui.roiPlot.addItem(self.roiCurve2)
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
    
    def openBatch(self):
        batchFolder = QtGui.QFileDialog.getExistingDirectory(self, 'Select batch Dir', 
                                                      self.projPath + '/.batches/')
        if batchFolder == '':
            return
        for f in os.listdir(batchFolder):
            if f.endswith('.pik'):
                self.ui.listwBatch.addItem(batchFolder + '/' + f[:-4])
            elif f.endswith('_mc.npz'):
                self.ui.listwMotCor.addItem(batchFolder +'/' + f)
        if self.ui.listwBatch.count() > 0:
            self.ui.btnStartBatch.setEnabled(True)
    
    def setSampleID(self):
        self.workEnv.imgdata.SampleID = self.ui.lineEdAnimalID.text() + '_-_' +  self.ui.lineEdTrialID.text()
        
    def addToBatch(self):
        if os.path.isdir(self.projPath + '/.batches/') is False:
            os.mkdir(self.projPath + '/.batches/')
        if self.currBatch is None:
            self.currBatch = str(time.time())
            self.currBatchDir = self.projPath + '/.batches/' + self.currBatch
            os.mkdir(self.currBatchDir)
        
        if self.workEnv.imgdata.isMotCor is False and self.ui.rigMotCheckBox.isChecked():
            mc_params = self.getMotCorParams()
        else:
            mc_params = None
        
        self.setSampleID()
#        SampleID = self.workEnv.imgdata.SampleID
#        
#        fileName = self.currBatchDir + '/' + SampleID + '_' + str(time.time())
                
#        tifffile.imsave(fileName+'.tiff', self.workEnv.imgdata.seq.T)
        
#        meta = self.workEnv.imgdata.meta
#        Map = self.workEnv.imgdata.Map
#        isSubArray = self.workEnv.imgdata.isSubArray
#        isMotCor = self.workEnv.imgdata.isMotCor
#        isDenoised = self.workEnv.imgdata.isDenoised
#        
#        
#        imdata = {'SampleID': SampleID, 'meta': meta, 
#                  'Map': Map, 'isSubArray': isSubArray, 'isMotCor': isMotCor,
#                  'isDenoised': isDenoised}
        
#        data = {'rigid_params': rigid_params, 'elas_params': elas_params}
        
#        pickle.dump(data, open(fileName+'.pik', 'wb'))
        
        rval, fileName = self.workEnv.to_pickle(self.currBatchDir, mc_params)
        
        if rval:
            self.ui.listwBatch.addItem(fileName)
            self.ui.btnStartBatch.setEnabled(True)

            self.ui.lineEdAnimalID.clear()
            self.ui.lineEdTrialID.clear()
            self.ui.lineEdGenotype.clear()

        else:
            print('Error when saving the file')
            
    def startBatch(self):
        batchSize = self.ui.listwBatch.count()
        self.ui.progressBar.setEnabled(True)
        self.ui.progressBar.setValue(1)
        for i in range(0, batchSize):
            cp = caimanPipeline(self.ui.listwBatch.item(i).text())
            self.ui.abortBtn.setEnabled(True)
            ''' USE AN OBSERVER PATTERN TO SEE WHEN THE PROCESS IS DONE!!!'''
            cp.start()
            print('>>>>>>>>>>>>>>>>>>>> Starting item: ' + str(i) + ' <<<<<<<<<<<<<<<<<<<<')
#            while cp.is_alive():
#                time.sleep(10)
        if os.path.isfile(self.ui.listwBatch.item(i).text()+'_mc.npz'):
            self.ui.listwMotCor.addItem(self.ui.listwBatch.item(i).text()+'_mc.npz')
            self.ui.listwMotCor.item(i).setBackground(QtGui.QBrush(QtGui.QColor('green')))
        else:
            self.ui.listwMotCor.addItem(self.ui.listwBatch.item(i).text()+'_mc.npz')
            self.ui.listwMotCor.item(i).setBackground(QtGui.QBrush(QtGui.QColor('red')))
#            self.ui.progressBar.setValue(100/batchSize)
        self.ui.abortBtn.setDisabled(True)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setDisabled(True)
    
    def clearBatchList(self):
        pass
    
    # Get Motion Correction Parameters from the GUI
    def getMotCorParams(self):
        #decay_time = float(self.ui.spinboxDecay.text())
        num_iters_rigid = int(self.ui.spinboxIter.text())
        rig_shifts_x = int(self.ui.spinboxX.text())
        rig_shifts_y = int(self.ui.spinboxY.text())
        num_threads = int(self.ui.spinboxThreads.text())
        
        rigid_params = {'decay_time': None, 'num_iters_rigid': num_iters_rigid, 
             'rig_shifts_x': rig_shifts_x, 'rig_shifts_y': rig_shifts_y,
             'num_threads': num_threads}
        
        if self.ui.elasMotCheckBox.isChecked():        
            strides = int(self.ui.sliderStrides.value())
            overlaps = int(self.ui.sliderOverlaps.value())
            upsample = int(self.ui.spinboxUpsample.text())
            max_dev = int(self.ui.spinboxMaxDev.text())
            
            elas_params = {'strides': strides, 'overlaps': overlaps,
                           'upsample': upsample, 'max_dev': max_dev}
        else:
            elas_params = None
        return rigid_params, elas_params

            
    def DiscardWorkEnv(self):
        if (self.workEnv.saved == False) and (QtGui.QMessageBox.warning(self, 'Warning!',
                  'You have unsaved work in your environment. Would you like to discard them and continue?',
                       QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)) == QtGui.QMessageBox.No:
                return False
        self.clearWorkEnv()
        return True
    
    # Clear the ROIs and plots
    def clearWorkEnv(self):
        # Remove any ROIs and associated curves on the plot
        for i in range(0,len(self.workEnv.ROIList)):
            self.delROI(self.workEnv.ROIList[0])
            '''calls delROI method to remove the ROIs from the list.
            You cannot simply reset the list to ROI = [] because objects must be removed from the scene
            and curves removed from the plot. This is what delROI() does. Removes the 0th once in each 
            iteration, number of iterations = len(ROIlist)'''
            
        # In case the user decided to add some of their own curves that don't correspond to the ROIs
        if len(self.workEnv.CurvesList) != 0:
            for i in range(0,len(self.workEnv.CurvesList)):
                self.workEnv.CurvesList[i].clear()
        
        # re-initialize ROI and curve lists
        self.workEnv = None
#        self._remove_workEnv_observer()
        
        # Remove the background bands showing stimulus times.
        for linReg in self.currStimMapBg:
            self.ui.roiPlot.removeItem(linReg)
       
#    def roiClicked(self):
#        showRoiPlot = False
#        if self.ui.roiBtn.isChecked():
#            showRoiPlot = True
#            self.roi.show()
#            #self.ui.roiPlot.show()
#            self.ui.roiPlot.setMouseEnabled(True, True)
#            self.ui.splitter.setSizes([self.height()*0.6, self.height()*0.4])
#            self.roiCurve.show()
#            self.roiCurve2 = self.ui.roiPlot.plot()
#            self.CurvesList.append(roiCurve2)
#            self.roiCurve2.show()
#            self.roiChanged()
#            self.ui.roiPlot.showAxis('left')
#        else:
#            self.roi.hide()
#            self.ui.roiPlot.setMouseEnabled(False, False)
#            self.roiCurve.hide()
#            self.ui.roiPlot.hideAxis('left')
#            
#        if self.hasTimeAxis():
#            showRoiPlot = True
#            mn = self.tVals.min()
#            mx = self.tVals.max()
#            self.ui.roiPlot.setXRange(mn, mx, padding=0.01)
#            self.timeLine.show()
#            self.timeLine.setBounds([mn, mx])
#            self.ui.roiPlot.show()
#            if not self.ui.roiBtn.isChecked():
#                self.ui.splitter.setSizes([self.height()-35, 35])
#        else:
#            self.timeLine.hide()
#            #self.ui.roiPlot.hide()
#            
#        self.ui.roiPlot.setVisible(showRoiPlot)

#    def roiChanged(self):
#        if self.image is None:
#            return
#            
#        image = self.getProcessedImage()
#        if image.ndim == 2:
#            axes = (0, 1)
#        elif image.ndim == 3:
#            axes = (1, 2)
#        else:
#            return
#        
#        data, coords = self.roi.getArrayRegion(image.view(np.ndarray), self.imageItem, axes, returnMappedCoords=True)
#        if data is not None:
#            while data.ndim > 1:
#                data = data.sum(axis=1)
#            if image.ndim == 3:
#                #self.roiCurve2 = self.roiCurve
#                self.roiCurve2.setData(y=np.random.rand(1577)*2000, x=self.tVals)
#                self.roiCurve2.show()
#                self.roiCurve.setData(y=data, x=self.tVals)
#                #self.ui.roiPlot.addItem(self.roiCurve)
#                #self.ui.roiPlot.addItem(self.roiCurve2)
#            else:
#                while coords.ndim > 2:
#                    coords = coords[:,:,0]
#                coords = coords - coords[:,0,np.newaxis]
#                xvals = (coords**2).sum(axis=0) ** 0.5
#                self.roiCurve.setData(y=data, x=xvals)

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

#    def normalize(self, image):
#        """
#        Process *image* using the normalization options configured in the
#        control panel.
#        
#        This can be repurposed to process any data through the same filter.
#        """
#        if self.ui.normOffRadio.isChecked():
#            return image
#            
#        div = self.ui.normDivideRadio.isChecked()
#        norm = image.view(np.ndarray).copy()
#        #if div:
#            #norm = ones(image.shape)
#        #else:
#            #norm = zeros(image.shape)
#        if div:
#            norm = norm.astype(np.float32)
#            
#        if self.ui.normTimeRangeCheck.isChecked() and image.ndim == 3:
#            (sind, start) = self.timeIndex(self.normRgn.lines[0])
#            (eind, end) = self.timeIndex(self.normRgn.lines[1])
#            #print start, end, sind, eind
#            n = image[sind:eind+1].mean(axis=0)
#            n.shape = (1,) + n.shape
#            if div:
#                norm /= n
#            else:
#                norm -= n
#                
#        if self.ui.normFrameCheck.isChecked() and image.ndim == 3:
#            n = image.mean(axis=1).mean(axis=1)
#            n.shape = n.shape + (1, 1)
#            if div:
#                norm /= n
#            else:
#                norm -= n
#            
#        if self.ui.normROICheck.isChecked() and image.ndim == 3:
#            n = self.normRoi.getArrayRegion(norm, self.imageItem, (1, 2)).mean(axis=1).mean(axis=1)
#            n = n[:,np.newaxis,np.newaxis]
#            #print start, end, sind, eind
#            if div:
#                norm /= n
#            else:
#                norm -= n
#                
#        return norm
        
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

    def getView(self):
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
            
#    def exportClicked(self):
#        fileName = QtGui.QFileDialog.getSaveFileName()
#        if fileName == '':
#            return
#        self.export(fileName)
#        
#    def buildMenu(self):
#        self.menu = QtGui.QMenu()
#        self.normAction = QtGui.QAction("Normalization", self.menu)
#        self.normAction.setCheckable(True)
#        self.normAction.toggled.connect(self.normToggled)
#        self.menu.addAction(self.normAction)
#        self.exportAction = QtGui.QAction("Export", self.menu)
#        self.exportAction.triggered.connect(self.exportClicked)
#        self.menu.addAction(self.exportAction)
#        
#    def menuClicked(self):
#        if self.menu is None:
#            self.buildMenu()
#        self.menu.popup(QtGui.QCursor.pos())

    def setColorMap(self, colormap):
        """Set the color map. 

        ============= =========================================================
        **Arguments**
        colormap      (A ColorMap() instance) The ColorMap to use for coloring 
                      images.
        ============= =========================================================
        """
        self.ui.histogram.gradient.setColorMap(colormap)

    @addGradientListToDocstring()
    def setPredefinedGradient(self, name):
        """Set one of the gradients defined in :class:`GradientEditorItem <pyqtgraph.graphicsItems.GradientEditorItem>`.
        Currently available gradients are:   
        """
        self.ui.histogram.gradient.loadPreset(name)
