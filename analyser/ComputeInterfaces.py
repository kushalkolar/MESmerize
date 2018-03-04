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


class Interface:
    def __init__(self, compute_class, args_dict):
        self.funcs = [f for f in compute_class.__dict__.items() if callable(f)]
        self.args_dict = args_dict
        self.Q = Queue()

    def run(self):
        for func in self.funcs:
            if func[0] not in self.args_dict.keys():
                continue

            a = tuple([self.Q] + self.args_dict[func[0]])
            proc = Process(target=func[1], args=a)
            proc.start()
            proc.join()

    def get_results(self):
        return self.Q.get()


class Static(Interface):
    def __init__(self, compute_class, args_dict):
        Interface.__init__(self, compute_class, args_dict)
        self.funcs = [f for f in compute_class.__dict__.items() if type(f[1]) == staticmethod]

