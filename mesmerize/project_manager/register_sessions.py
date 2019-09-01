import numpy as np
from typing import *
from caiman.base.rois import register_multisession
from ..common import get_project_manager
import pickle
import os
import tifffile


def assign_component_ids(assignments: np.ndarray) -> List[Dict[int, int]]:#, idx_components_sessions: List[np.ndarray]):
    """
    Returns a list of dicts to map component indices from a session to a cell ID.
    list index is session number.
    :param assignments:
    """
    mappings = [dict()] * assignments.shape[1]
    for cell_id in assignments.shape[0]:
        for session in assignments.shape[1]:
            idx_component = assignments[cell_id, session]
            mappings[session][idx_component] = cell_id

    return mappings


def register_animal(animal_id: str, session_column: str):
    df = get_project_manager().dataframe
    animal_df = df[df.SampleID.apply(lambda sid: sid.split('-_-')[0] == animal_id)]
    animal_df = animal_df.copy()

    animal_df.drop_duplicates(subset=session_column, keep='first', inplace=True)

    animal_df.sort_values(by=[session_column], inplace=True).reset_index(drop=True)

    data_paths = [os.path.join(get_project_manager().root_dir, path) for path in animal_df.ImgInfoPath.tolist()]


def register_sessions(data_paths: List[str]) -> np.ndarray:
    """

    :param data_paths:
    :return: assignments array
    """
    As = []
    templates = []

    for path in data_paths:
        p = pickle.load(open(path, 'rb'))
        As.append(p['roi_states']['cnmf_output']['cnmA'])


