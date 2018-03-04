#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from multiprocessing import Process, Queue


class Static:
    def __init__(self, compute_class, args_dict):
        self.compute_class = compute_class
        self.args_dict = args_dict
        self.func_names = [f for f in self.args_dict.keys() if hasattr(self.compute_class, f)]
        self.Q = Queue()

    def run(self):
        for func in self.func_names:
            f = getattr(self.compute_class, func)
            a = tuple([self.Q] + self.args_dict[func])
            proc = Process(target=f, args=a)
            proc.start()
            proc.join()

    def get_results(self):
        return self.Q.get()

