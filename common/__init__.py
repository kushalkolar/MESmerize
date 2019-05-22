import os
from webbrowser import open_new_tab
from functools import partial

docs_dir = os.path.dirname(os.path.dirname(__file__)) + '/docs'
docs_dir = docs_dir + '/user_guides'

doc_pages = {'home':            '/../index.html',
             'new_project':     '/project_organization/new_project/new_project.html',
             'viewer':          '/viewer/viewer.html',
             'faq':             '/faq.html'
             }

for k in doc_pages.keys():
    doc_pages[k] = partial(open_new_tab, docs_dir + doc_pages[k])
