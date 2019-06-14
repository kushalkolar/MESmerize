#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 2 2017

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from multiprocessing import Process, Queue as Q_p
from threading import Thread
from queue import Queue as Q_t
from functools import partial
import abc


class Interface(metaclass=abc.ABCMeta):
    def __init__(self, compute_class, args_dict: dict):
        self.compute_class = compute_class
        self.args_dict = args_dict
        self.func_names = [f for f in self.args_dict.keys() if hasattr(self.compute_class, f)]
        self.funcs = None
        self.Q = None

    @abc.abstractmethod
    def compute(self) -> dict:
        pass

    def get_results(self) -> dict:
        if self.Q is None:
            raise Exception('You must run the compute method first')

        l = dict()
        while self.Q.qsize() > 0:
            l.update(self.Q.get())
        return l


class Static(Interface):
    def compute(self):
        self.Q = {}
        for func in self.func_names:
            f = getattr(self.compute_class, func)
            a = tuple([self.Q] + self.args_dict[func])
            print(callable(getattr(self.compute_class, func)))
            # self.Q.update(result)

    def get_results(self):
        return self.Q


class StaticMP(Interface):
    def compute(self):
        self.Q = Q_p()
        for func in self.func_names:
            f = getattr(self.compute_class, func)
            a = tuple([self.Q] + self.args_dict[func])
            proc = Process(target=f, args=a)
            proc.start()
            proc.join()
        return self.get_results()


class StaticMT(Interface):
    def compute(self):
        self.Q = Q_t()
        for func in self.func_names:
            f = getattr(self.compute_class, func)
            a = tuple([self.Q] + self.args_dict[func])
            thread = Thread(target=f, args=a)
            thread.start()
            thread.join()
        return self.get_results()
