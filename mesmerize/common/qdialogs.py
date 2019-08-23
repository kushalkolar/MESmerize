#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#@author: kushal

#Chatzigeorgiou Group
#Sars International Centre for Marine Molecular Biology

#GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

from PyQt5.QtWidgets import QMessageBox, QFileDialog
import traceback
from functools import wraps
from . import get_project_manager
from typing import *


"""
Decorators for frequent Qt Dialog GUIs
"""


def present_exceptions(title: str = 'error', msg: str = 'The following error occurred.', help_func: callable = None):
    """
    Use to catch exceptions and present them to the user in a QMessageBox warning dialog.
    The traceback from the exception is also shown.

    :param title:       Title of the dialog box
    :param msg:         Message to display above the traceback in the dialog box
    :param help_func:   A helper function which is called if the user clicked the "Help" button
    """
    def catcher(func):
        @wraps(func)
        def fn(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                args = (self, title, msg + f'\n\n{e.__class__.__name__}: {e}\n\n{tb}', QMessageBox.Ok)
                if help_func is not None and QMessageBox.warning(*args, QMessageBox.Help) == QMessageBox.Help:
                    help_func(e, tb)
                else:
                    QMessageBox.warning(*args)
        return fn
    return catcher


def _get_start_dir(start_dir) -> str:
    if start_dir is not None:
        return start_dir
    try:
        d = get_project_manager().root_dir
    except:
        return ''
    else:
        if d is None:
            return ''
        else:
            return d


def use_open_file_dialog(title: str = 'Choose file', start_dir: Union[str, None] = None, exts: List[str] = None):
    """
    Use to pass a file path, for opening, into the decorated function using QFileDialog.getOpenFileName

    :param title:       Title of the dialog box
    :param start_dir:   Directory that is first shown in the dialog box.
    :param exts:        List of file extensions to set the filter in the dialog box
    """
    def wrapper(func):
        @wraps(func)
        def fn(self, *args, **kwargs):
            if exts is None:
                e = []
            else:
                e = exts
            path = QFileDialog.getOpenFileName(self, title, _get_start_dir(start_dir), f'({" ".join(e)})')
            if not path[0]:
                return
            path = path[0]
            func(self, path, *args, **kwargs)
        return fn
    return wrapper


def use_save_file_dialog(title: str = 'Save file', start_dir: Union[str, None] = None, ext: str = None):
    """
    Use to pass a file path, for saving, into the decorated function using QFileDialog.getSaveFileName

    :param title:       Title of the dialog box
    :param start_dir:   Directory that is first shown in the dialog box.
    :param exts:        List of file extensions to set the filter in the dialog box
    """
    def wrapper(func):
        @wraps(func)
        def fn(self, *args, **kwargs):
            if ext is None:
                raise ValueError('Must specify extension')
            if ext.startswith('*'):
                ex = ext[1:]
            else:
                ex = ext
            path = QFileDialog.getSaveFileName(self, title, _get_start_dir(start_dir), f'(*{ex})')
            if not path[0]:
                return
            path = path[0]
            if not path.endswith(ex):
                path = f'{path}{ex}'

            func(self, path, *args, **kwargs)

        return fn
    return wrapper


def use_open_dir_dialog(title: str = 'Open directory', start_dir: Union[str, None] = None):
    """
    Use to pass a dir path, to open, into the decorated function using QFileDialog.getExistingDirectory

    :param title:       Title of the dialog box
    :param start_dir:   Directory that is first shown in the dialog box.
    """
    def wrapper(func):
        @wraps(func)
        def fn(self, *args, **kwargs):
            path = QFileDialog.getExistingDirectory(self, title, _get_start_dir(start_dir))
            if not path:
                return
            func(self, path, *args, **kwargs)
        return fn
    return wrapper


