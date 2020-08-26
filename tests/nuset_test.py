from mesmerize.viewer.modules.nuset_segment import *
import tifffile
from glob import glob
from re import sub as regex_sub
from tqdm import tqdm


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    fnames = glob('/home/kushal/Sars_stuff/zfish_stds/*.tiff')

    fnames.sort(
        key=lambda name: int(
            regex_sub(r"[^0-9]*", '', name)
        )
    )

    # img = tifffile.imread('/home/kushal/Sars_stuff/zfish_stds/5.tiff')

    imgs = [tifffile.imread(f) for f in tqdm(fnames)]

    w = ModuleGUI(None, None)
    w.show()

    w.widget.imgs_projected = imgs
    w.widget.z_max = len(imgs)
    w.widget.zslider.setMaximum(w.widget.z_max)
    w.widget.spinbox_zlevel.setMaximum(w.widget.z_max)
    w.widget.imgitem_raw.setImage(imgs[0])

    # w.imgitem_raw.setImage(img)
    # w.image_projection = img

    app.exec_()
