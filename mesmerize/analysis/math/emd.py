#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

import numpy as np
from cv2 import EMD, DIST_L2


def emd_1d(u: np.ndarray, v: np.ndarray) -> float:
    """
    Wrapper around OpenCV Earth Mover's Distance (EMD) function to calculate EMD between 1D arrays

    :param u: an array of weights
    :param v: an array of weights
    :return: Earth Mover's Distance between u & v
    """

    a = np.empty((u.size, 2), dtype=np.float32)
    b = np.empty((v.size, 2), dtype=np.float32)

    a[:, 0] = u.astype(np.float32)
    a[:, 1] = np.arange(u.size, dtype=np.float32)

    b[:, 0] = v.astype(np.float32)
    b[:, 1] = np.arange(v.size, dtype=np.float32)

    return EMD(a, b, DIST_L2)[0]
