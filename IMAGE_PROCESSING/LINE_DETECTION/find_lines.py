import copy
import datetime
import os
import time
import cv2
import numpy as np
from PIL import Image
from math import sin, cos, pi

from CONFIG.config import target_distance, target_degree, min_diff, default_y1, default_x1, default_x2


def find_lines(image, save=False, edge_thickness=1, last_dist=None):
    image_blur1 = cv2.GaussianBlur(image, (1, 51), cv2.BORDER_DEFAULT)
    image_blur2 = cv2.GaussianBlur(image, (51, 1), cv2.BORDER_DEFAULT)

    ret, binary_image = cv2.threshold(image, 130, 200, cv2.THRESH_BINARY)
    ret, otsu_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    binary_image_gauss = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=13, C=12)
    # binary_image = binary_image_gauss
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours_filtered = [cnt for cnt in contours if cnt.shape[0] > 30]

    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    img = copy.deepcopy(image_color)
    img = cv2.drawContours(img, contours_filtered, -1, (0, 255, 0), 1)
    return img


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\lc\2021-06-30\22_35_43'
    last_dist = 500
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                last_dist, _, _, _ = find_lines(image, edge_thickness=3, last_dist=last_dist)
                print(f'E2: {time.time() - st}')

    pass
