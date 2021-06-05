#!/bin/bash
set -ev
if [ "${TRAVIS_OS_NAME}" = "osx" ]; then 
    ln -s /usr/local/lib/python36/site-packages/numpy/core/include/numpy numpy && python -m pip install -q -r requirements.txt
fi