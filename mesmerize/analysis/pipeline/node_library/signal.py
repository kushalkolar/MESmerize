#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019 Kushal Kolar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from fcsugar import *
import numpy as np
from scipy import signal as scipy_signal
from ..containers import TransmissionContainer


@node
def sort_peak_widths(container: TransmissionContainer, data_column: str):
    peaks = container.df[data_column]
    widths = [scipy_signal.peak_widths(p, [np.argmax(p)])[0][0] for p in peaks]

    width_sorter = np.argsort(widths)

    container.df = container.df.reindex(index=width_sorter).reset_index(drop=True)

    return container
