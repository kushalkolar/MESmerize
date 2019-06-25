import numpy as np
from . import cross_correlation
from . import tvregdiff
from . import sosd


def modln(x): return np.sign(x) * np.log(np.abs(x))
def modlog10(x): np.sign(x) * np.log10(np.abs(x))
def normalize(a): return ((a - np.min(a)) / (np.max(a - np.min(a))))
