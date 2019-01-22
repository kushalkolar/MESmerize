#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


from PyQt5 import QtCore, QtGui, QtWidgets
from .heatmap import Heatmap
from .control_widget import Ui_DockWidget
from pyqtgraphCore.imageview.ImageView import ImageView
from cv2 import imread
from glob import glob
from viewer.core.common import *
import numpy as np

import pandas as pd
import pickle
from scipy import signal


class HeatmapWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = Heatmap()

        self.vlayout.addWidget(self.plot_widget)
        self.setLayout(self.vlayout)

    def set_data(self, array: np.ndarray = None, dataframe: pd.DataFrame = None, data_column: str = None,
                 cmap: str = 'jet'):

        if array is not None:
            assert isinstance(array, np.ndarray)
            data = array

        elif dataframe is not None:
            assert isinstance(dataframe, pd.DataFrame)
            assert isinstance(data_column, str)
            self.dataframe = dataframe
            data = np.vstack(self.dataframe[data_column].values)

        else:
            raise TypeError('You must pass either a numpy array or dataframe as and argument')

        self.plot_widget.set(data, cmap=cmap)


class HeatmapViewerWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = Heatmap()

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.addWidget(self.plot_widget)
        self.image_view = ImageView()
        self.splitter.addWidget(self.image_view)

        self.vlayout.addWidget(self.splitter)
        self.setLayout(self.vlayout)

        self.plot_widget.signal_row_selection_changed.connect(self.set_viewer)

        self.vi = ViewerInterface(self.image_view)

        self.dataframe = None

    def set_viewer(self, ix: int):
        pik_path = '/home/kushal/Sars_stuff/palp_project_mesmerize/' + self.dataframe.iloc[ix]['ImgInfoPath']
        tiff_path = '/home/kushal/Sars_stuff/palp_project_mesmerize/' + self.dataframe.iloc[ix]['ImgPath']
        self.vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=pik_path, tiff_path=tiff_path)
        self.vi.update_workEnv()
        #self.vi.viewer.workEnv.restore_rois_from_states()
        self.vi.viewer.ui.label_curr_img_seq_name.setText(self.dataframe.iloc[ix]['SampleID'])

    def set_data(self, dataframe: pd.DataFrame = None, data_column: str = None, cmap: str ='jet'):
        self.dataframe = dataframe
        data = np.vstack(self.dataframe[data_column].values)
        self.plot_widget.set(data, cmap=cmap)


class HeatmapControlWidget(QtWidgets.QDockWidget):
    signal_colormap_changed = QtCore.pyqtSignal(str)

    def __init__(self):
        QtWidgets.QDockWidget.__init__(self)
        self.ui = Ui_DockWidget()
        self.ui.setupUi(self)

        self.populate_colormaps()
        self.ui.listWidgetColorMaps.itemClicked.connect(self.emit_colormap_changed)

    def emit_colormap_changed(self, item: QtWidgets.QListWidgetItem):
        self.signal_colormap_changed.emit(item.text())

    def populate_colormaps(self):
        for path in glob('/home/kushal/MESmerize/plotter/modules/heatmap/colormaps/*.png'):
            img = QtGui.QIcon(path)
            item = QtWidgets.QListWidgetItem(path.split('/')[-1][:-4])
            item.setIcon(img)
            self.ui.listWidgetColorMaps.addItem(item)
        self.ui.listWidgetColorMaps.setIconSize(QtCore.QSize(100,50))

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = HeatmapWidget()
    # # df = pickle.load(open('/home/kushal/Sars_stuff/palp_project_mesmerize/oct_31_all_data.trn', 'rb'))['df']
    # # df = df[~df['comments'].str.contains('poking')]
    # # odor_df_f = []
    # # for i in range(df.index.size):
    # #     odor_df_f.append(
    # #         df.iloc[i]['curve'] / df.iloc[i]['curve'][:int(df.iloc[i]['meta']['fps'] * 4)].mean())
    # # df['df_f'] = odor_df_f
    # #
    # #
    # # duration = []
    # # for i in range(df.index.size):
    # #     duration.append(df.iloc[i]['df_f'].shape[0] / df.iloc[i]['meta']['fps'])
    # # df['duration'] = duration
    # # nh4_df = df[df.odor.apply(lambda x: 'NH4 100mM' in x)]
    # # nh4_df = nh4_df.iloc[5:]
    # # nh4_df = nh4_df[nh4_df['duration'] < 60]
    # # nh4_curves = nh4_df.curve.values
    # # data = []
    # # for c in nh4_curves:
    # #     data.append(resample(c, 2000))
    #
    # tr = pickle.load(open('/home/kushal/Sars_stuff/palp_project_mesmerize/oct_31_all_data.trn', 'rb'))
    # df = tr['df']
    # odor_df = df[~df['comments'].str.contains('poking')]
    # odor_df_f = []
    # for i in range(odor_df.index.size):
    #     odor_df_f.append(
    #         odor_df.iloc[i]['curve'] / odor_df.iloc[i]['curve'][:int(odor_df.iloc[i]['meta']['fps'] * 4)].mean())
    #
    # odor_df['df_f'] = odor_df_f
    # duration = []
    # for i in range(odor_df.index.size):
    #     duration.append(odor_df.iloc[i]['df_f'].shape[0] / odor_df.iloc[i]['meta']['fps'])
    # odor_df['duration'] = duration
    #
    # nh4_df = odor_df[odor_df['odor'].apply(lambda x: 'NH4 100mM' in x)]
    # nh4_df = nh4_df[nh4_df['duration'] < 60]
    # fps = []
    # for i in range(nh4_df.index.size):
    #     fps.append(nh4_df.iloc[i]['meta']['fps'])
    # nh4_df['fps'] = fps
    # resampled_nh4 = []
    # for i in range(nh4_df.index.size):
    #     resampled_nh4.append(signal.resample(nh4_df.iloc[i]['df_f'], 2000))
    #
    # resampled_nh4_array = np.array(resampled_nh4)
    # npy = resampled_nh4_array[:, :1000]
    # npy = np.delete(npy, 21, axis=0)
    # normalized = (npy - np.min(npy, axis=1)[:, np.newaxis]) / np.ptp(npy, axis=1)[:, np.newaxis]
    # nh4_df.drop(index=21, inplace=True)
    #
    # nh4_df['nordmalized'] = normalized
    #
    # nh4_df.to_pickle('/home/kushal/MESmerize/plotter/modules/heatmap/normalized_df.pik')

    #data = np.array(normalized)

    w.plot_widget.set(data, cmap='jet')
    #w.plot_widget.add_stimulus_indicator(144, 288, 'k')

    c = HeatmapControlWidget()
    c.show()

    c.signal_colormap_changed.connect(lambda m: w.plot_widget.set(data, cmap=m))

    w.show()
    app.exec()
