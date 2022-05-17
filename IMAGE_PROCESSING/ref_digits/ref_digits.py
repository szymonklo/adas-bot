import os

import cv2
import numpy as np

from config import RefDigitsPath
from detect_speed import find_digit_images


def init_ref_digits():
    ref_digits = init_speed(RefDigitsPath.cluster)
    ref_digits_signs1 = init_speed(RefDigitsPath.signs)
    ref_digits_signs = {}

    for digit, ref_digits_sign1 in ref_digits_signs1.items():
        width = ref_digits_sign1.shape[0]
        if width != 15:
            widths = 9, 18, int(0.4 * width), int(0.6 * width)
            ref_digits_sign = find_digit_images(ref_digits_sign1, ref_digits={}, widths=widths, axis=1)
            ref_digits_signs[digit] = ref_digits_sign[0]
        else:
            ref_digits_signs[digit] = ref_digits_sign1

    return ref_digits, ref_digits_signs


def init_speed(path):
    ref_digits = {}
    files = os.listdir(path)
    for file in files:
        image = cv2.imread(os.path.join(path, file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # image = image.astype(np.int16)
        image = image.astype(np.uint8)
        ref_digits.update({file[:-4]: image})
    return ref_digits
