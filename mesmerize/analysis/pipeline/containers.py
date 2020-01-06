#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Kushal Kolar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from fcsugar import Container
from .. import Transmission
import os
import pandas as pd


class TransmissionContainer(Transmission, Container):
    def __init__(self, *args, **kwargs):
        Transmission.__init__(self, *args, **kwargs)
        Container.__init__(self)

    @property
    def dataframe(self):
        proj_df_path = os.path.join(self.get_proj_path(), 'dataframes', 'root.dfr')
        proj_df = pd.read_hdf(proj_df_path, key='project_dataframe', mode='r')
        return pd.merge(proj_df, self.df, on='uuid_curve')

    def append_log(self, node):
        super(TransmissionContainer, self).append_log(node)
        self.history_trace.add_operation('all', node.name, node.params)

    def __add__(self, other):
        if not isinstance(other, TransmissionContainer):
            raise TypeError("Can only combine TransmissionContainers")

        return TransmissionContainer.merge([self, other])
