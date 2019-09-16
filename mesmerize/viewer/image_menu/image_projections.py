# from ...pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ...pyqtgraphCore.imageview import ImageView
import numpy as np


def display_projection(projection: str, imgseq: np.ndarray, img_name: str):
    # Due to weird importing you must do this, not a big deal
    iv = ImageView.ImageView()
    # ax = mw.fig.add_subplot(111)

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

    # ax.set_title(t)
    iv.setImage(p.T)
    iv.ui.label_curr_img_seq_name.setText(t)
    iv.setWindowTitle(t)
    # ax.imshow(p.T)

    iv.show()
    return iv
