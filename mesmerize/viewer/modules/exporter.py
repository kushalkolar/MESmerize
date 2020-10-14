import numpy as np
import numexpr
from tqdm import tqdm
from ...plotting.utils import auto_colormap
from ..core import ViewerUtils
from ...common.qdialogs import *
import os
import skvideo.io
from .pytemplates.exporter_pytemplate import *


# adapted from https://github.com/ver228/tierpsy-tracker/blob/master/tierpsy/analysis/compress/compressVideo.py
def normalize_image(img, imin, imax):
    factor = 255 / (imax - imin)

    imgN = numexpr.evaluate('(img-imin)*factor')
    imgN = imgN.astype(np.uint8)
    imgN[imgN == 255] = 254

    return imgN


class ModuleGUI(QtWidgets.QWidget):
    def __init__(self, parent, viewer_ref: ViewerUtils):
        QtWidgets.QWidget.__init__(self)
        self.viewer = viewer_ref

        self.ui = Ui_exporter_template()
        self.ui.setupUi(self)

        self.ui.sliderFPS_Scaling.valueChanged.connect(
            lambda v: self.ui.doubleSpinBox.setValue(v / 10)
        )

        self.ui.btnExport.clicked.connect(lambda: self.export())
        self.ui.listWidget.set_cmap('gnuplot2')
        self.ui.btnChoosePath.clicked.connect(
            lambda: self.set_path()
        )

        self.ui.lineEdPath.setToolTip(
            "Do not specify the extension, it is "
            "chosen automatically based on the codec"
        )

    @use_save_file_dialog('Choose path, DO NOT SPECIFY EXTENSION')
    def set_path(self, path, *args):
        if os.path.isfile(path):
            raise FileExistsError

        else:
            self.ui.lineEdPath.setText(path)

    @present_exceptions('Export Error')
    def export(self):
        if (self.viewer.workEnv.imgdata is None) or (self.viewer.workEnv.imgdata.seq is None):
            raise ValueError("No image data to export")

        codec = self.ui.comboBoxFormat.currentText()

        if codec in ['libx264']:
            extn = 'avi'
        elif codec in ['wmv2']:
            extn = 'wmv'

        fps_scaling = self.ui.doubleSpinBox.value()

        if self.ui.radioAuto.isChecked():
            vmin = np.nanmin(self.viewer.workEnv.imgdata.seq)
            vmax = np.nanmax(self.viewer.workEnv.imgdata.seq)

        else:
            vmin = self.viewer.levelMin
            vmax = self.viewer.levelMax

        cmap = self.ui.listWidget.get_cmap()

        path = self.ui.lineEdPath.text()
        if os.path.isfile(path):
            raise FileExistsError

        seq = self.viewer.workEnv.imgdata.seq

        print('Normalizing image for 8bit video output')
        norm = normalize_image(seq, vmin, vmax)

        # RGB LUT
        lut = np.zeros(shape=(256, 1, 3), dtype=np.uint8)

        cmap = np.vstack(auto_colormap(n_colors=256, cmap=cmap))

        lut[:, 0, :] = cmap[:, :-1] * 255

        orig_fps = self.viewer.workEnv.imgdata.meta['fps']

        r = int(orig_fps * fps_scaling)

        pts = orig_fps / float(r)

        output_params = \
            {
                '-r': str(r),
                '-filter:v': f"setpts={pts}*PTS",
                '-vcodec': codec
            }
        print("Creating ffmpeg writer")
        writer = skvideo.io.FFmpegWriter(f'{path}.{extn}', outputdict=output_params)

        print("Writing video")
        for i in tqdm(range(norm.shape[2])):
            frame = norm[:, :, i]
            # use the LUT to create RGB pseudocolored image
            writer.writeFrame(lut[frame][:, :, 0, :])
        writer.close()
