import isx
import numpy as np
import click
from multiprocessing import shared_memory
from tqdm import tqdm


@click.command()
@click.option('--isx-path', type=str)
@click.option('--shm-meta-array-name', type=str)
def load_file(isx_path, shm_meta_array_name):#shm_name, shm-size, shm-dtype):
    """
    isx_path: full path to the isx file to open
    shm_meta_array_name: same of the shared memory array that is used to pass
    array metadata (shape, dtype, name) to effectively communication with the
    parent mesmerize instance

    shm-name: name of the parent shared array that contains the 

    """
    movie = isx.Movie.read(isx_path)

    meta = movie.get_acquisition_info()

    d = \
        {
            'fps': 1000 / movie.timing.period.to_msecs(),
            'origin': meta['Microscope Type'],
            'date': '00000000_000000',
            'orig_meta': meta
        }
    
    # total number of frames in the recording
    nframes = movie.timing.num_samples

    # shape of each frame
    frame0 = movie.get_frame_data(0)
    
    # image shape
    shape = (*frame0.shape, nframes)

    # calculate number of bytes required for the shared memory
    nbytes = np.prod(shape) * np.dtype(movie.data_type).itemsize

    # created a shared memory buffer
    shm = shared_memory.SharedMemory(create=True, size=nbytes)

    # create shared numpy array backed by the shared memory buffer
    imgseq = np.ndarray(shape, dtype=np.dtype(movie.data_type), buffer=shm.buf)
    
    # fill the array with the inscopix data
    for i in tqdm(range(nframes)):
        imgseq[..., i] = movie.get_frame_data(i)

    # communicate the array metadata to access the shared array from within mesmerize
    shm_metadata = shared_memory.SharedMemory(name=shm_meta_array_name)
    array_metadata = np.ndarray((5,), dtype=np.dtype('<U64'), buffer=shm_metadata.buf)

    array_metadata[0] = shm.name
    array_metadata[1] = np.dtype(movie.data_type).name
    array_metadata[2] = ','.join(str(s) for s in shape)
    array_metadata[3] = str(d['fps'])
    array_metadata[4] = str(d['origin'])
    
    print(f'imgdata address: {shm.name}')
    print(array_metadata)

    shm.close()


if __name__ == '__main__':
    load_file()


