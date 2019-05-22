from plotting.matplotlibformatter_window import Ui_Form
from PyQt5 import QtCore, QtGui, QtWidgets
import seaborn as sns
from variants.violins import ViolinsPlot
import sys 
class MatplotFormatter(QtWidgets.QWidget):
    sig_plot_changed = QtCore.pyqtSignal() # Main plotting class can use this signal to call its draw() method to redraw the plot when stuff is done

    def __init__(self, plot_object):
        QtWidgets.QWidget.__init__(self)
        self._plot_object = plot_object
        self._formatter_ui = Ui_Form() # A simple widget for doing all the things
        self._formatter_ui.setupUi(self)
        
        self.fig = None
        self._xtick_labels_orig = None
        self._xtick_labels_edit = None
        self._xlabels_orig = None
        self._ylabels_orig = None
        self._xlabels_edit = None
        self._ylabels_edit = None
        
        if isinstance(self._plot_object, ViolinsPlot):
            self.ax = self._plot_object.axes
        else:
            self.ax = [self._plot_object.ax]
        self.xdata_type = None
        self.ydata_type = None
        
        self._formatter_ui.listWidget_xticklabels_edit.itemDoubleClicked.connect(self._edit_label)
        self._formatter_ui.listWidget_xlabels_edit.itemDoubleClicked.connect(self._edit_label)
        self._formatter_ui.listWidget_ylabels_edit.itemDoubleClicked.connect(self._edit_label)
        
        self._formatter_ui.pushButton_Apply.clicked.connect(self._apply_changes)
        
        self._set_formatter()
        
    def _set_formatter(self):
        self._get_xticklabels()
        self._get_xylabels()
        
    def _get_xticklabels(self):
        self._xtick_labels_orig = [x.get_text() for x in self.ax[0].get_xticklabels()]
        self._formatter_ui.listWidget_xticklabels_orig.addItems(self._xtick_labels_orig)
        if self._xtick_labels_edit == None:
            self._xtick_labels_edit = self._xtick_labels_orig
        self._formatter_ui.listWidget_xticklabels_edit.addItems(self._xtick_labels_edit)
    
    def _set_xticklabels(self):
        for ax in self.ax:
            ax.set_xticklabels(self._xtick_labels_edit)
    
    
    def _edit_label(self, item):
        new_text, ok = QtWidgets.QInputDialog.getText(self,"renaming...","Enter a new name")
        if ok and new_text != "":
            item.setText(new_text)
            self._update_editted_labels()
        
    
    def _update_editted_labels(self):
        self._xtick_labels_edit = [self._formatter_ui.listWidget_xticklabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_xticklabels_edit.count())]
        self._xlabels_edit = [self._formatter_ui.listWidget_xlabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_xlabels_edit.count())]
        self._ylabels_edit = [self._formatter_ui.listWidget_ylabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_ylabels_edit.count())]
        
    
    def _get_xylabels(self):
        self._xlabels_orig = [ax.get_xlabel() for ax in self.ax]
        self._ylabels_orig = [ax.get_ylabel() for ax in self.ax]
        if self._xlabels_edit == None:
            self._xlabels_edit = self._xlabels_orig
        if self._ylabels_edit == None:
            self._ylabels_edit = self._ylabels_orig
        for widget, labels in zip([self._formatter_ui.listWidget_xlabels_orig,
                                   self._formatter_ui.listWidget_xlabels_edit,
                                   self._formatter_ui.listWidget_ylabels_orig,
                                   self._formatter_ui.listWidget_ylabels_edit],
                                  [self._xlabels_orig,
                                   self._xlabels_edit,
                                   self._ylabels_orig,
                                   self._ylabels_edit]):
            widget.addItems(labels)
        
    def _set_xylabels(self):
        for ax, xlabel, ylabel in zip(self.ax, self._xlabels_edit, self._ylabels_edit):
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
    
    def _apply_changes(self):
        self._set_xticklabels()
        self._set_xylabels()
        self._plot_object.fig
if __name__ == "__main__":
#    app = QtWidgets.QApplication([])
    
    iris = sns.load_dataset('iris')
    v = ViolinsPlot()
    v.set(iris, [x for x in iris.columns if "species" not in x], "species")
    m = MatplotFormatter(plot_object=v)
    m.show()
#    sys.exit(app.exec())