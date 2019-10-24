#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
import pandas as pd
from string import ascii_uppercase
from math import sqrt
from pomegranate.MarkovChain import MarkovChain
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
from . import Transmission, pad_arrays
from ..common.utils import make_workdir