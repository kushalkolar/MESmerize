# -*- coding: utf-8 -*-
from ...Qt import QtWidgets
# from . import functions
from .common import *
from ....plotting.widgets import CurvePlotWindow
# from analysis import pca_gui


class CurvePlotsNode(CtrlNode):
    """Curve plots"""
    nodeName = 'CurvePlots'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
                  ('ShowGUI', 'button', {'text': 'OpenGUI'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
        self.plot_gui = None
        self.ctrls['ShowGUI'].clicked.connect(self._open_plot_gui)

    def process(self, **kwargs):
        if (self.ctrls['Apply'].isChecked() is False) or self.plot_gui is None:
            return

        transmissions = kwargs['In']

        if not len(transmissions) > 0:
            raise Exception('No incoming transmissions')

        transmissions_list = []

        for t in transmissions.items():
            t = t[1]
            if t is None:
                QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
                continue

            transmissions_list.append(t.copy())

        self.plot_gui.update_input_transmissions(transmissions_list)

    def _open_plot_gui(self):
        if self.plot_gui is None:
            self.plot_gui = CurvePlotWindow(parent=self.parent())
        self.plot_gui.show()

# class PCA(CtrlNode):
#     """PCA (Principal component analysis)"""
#     nodeName = 'PCA'
#     uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True}),
#                   ('ShowGUI', 'button', {'text': 'OpenGUI'})]
#
#     def __init__(self, name):
#         CtrlNode.__init__(self, name, terminals={'In': {'io': 'in', 'multi': True}})
#         self.ctrls['ShowGUI'].clicked.connect(self._open_pca_gui)
#
#     def process(self, **kwargs):
#         if (self.ctrls['Apply'].isChecked() is False) or not hasattr(self, 'pca_gui'):
#             return
#
#         transmissions = kwargs['In']
#
#         if not len(transmissions) > 0:
#             raise Exception('No incoming transmissions')
#
#         transmissions_list = []
#
#         for t in transmissions.items():
#             t = t[1]
#             if t is None:
#                 QtWidgets.QMessageBox.warning(None, 'None transmission', 'One of your transmissions is None')
#                 continue
#
#             if not any('Power Spectral Density' in d for d in t.src):
#                 raise KeyError('Cannot perform PCA with incoming transmissions. '
#                                'You must pass through one of the following nodes before performing a PCA:\n'
#                                'Power Spectral Density')
#
#             transmissions_list.append(t.copy())
#
#         self.pca_gui.update_input(transmissions_list)
#
#     def _open_pca_gui(self):
#         if hasattr(self, 'pca_gui'):
#             self.pca_gui.show()
#             return
#
#         self.pca_gui = pca_gui.PCA_GUI()
#         self.pca_gui.show()
#         self.changed()
