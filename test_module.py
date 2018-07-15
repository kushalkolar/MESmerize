#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

# from analyser.plot_window.beeswarms_window import *
from analyser.plot_window.curve_plots_window import *
from analyser.DataTypes import Transmission

# data = np.random.normal(size=(4,20))
# data[0] += 5
# data[1] += 7
# data[2] += 5
# data[3] = 10 + data[3] * 2
# df = pd.DataFrame(data.T, columns=['a', 'b', 'c', 'd'])
# uuids = [uuid4() for i in range(20)]
# dfuuid = pd.DataFrame(uuids, columns=['uuid'])
# df = pd.concat([df, dfuuid], axis=1)

#
# app = QtWidgets.QApplication([])
# bpw = BeeswarmPlotWindow()
# ts = [Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/methods_paper_transmissions/for_methods_paper_pc2_pfeatures.trn'),
#  Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/methods_paper_transmissions/for_methods_paper_eef1a_pfeatures.trn')]
# bpw.update_input_transmissions(ts)
# # bpw.plot_obj.add_plot('bah_title')
# # bpw.plot_obj.set_plot_data(0, df, ['a', 'b', 'c'])
# bpw.show()
# app.exec_()

app = QtWidgets.QApplication([])
bpw = CurvePlotWindow()
ts = [Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/methods_paper_transmissions/for_methods_paper_pc2_pfeatures.trn'),
 Transmission.from_pickle('/home/kushal/Sars_stuff/github-repos/methods_paper_transmissions/for_methods_paper_eef1a_pfeatures.trn')]
bpw.update_input_transmissions(ts)
# bpw.plot_obj.add_plot('bah_title')
# bpw.plot_obj.set_plot_data(0, df, ['a', 'b', 'c'])
bpw.show()
app.exec_()