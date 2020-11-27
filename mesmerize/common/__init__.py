# @author: kushal

# Chatzigeorgiou Group
# Sars International Centre for Marine Molecular Biology

# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

import os
from webbrowser import open_new_tab as open_new_web_browser_tab
import configparser
from datetime import datetime
from time import time
from .configuration import get_sys_config, console_history_path
from functools import partial
from PyQt5.QtWidgets import QApplication
from abc import ABCMeta
from pathlib import Path


with open(Path(__file__).parent.parent.joinpath('VERSION'), 'r') as vf:
    __version__ = vf.read().split('\n')[0]


def get_proj_config(proj_path: str = None) -> configparser.RawConfigParser:
    """
    :param proj_path: Full project path
    """

    if proj_path is None:
        proj_path = get_project_manager().root_dir
        if proj_path is None:
            raise NoProjectOpen

    proj_cfg = configparser.RawConfigParser(allow_no_value=True)
    proj_cfg.optionxform = str
    proj_cfg.read(proj_path + '/config.cfg')
    return proj_cfg


docs_dir = f'https://docs.mesmerizelab.org/en/v{__version__}/'

doc_pages = \
    {
        'issue-tracker':    'https://github.com/kushalkolar/MESmerize/issues',
        'gitter':           'https://gitter.im/mesmerize_discussion/community'
    }

mesmerize_doc_pages = \
    {
        'home':             '',
        'new_project':      'user_guides/project_organization/new_project/new_project.html',
        'viewer':           'user_guides/viewer/overview.html',
        'faq':              'user_guides/faq.html',
        'sys_config':       'user_guides/general/misc.html#system-configuration'
    }

doc_pages.update(
    {k: docs_dir + v for k, v in mesmerize_doc_pages.items()}
)


for k in doc_pages.keys():
    doc_pages[k] = partial(open_new_web_browser_tab, doc_pages[k])


class InheritDocs(ABCMeta):
    """Inherit doc string from superclass if not present in subclass"""

    def __new__(mcls, classname, bases, cls_dict):
        cls = super().__new__(mcls, classname, bases, cls_dict)
        for name, member in cls_dict.items():
            if not getattr(member, '__doc__'):
                if hasattr(bases[-1], name):
                    member.__doc__ = getattr(bases[-1], name).__doc__
        return cls


def get_timestamp_str() -> str:
    date = datetime.fromtimestamp(time())
    time_str = date.strftime('%Y%m%d') + '_' + date.strftime('%H%M%S')
    return time_str


def is_app() -> bool:
    if QApplication.instance() is None:
        return False

    if hasattr(QApplication.instance(), 'window_manager') and hasattr(QApplication.instance(), 'project_manager'):
        return True

    return False


def get_project_manager():
    """Get the project manager for this Mesmerize instance"""
    if not is_app():
        raise NotInApplicationError

    pm = getattr(QApplication.instance(), 'project_manager')
    return pm


def set_project_manager(project_manager):
    if not is_app():
        raise NotInApplicationError

    setattr(QApplication.instance(), 'project_manager', project_manager)


def get_window_manager():
    """Get the Window Manager for this Mesmerize instance"""

    if not is_app():
        raise NotInApplicationError
    return getattr(QApplication.instance(), 'window_manager')
    # try:
    #     wm = getattr(QApplication.instance(), 'window_manager')
    # except AttributeError:
    #     raise AttributeError("This can only be used in a full Mesmerize Application")
    # return wm


def is_mesmerize_project(proj_dir: str) -> bool:
    if not os.path.isdir(proj_dir + '/dataframes'):
        raise NotAMesmerizeProject('dataframes directory not found')

    if not os.path.isdir(proj_dir + '/images'):
        raise NotAMesmerizeProject('images directory not found')

    return True


class NoProjectOpen(Exception):
    """No Mesmerize project is open."""


class NotInApplicationError(Exception):
    """This can only be used in a full Mesmerize Application"""


class NotAMesmerizeProject(Exception):
    """Not a valid Mesmerize Project"""

    def __init__(self, msg):
        assert isinstance(msg, str)
        self.msg = msg

    def __str__(self):
        return str(self.__doc__) + '\n' + self.msg
