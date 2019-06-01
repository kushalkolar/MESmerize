import os
from webbrowser import open_new_tab
from functools import partial
import configparser


def get_sys_config() -> configparser.RawConfigParser:
    sys_cfg_path = os.environ['HOME'] + '/.mesmerize'
    sys_cfg_file = sys_cfg_path + '/config'
    sys_cfg = configparser.RawConfigParser(allow_no_value=True)
    sys_cfg.optionxform = str
    sys_cfg.read(sys_cfg_file)
    return sys_cfg


def get_proj_config(proj_path: str = None) -> configparser.RawConfigParser:
    if proj_path is None:
        proj_path = os.environ['_mesmerize_proj_path']
    proj_cfg = configparser.RawConfigParser(allow_no_value=True)
    proj_cfg.optionxform = str
    proj_cfg.read(proj_path + '/config.cfg')
    return proj_cfg

docs_dir = os.path.dirname(os.path.dirname(__file__)) + '/docs'
docs_dir = docs_dir + '/user_guides'

doc_pages = {'home':            '/../index.html',
             'new_project':     '/project_organization/new_project/new_project.html',
             'viewer':          '/viewer/viewer.html',
             'faq':             '/faq.html'
             }

for k in doc_pages.keys():
    doc_pages[k] = partial(open_new_tab, docs_dir + doc_pages[k])

