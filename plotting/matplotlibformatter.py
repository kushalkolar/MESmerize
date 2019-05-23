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
        
        self._connect_gui()
        
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

        self._formatter_ui
        
        self._formatter_ui.pushButton_Apply.clicked.connect(self._apply_changes)
        
        self._set_formatter()
    
    def _connect_gui(self):
        """
        Connect the gui objects to the class methods
        """
                
        self._formatter_ui.listWidget_xticklabels_edit.itemDoubleClicked.connect(self._edit_label)
        self._formatter_ui.listWidget_xlabels_edit.itemDoubleClicked.connect(self._edit_label)
        self._formatter_ui.listWidget_ylabels_edit.itemDoubleClicked.connect(self._edit_label)
        
        self._formatter_ui.pushButton_xylabelfont.clicked.connect(self._set_xylabelfont)
        
        
    def _set_formatter(self):
        self._get_xticklabels()
        self._get_xylabels()
        self._formatter_ui.label_currentxylabelfont.setText(f"Current font: {self._xylabel_font}")
        
        
    def _edit_label(self, item):
        """
        Replaces the double-clicked label with given input.
        """
        new_text, okPressed = QtWidgets.QInputDialog.getText(self,"renaming...","Enter a new name")
        if okPressed and new_text != "":
            item.setText(new_text)
            self._update_editted_labels()
            
    def _set_xylabelfont(self):
        self._xylabel_font = self._select_font()
        self._formatter_ui.label_currentxylabelfont.setText(f"Current font: {self._xylabel_font}")
                   
    def _get_xticklabels(self):
        """
        Retrieves the xticklabels and parameters from the passed axes instance.
        """
        self._xtick_labels_orig = [x.get_text() for x in self.ax[0].get_xticklabels()]
        self._formatter_ui.listWidget_xticklabels_orig.addItems(self._xtick_labels_orig)
        if self._xtick_labels_edit == None:
            self._xtick_labels_edit = self._xtick_labels_orig
        self._formatter_ui.listWidget_xticklabels_edit.addItems(self._xtick_labels_edit)
        try:
            self._xticklabel_font = self.ax[0].get_xticklabels()[0].get_fontname()
        except:
            self._xticklabel_font = "DejaVu Sans"
    
    def _set_xticklabels(self):
        """
        Sets the userdefined xticklabels and parameters on the passed axes isntance
        """
        for ax in self.ax:
            ax.set_xticklabels(self._xtick_labels_edit, fontname = self._xticklabel_font)
    
    def _update_editted_labels(self):
        """
        Update all editted labels in the  gui
        """
        self._xtick_labels_edit = [self._formatter_ui.listWidget_xticklabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_xticklabels_edit.count())]
        self._xlabels_edit = [self._formatter_ui.listWidget_xlabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_xlabels_edit.count())]
        self._ylabels_edit = [self._formatter_ui.listWidget_ylabels_edit.item(i).text() for i in range(self._formatter_ui.listWidget_ylabels_edit.count())]
        
    
    def _get_xylabels(self):
        """
        Retrieves XY-labels and parameters frm the passed axes instance
        """
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
            
        self._xylabel_font = self.ax[0].xaxis.get_label().get_fontname()
        
    def _set_xylabels(self):
        """
        Sets the userdefined XY labels and parameters on teh passed axes instance
        """
        for ax, xlabel, ylabel in zip(self.ax, self._xlabels_edit, self._ylabels_edit):
            ax.set_xlabel(xlabel, fontname = self._xylabel_font)
            ax.set_ylabel(ylabel, fontname = self._xylabel_font)
    
    def _select_font(self):
        """
        Input Dialog to select an availabel matplotlib font for a label
        """
        import matplotlib.font_manager
        available_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        names = [x.split("/")[-1].rstrip(".ttf") for x in available_fonts]
        names.sort()
        font_name, okPressed = QtGui.QInputDialog.getItem(self, "Font", "Select a Font", names)
        if okPressed:
            return font_name
    
    def _apply_changes(self):
        """
        Set all user defined parameters on the passed axes instance
        """
        self._set_xticklabels()
        self._set_xylabels()

if __name__ == "__main__":
#    app = QtWidgets.QApplication([])
    
    iris = sns.load_dataset('iris')
    v = ViolinsPlot()
    v.set(iris, [x for x in iris.columns if "species" not in x], "species")
    m = MatplotFormatter(plot_object=v)
    m.show()
#    sys.exit(app.exec())