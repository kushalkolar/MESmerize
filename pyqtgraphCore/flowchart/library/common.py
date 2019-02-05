# -*- coding: utf-8 -*-
from ...Qt import QtCore, QtGui, QtWidgets
from ...widgets.SpinBox import SpinBox
#from ...SignalProxy import SignalProxy
from ...WidgetGroup import WidgetGroup
#from ColorMapper import ColorMapper
from ..Node import Node
import numpy as np
from ...widgets.ColorButton import ColorButton
from analyser.DataTypes import Transmission
try:
    import metaarray
    HAVE_METAARRAY = True
except:
    HAVE_METAARRAY = False


def generateUi(opts):
    """Convenience function for generating common UI types"""
    widget = QtWidgets.QWidget(parent=None)
    l = QtWidgets.QFormLayout()
    l.setSpacing(0)
    widget.setLayout(l)
    ctrls = {}
    row = 0
    for opt in opts:
        if len(opt) == 2:
            k, t = opt
            o = {}
        elif len(opt) == 3:
            k, t, o = opt
        else:
            raise Exception("Widget specification must be (name, type) or (name, type, {opts})")
        if t == 'intSpin':
            # w = QtGui.QSpinBox()
            w = QtWidgets.QSpinBox()
            if 'max' in o:
                w.setMaximum(o['max'])
            if 'min' in o:
                w.setMinimum(o['min'])
            if 'value' in o:
                w.setValue(o['value'])
            if 'step' in o:
                w.setSingleStep(o['step'])

        elif t == 'doubleSpin':
            w = QtWidgets.QDoubleSpinBox()
            if 'max' in o:
                w.setMaximum(o['max'])
            if 'min' in o:
                w.setMinimum(o['min'])                
            if 'value' in o:
                w.setValue(o['value'])
            if 'step' in o:
                w.setSingleStep(o['step'])

        # elif t == 'spin':
        #     w = SpinBox()
        #     w.setOpts(**o)

        elif t == 'check':
            w = QtWidgets.QCheckBox()
            if 'checked' in o:
                w.setChecked(o['checked'])
            if 'toolTip' in o:
                w.setToolTip(o['toolTip'])
            if 'applyBox' in o:
                if o['applyBox'] is True:
                    w.setToolTip('When checked this node will process all incoming data.\n'
                                 'Therefore note that this will cause the program to behave\n'
                                 'slowly if you are constantly changing things around\n'
                                 'while keeping this checked.')

        elif t == 'radioBtn':
            w = QtWidgets.QRadioButton()
            if 'checked' in o:
                w.setChecked(o['checked'])

        elif t == 'combo':
            w = QtWidgets.QComboBox()
            if 'values' in o.keys():
                for i in o['values']:
                    if i != '':
                        w.addItem(i)

        elif t == 'lineEdit':
            w = QtWidgets.QLineEdit()
            if 'placeHolder' in o:
                w.setPlaceholderText(o['placeHolder'])
            if 'text' in o:
                w.setText(o['text'])
            if 'toolTip' in o:
                w.setToolTip(o['toolTip'])

        elif t == 'label':
            w = QtWidgets.QLabel()
            if 'text' in o:
                w.setText(o['text'])
            if 'toolTip' in o:
                w.setToolTip(o['toolTip'])

        elif t == 'button':
            w = QtWidgets.QPushButton()
            if 'text' in o:
                w.setText(o['text'])
            if 'checkable' in o:
                w.setChecked(o['checkable'])
            if 'toolTip' in o:
                w.setToolTip(o['toolTip'])

        #elif t == 'colormap':
            #w = ColorMapper()
        elif t == 'color':
            w = ColorButton()
        else:
            raise Exception("Unknown widget type '%s'" % str(t))
        if 'tip' in o:
            w.setToolTip(o['tip'])
        w.setObjectName(k)
        l.addRow(k, w)
        if o.get('hidden', False):
            w.hide()
            label = l.labelForField(w)
            label.hide()
            
        ctrls[k] = w
        w.rowNum = row
        row += 1
    group = WidgetGroup(widget)
    return widget, group, ctrls


