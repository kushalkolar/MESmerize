import cv2
import numpy as np
from .common import BitDepthConverter
from typing import Tuple, Union, Any, List


def get_rect(seq: np.ndarray,
              projection: str,
              method: str,
              denoise: str = 'blur',
              denoise_params: tuple = (16, 16),
              thresh: tuple = (50, 255),
              padding: int = 30) -> Tuple[bool, List[Tuple[Union[object, Any], Union[object, Any]]]]:
    """

    :param seq:             image sequence
    :param projection:      'max', 'std', or 'max+std'
    :param method:          'threshold', 'spectral_saliency', or 'fine_grained_saliency'
    :param denoise:         'blur', 'NlMeans', or 'none'
    :param denoise_params:  params passed to cv2.blur or cv2.fastNlMeansDenoising
    :param thresh:          thresholds for binary image from which to get contours and rect
    :param padding:         number of pixels by which to increase boundaries of returned rectangle
    :return:                [(x1, y1), (x2, y2)]
    """

    if projection == 'max':
        img = seq.max(axis=2)
    elif projection == 'std':
        img = seq.std(axis=2)
    elif projection == 'max+std':
        img = seq.max(axis=2) + seq.std(axis=2)
    else:
        raise ValueError('Invalid projection argument: ' + str(projection))

    if img.dtype != np.uint8:
        img = img.astype('uint16')
        min_img = img.min()
        max_img = img.max()
        lut = BitDepthConverter.create_LUT((int(min_img), int(max_img)), 16, 8)
        img = BitDepthConverter.apply_LUT(img, lut)

    if denoise == 'blur':
        img = cv2.blur(img, denoise_params)
    elif denoise == 'NlMeans':
        img = cv2.fastNlMeansDenoising(img, None, *denoise_params)
    elif denoise == 'none':
        pass
    else:
        raise ValueError('Invalid denoise argument: ' + str(denoise))

    if method == 'spectral_saliency':
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (ret, saliencyMap) = saliency.computeSaliency(img)
        img = (saliencyMap * 255).astype("uint8")

    elif method == 'fine_grained_saliency':
        saliency = cv2.saliency.StaticSaliencyFineGrained_create()
        (success, saliencyMap) = saliency.computeSaliency(img)

    rval, th_img = cv2.threshold(img.astype('uint8'), *thresh, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    im2, contours, hierarchy = cv2.findContours(th_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    try:
        hierarchy = hierarchy[0]
    except:
        hierarchy = []

    height, width = th_img.shape
    min_x, min_y = width, height
    max_x = max_y = 0

    # computes the bounding box for the contour, and draws it on the frame,
    for contour, hier in zip(contours, hierarchy):
        (x, y, w, h) = cv2.boundingRect(contour)
        min_x, max_x = min(x, min_x), max(x + w, max_x)
        min_y, max_y = min(y, min_y), max(y + h, max_y)
        # if w > 80 and h > 80:
        # cv2.rectangle(th_img, (x,y), (x+w,y+h), (255, 0, 0), 2)

    x1 = max(0, min_x - padding)
    x2 = min(img.shape[0], max_x + padding)

    y1 = max(0, min_y - padding)
    y2 = min(img.shape[1], max_y + padding)

    if max_x - min_x > 0 and max_y - min_y > 0:

        return True, [(x1, y1), (x2, y2)]

    else:
        return False, [(x1, y1), (x2, y2)]


def crop(seq: np.ndarray, params: dict) -> np.ndarray:
    """
    :param seq:     image sequence
    :param params:  params, passed to get_rect()
    :return:        cropped image sequence
    """
    r, rect = get_rect(seq, **params)
    if r is False:
        raise ValueError('Cannot crop image sequence, try different parameters\n' + str(rect))

    x1 = rect[0][0]
    y1 = rect[0][1]

    x2 = rect[1][0]
    y2 = rect[1][1]

    return seq[y1:y2, x1:x2, :]
