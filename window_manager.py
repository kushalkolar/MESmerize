#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 14 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""


class WindowManager:
    def __init__(self):
        self.project_browsers = []
        self.viewers = []
        self.flowcharts = []
        self.plots = []
        self.clustering_windows = []

    def garbage_collect(self):
        pass

    def garbage_collect_all_closed_windows(self):
        pass
