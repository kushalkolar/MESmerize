import os
from webbrowser import open_new_tab as open_new_web_browser_tab
import configparser
from datetime import datetime
from time import time
from .. import docs
from .configuration import get_sys_config
from functools import partial
from PyQt5.QtWidgets import QApplication


# def get_sys_config() -> configparser.RawConfigParser:
#     sys_cfg_file = os.environ['HOME'] + '/.mesmerize'
#     sys_cfg_file = sys_cfg_file + '/config'
#     sys_cfg = configparser.RawConfigParser(allow_no_value=True)
#     sys_cfg.optionxform = str
#     sys_cfg.read(sys_cfg_file)
#     return sys_cfg


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


docs_dir = os.path.dirname(docs.__file__)
docs_dir = docs_dir + '/user_guides'

doc_pages = {'home':            '/../index.html',
             'new_project':     '/project_organization/new_project/new_project.html',
             'viewer':          '/viewer/viewer.html',
             'faq':             '/faq.html'
             }

for k in doc_pages.keys():
    doc_pages[k] = partial(open_new_web_browser_tab, docs_dir + doc_pages[k])


def get_timestamp_str() -> str:
    date = datetime.fromtimestamp(time())
    time_str = date.strftime('%Y%m%d') + '_' + date.strftime('%H%M%S')
    return time_str


def is_app() -> bool:
    if hasattr(QApplication.instance(), 'window_manager') and hasattr(QApplication.instance(), 'project_manager'):
        return True
    return False


def get_project_manager():
    if not is_app():
        raise NotInApplicationError

    pm = getattr(QApplication.instance(), 'project_manager')
    return pm


def set_project_manager(project_manager):
    if not is_app():
        raise NotInApplicationError

    setattr(QApplication.instance(), 'project_manager', project_manager)


def get_window_manager():
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

    if not os.path.isdir(proj_dir + '/curves'):
        raise NotAMesmerizeProject('curves directory not found')

    return True


class NoProjectOpen(BaseException):
    """No Mesmerize project is open."""


class NotInApplicationError(BaseException):
    """This can only be used in a full Mesmerize Application"""


class NotAMesmerizeProject(BaseException):
    """Not a valid Mesmerize Project"""

    def __init__(self, msg):
        assert isinstance(msg, str)
        self.msg = msg

    def __str__(self):
        return str(self.__doc__) + '\n' + self.msg