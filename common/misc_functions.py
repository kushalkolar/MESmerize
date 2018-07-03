#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 27 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""


def floating_point_equality(m: float, n: float, epsilon: float) -> bool:
    return abs((m + 0.0) - (n + 0.0)) < epsilon
