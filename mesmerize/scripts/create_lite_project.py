#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

A back-end module for managing most project related functions, such as the root dataframe and all children,
adding rows to the root dataframe, updating child dataframes, and updating the project configuration.
"""

from shutil import copy2
from glob import glob
from os import makedirs


def main(proj_dir: str, dest_dir: str):
    print(proj_dir, dest_dir)
