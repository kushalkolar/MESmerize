from fcsugar import *
from ..containers import TransmissionContainer
import numpy as np
from ...utils import pad_arrays as _pad_arrays


@node
def pad_arrays(container, data_column, method: str = 'random'):
    data = _pad_arrays(container.df[data_column].values, method=method)

    container.df['pad_arrays'] = data.tolist()
    container.df['pad_arrays'] = container.df['pad_arrays'].apply(np.array)

    return container


@node
def partition(container, n_partitions: int):
    size = container.df.index.size

    ixs = np.array(range(size))

    partitions = np.array_split(ixs, n_partitions)
    labels = np.empty(shape=(size,), dtype=np.int64)

    for label, p in enumerate(partitions):
        labels[p] = label

    container.df['partition'] = labels
    return container

# TODO: Create container for numpy arrays!
@node
def sample_partition(contrainer, data_column: str, labels_column: str) -> np.ndarray:
    partitions = contrainer.df[labels_column].unique()

    df = contrainer.df

    samples = []
    for p in partitions:
        s = df[data_column][df[labels_column] == p].sample(1).values[0]
        samples.append(s)

    samples = np.array(samples)

    return samples
