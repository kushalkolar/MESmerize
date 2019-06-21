import numpy as np
from . import cross_correlation
from . import tvregdiff
from . import sosd

modln = lambda x: np.sign(x) * np.log(np.abs(x))
modlog10 = lambda x: np.sign(x) * np.log(np.abs(x))
normalize = lambda a: ((a - np.min(a)) / (np.max(a - np.min(a))))
