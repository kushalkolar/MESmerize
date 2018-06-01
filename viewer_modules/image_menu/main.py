#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on June 1 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

from .resize import ResizeDialogBox

class ImageMenu:
    def __init__(self, viewer_interface):
        self.vi = viewer_interface
    def resize(self):
        if not hasattr(self, 'resize_dialog'):
            self.resize_dialog = ResizeDialogBox(self.vi)
        self.resize_dialog.show()