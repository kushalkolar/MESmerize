"""
Pandas extensions for working with Batch Manager data
"""

import pandas as pd
import pathlib
from ..common import configuration
from typing import *
from uuid import UUID
import pickle
if configuration.HAS_CAIMAN:
    import caiman as cm

CURRENT_BATCH: pathlib.Path = None  # only one batch at a time for now


def load_batch(path: Union[str, pathlib.Path]) -> pd.DataFrame:
    global CURRENT_BATCH

    df = pd.read_pickle(
        pathlib.Path(path).joinpath('/dataframe.batch')
    )

    CURRENT_BATCH = pathlib.Path(path)

    return df


def _get_item_uuid(item: Union[int, str, UUID]) -> UUID:
    pass


@pd.api.extensions.register_series_accessor("caiman")
class CaimanExtensions:
    """
    Extensions for caiman related functions
    """
    def __init__(self, series: pd.Series):
        if not configuration.HAS_CAIMAN:
            raise ImportError("Caiman not found in the environment")

        self._series = series

    def get_params(self) -> dict:
        params_path = \
            CURRENT_BATCH.joinpath(
                f"{self._series.uuid}.params"
            )

        return pickle.load(open(params_path, 'rb'))

    def get_mc_movie_path(self) -> pathlib.Path:
        if not self._series['module'] == 'caiman_motion_correction':
            raise TypeError("Not a motion correction batch item.")

        path = CURRENT_BATCH.joinpath(f"{self._series.uuid}_mc.tiff")

        if not path.is_file():
            raise FileNotFoundError("Motion corrected movie not found for this batch item.")

        return path

    def get_mc_movie(self):
        path = self.get_mc_movie_path()

        return cm.load_movie_chain([str(path)])

    def get_mc_eval_metrics(
            self,
            winsize: int = 100,
            swap_dim: bool = False,
            play_flow: bool = False,
            resize_fact_flow: float = 0.2
    ) -> dict:
        gSig_filt = self.get_params()['mc_kwargs']['gSig_filt']

        dims = self.get_mc_movie().shape[1:]

        template_metric, \
        correlations_metric, \
        flows_metric, \
        norms_metric, \
        crispness_metric = \
            cm.motion_correction.compute_metrics_motion_correction(
                self.get_mc_movie_path(),
                dims[0],
                dims[1],
                swap_dim,
                winsize=winsize,
                play_flow=play_flow,
                resize_fact_flow=resize_fact_flow,
                gSig_filt=gSig_filt
            )

        return \
            {
                "template_metric": template_metric,
                "correlations_metric": correlations_metric,
                "flows_metric": flows_metric,
                "norms_metric": norms_metric,
                "crispness_metric": crispness_metric
            }