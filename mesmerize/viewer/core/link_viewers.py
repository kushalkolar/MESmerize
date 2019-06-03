#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 26 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .link_viewers_dialog_pytemplate import *
from ...common import configuration
from ...pyqtgraphCore.imageview import ImageView


class ViewerLinkages(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.linkages = {'source': None, 'receivers': list()}

        self.ui.btnSet.clicked.connect(self.slot_set)
        self.ui.btnDisconnect.clicked.connect(self.disconnect_all)

        self.ui.listWidgetReceivers.addItems(['0', '1', '2', '3', '4'])

    def populate_list_widgets(self):
        self.ui.listWidgetReceivers.clear()
        self.ui.listWidgetSource.clear()

        self.ui.listWidgetReceivers.addItems(list(range(len(configuration.window_manager.viewers))))
        self.ui.listWidgetSource.addItems(list(range(len(configuration.window_manager.viewers))))

    def disconnect_all(self):
        source = self.linkages['source']
        if source is None:
            return
        assert isinstance(source, ImageView)
        for receiver in self.linkages['receivers']:
            assert isinstance(receiver, ImageView)
            source.sigTimeChanged.disconnect(receiver.setCurrentIndex)

        self.linkages = {'source': None, 'receivers': list()}

    def slot_set(self):
        self.disconnect_all()
        src_ix = self.ui.listWidgetSource.currentRow()
        self.ui.listWidgetSource.currentItem().setBackground(QtGui.QBrush(QtGui.QColor('yellow')))
        source = configuration.window_manager.viewers[src_ix]

        self.linkages['source'] = source

        for item in self.ui.listWidgetReceivers.items():
            item.setBackground(QtGui.QBrush(QtGui.QColor('yellow')))

        qmodel_ixs = self.ui.listWidgetReceivers.selectedIndexes()
        receiver_ixs = [ix.row() for ix in qmodel_ixs]

        self.linkages['receivers'] = [configuration.window_manager.viewers[ix] for ix in receiver_ixs]

        self.connect_receivers(self.linkages['source'], self.linkages['receivers'])

    def connect_receivers(self, source: ImageView, receivers: list):
        for receiver in receivers:
            assert isinstance(receiver, ImageView)
            source.sigTimeChanged.connect(receiver.setCurrentIndex)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = ViewerLinkages()
    w.show()
    app.exec_()