class CtrlNode(Node):
    """Abstract class for nodes with auto-generated control UI"""
    
    sigStateChanged = QtCore.Signal(object)
    
    def __init__(self, name, ui=None, terminals=None, **kwargs):
        if ui is None:
            if hasattr(self, 'uiTemplate'):
                ui = self.uiTemplate
            else:
                ui = []
        if terminals is None:
            terminals = {'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}}
        Node.__init__(self, name=name, terminals=terminals)
        
        self.ui, self.stateGroup, self.ctrls = generateUi(ui)
        self.stateGroup.sigChanged.connect(self.changed)
        self.count = 0

    def ctrlWidget(self):
        return self.ui
       
    def changed(self):
        self.update()
        self.sigStateChanged.emit(self)

    def process(self, **kwargs):#In, display=True):
        In = kwargs['In']

        if In is None:
            return

        # if 'Out' in kwargs.items():
            # print(' !!!!!!!!! >>>>>>>>>> OUT PASSED INTO process() <<<<<<<<<<<<<<< !!!!!!!!!!!!')
            # print(kwargs['Out'])
            # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

        if type(In) is None:
            raise TypeError('Incoming tranmission is None')

        if isinstance(In, Transmission):
            if In.df.empty:
                # QtGui.QMessageBox.warning(None, 'IndexError!',
                #                                 'The DataFrame of the incoming transmission is empty!')
                raise IndexError('The DataFrame of the incoming transmission is empty!')

        out = self.processData(In)
        return {'Out': out}
    
    def saveState(self):
        # self.changed()
        state = Node.saveState(self)
        state['ctrl'] = self.stateGroup.state()
        return state
    
    def restoreState(self, state):
        Node.restoreState(self, state)
        if self.stateGroup is not None:
            self.stateGroup.setState(state.get('ctrl', {}))
        # self.changed()
            
    def hideRow(self, name):
        w = self.ctrls[name]
        l = self.ui.layout().labelForField(w)
        w.hide()
        l.hide()
        
    def showRow(self, name):
        w = self.ctrls[name]
        l = self.ui.layout().labelForField(w)
        w.show()
        l.show()


class PlottingCtrlNode(CtrlNode):
    """Abstract class for CtrlNodes that can connect to plots."""
    
    def __init__(self, name, ui=None, terminals=None):
        #print "PlottingCtrlNode.__init__ called."
        CtrlNode.__init__(self, name, ui=ui, terminals=terminals)
        self.plotTerminal = self.addOutput('plot', optional=True)

    def connected(self, term, remote):
        CtrlNode.connected(self, term, remote)
        if term is not self.plotTerminal:
            return
        node = remote.node()
        node.sigPlotChanged.connect(self.connectToPlot)
        self.connectToPlot(node)    
        
    def disconnected(self, term, remote):
        CtrlNode.disconnected(self, term, remote)
        if term is not self.plotTerminal:
            return
        remote.node().sigPlotChanged.disconnect(self.connectToPlot)
        self.disconnectFromPlot(remote.node().getPlot())   
       
    def connectToPlot(self, node):
        """Define what happens when the node is connected to a plot"""
        raise Exception("Must be re-implemented in subclass")
    
    def disconnectFromPlot(self, plot):
        """Define what happens when the node is disconnected from a plot"""
        raise Exception("Must be re-implemented in subclass")

    def process(self, In, display=True):
        out = CtrlNode.process(self, In, display)
        out['plot'] = None
        return out


def metaArrayWrapper(fn):
    def newFn(self, data, *args, **kargs):
        if HAVE_METAARRAY and (hasattr(data, 'implements') and data.implements('MetaArray')):
            d1 = fn(self, data.view(np.ndarray), *args, **kargs)
            info = data.infoCopy()
            if d1.shape != data.shape:
                for i in range(data.ndim):
                    if 'values' in info[i]:
                        info[i]['values'] = info[i]['values'][:d1.shape[i]]
            return metaarray.MetaArray(d1, info=info)
        else:
            return fn(self, data, *args, **kargs)
    return newFn


def merge_transmissions(transmissions):
    if not len(transmissions) > 0:
        raise Exception('No incoming transmissions')

    transmissions_list = []

    for t in transmissions.items():
        t = t[1]
        if t is None:
            QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
            continue
        if type(t) is list:
            for i in range(len(t)):
                if t[i] is None:
                    QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                    continue
                transmissions_list.append(t[i].copy())
            continue

        transmissions_list.append(t.copy())
    return transmissions_list
    #self.plot_gui.update_input_transmissions(transmissions_list)

