from pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np


def display_projection(projection: str, imgseq: np.ndarray, img_name: str):
    mw = MatplotlibWidget()
    ax = mw.fig.add_subplot(111)

    if projection == 'mean':
        t = 'Mean Projection of : ' + img_name
        p = imgseq.mean(axis=2)

    elif projection == 'max':
        t = 'Max Projection of : ' + img_name
        p = imgseq.max(axis=2)

    elif projection == 'std':
        t = 'Std. Deviation projection of : ' + img_name
        p = imgseq.std(axis=2)

    else:
        raise ValueError('Invalid projection type, only accepts "mean", "max", or "std"')

    ax.set_title(t)
    mw.setWindowTitle(t)
    ax.imshow(p.T)

    mw.show()
    return mw