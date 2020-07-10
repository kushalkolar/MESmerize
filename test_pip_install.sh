#!/bin/bash
rm -rf /share/python-virtual-environments/mesmerize-pip-testing &&
python3 -m venv /share/python-virtual-environments/mesmerize-pip-testing &&
source /share/python-virtual-environments/mesmerize-pip-testing &&
pip install --upgrade pip setuptools
pip install Cython numpy
pip install mesmerize --extra-index-url=https://test.pypi.org/simple/
which mesmerize

