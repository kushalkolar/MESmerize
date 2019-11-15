# -*- coding: utf-8 -*-
import sys
from ...Qt import QtCore, QtGui
from ...widgets.SpinBox import SpinBox
#from ...SignalProxy import SignalProxy
from ...WidgetGroup import WidgetGroup
#from ColorMapper import ColorMapper
from ..Node import Node
import numpy as np
from ...widgets.ColorButton import ColorButton
from ....analysis import Transmission
from tqdm import tqdm
try:
    import metaarray
    HAVE_METAARRAY = True
except:
    HAVE_METAARRAY = False

from ...widgets.ComboBox import ComboBox as QComboBox
from ...widgets.ListWidget import ListWidget
from ...widgets.LineEdit import LineEdit
from ...widgets.KwargPlainTextEdit import KwargPlainTextEdit
from ....analysis import organize_dataframe_columns
# from PyQt5.QtWidgets import QLineEdit as LineEdit


def generateUi(opts):
    """Convenience function for generating common UI types"""
    widget = QtGui.QWidget(parent=None)
    l = QtGui.QFormLayout()
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
            w = QtGui.QSpinBox()
            if 'max' in o:
                w.setMaximum(o['max'])
            if 'min' in o:
                w.setMinimum(o['min'])
            if 'value' in o:
                w.setValue(o['value'])
            if 'step' in o:
                w.setSingleStep(o['step'])

        elif t == 'doubleSpin':
            w = QtGui.QDoubleSpinBox()
            if 'max' in o:
                w.setMaximum(o['max'])
            if 'min' in o:
                w.setMinimum(o['min'])                
            if 'value' in o:
                w.setValue(o['value'])
            if 'step' in o:
                w.setSingleStep(o['step'])

        elif t == 'check':
            w = QtGui.QCheckBox()
            if 'checked' in o:
                w.setChecked(o['checked'])
            if 'applyBox' in o:
                if o['applyBox'] is True:
                    w.setToolTip('When checked this node will process all incoming data.\n'
                                 'Therefore note that this will cause the program to behave\n'
                                 'slowly if you are constantly changing things around\n'
                                 'while keeping this checked.')

        elif t == 'radioBtn':
            w = QtGui.QRadioButton()
            if 'checked' in o:
                w.setChecked(o['checked'])

        elif t == 'combo':
            w = QComboBox()
            if 'values' in o.keys():
                for i in o['values']:
                    if i != '':
                        w.addItem(i)
            if 'items' in o.keys():
                w.setItems(o['items'])

        elif t == 'list_widget':
            w = ListWidget()
            if 'items' in o.keys():
                w.setItems(o['items'])
            if 'selection_mode' in o.keys():
                w.setSelectionMode(o['selection_mode'])

        elif t == 'lineEdit':
            # w = QtGui.QLineEdit()
            w = LineEdit()
            if 'placeHolder' in o:
                w.setPlaceholderText(o['placeHolder'])
            if 'text' in o:
                w.setText(o['text'])
            if 'readOnly' in o:
                w.setReadOnly(True)

        elif t == 'plainTextEdit':
            w = QtGui.QPlainTextEdit()
            if 'placeHolder' in o:
                w.setPlaceholderText(o['placeHolder'])
            if 'text' in o:
                w.setText(o['text'])

        elif t == 'kwargTextEdit':
            w = KwargPlainTextEdit()
            if 'placeHolder' in o:
                w.setPlaceholderText(o['placeHolder'])
            if 'text' in o:
                w.setText(o['text'])

        elif t == 'label':
            w = QtGui.QLabel()
            if 'text' in o:
                w.setText(o['text'])

        elif t == 'button':
            w = QtGui.QPushButton()
            if 'text' in o:
                w.setText(o['text'])
            if 'checkable' in o:
                w.setChecked(o['checkable'])

        elif t == 'color':
            w = ColorButton()
        else:
            raise Exception("Unknown widget type '%s'" % str(t))
        if 'toolTip' in o:
            w.setToolTip(o['toolTip'])
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
        """:param terminals: Dict containing terminal names and specifying whether they are input or output terminals"""

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
        self.t = None
        self._data_column = None

    def ctrlWidget(self):
        return self.ui
       
    def changed(self):
        self.update()
        self.sigStateChanged.emit(self)
        out = f"Processing node: {self.name()}\n"

        sys.stdout.write(out)

    def process(self, **kwargs):#In, display=True):
        In = kwargs['In']

        if In is None:
            return

        if type(In) is None:
            raise TypeError('Incoming transmission is None')

        if isinstance(In, Transmission):
            if In.df.empty:
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

    def set_data_column_combo_box(self):
        try:
            columns = self.t.df.columns
            self.ctrls['data_column'].setItems(organize_dataframe_columns(columns.to_list())[0])
            ix = self.ctrls['data_column'].findText(self.t.last_output)
            if ix > 0:
                self.ctrls['data_column'].setCurrentIndex(ix)
        except:
            pass

    @property
    def data_column(self):
        try:
            self._data_column = self.ctrls['data_column'].currentText()
            return self._data_column
        except:
            return None

    @data_column.setter
    def data_column(self, d):
        pass

    def apply_checked(self) -> bool:
        return self.ctrls['Apply'].isChecked()


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


def merge_transmissions(transmissions) -> list:
    if not len(transmissions) > 0:
        raise Exception('No incoming transmissions')

    transmissions_list = []

    for t in transmissions.items():
        t = t[1]
        if t is None:
            raise TypeError('One of your transmissions is None')
           # continue
        if type(t) is list:
            for i in range(len(t)):
                if t[i] is None:
                    raise TypeError('One of your transmissions is None')
                    # QtGui.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                    # continue
                transmissions_list.append(t[i].copy())
            continue

        transmissions_list.append(t.copy())
    return transmissions_list


normalize_zero_one = lambda a: ((a - np.min(a)) / (np.max(a - np.min(a))))
