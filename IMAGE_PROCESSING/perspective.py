import os

import cv2
import numpy as np
from matplotlib import pyplot as plt

from CONFIG.config import points_before_transform, points_after_transform, x_size, y_size, y_min, y_max, x_min, x_max, \
    x_margin


def perspective(raw):
    pts1 = np.float32(points_before_transform)
    pts2 = np.float32(points_after_transform)

    M = cv2.getPerspectiveTransform(pts1, pts2)

    processed = cv2.warpPerspective(raw, M, (x_size + 2 * x_margin, y_size))

    # plt.subplot(121), plt.imshow(image), plt.title('Input')
    # plt.subplot(122), plt.imshow(dst), plt.title('Output')
    # plt.imshow(processed)
    # plt.show()

    return processed


if __name__ == '__main__':
    image = cv2.imread(r'C:\PROGRAMOWANIE\auto_data\photos\lc\2021-06-30\22_35_43\0_raw.png', cv2.IMREAD_GRAYSCALE)
    path = r'C:\PROGRAMOWANIE\auto_data\photos\lc\2021-06-30\22_35_43\0_raw.png'
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image_cropped = image[y_min: y_max, x_min - x_margin: x_max + x_margin]

    perspective(image)
