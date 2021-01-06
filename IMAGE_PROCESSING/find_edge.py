import datetime
import os
import time
import cv2
import numpy as np
from PIL import Image
from math import sin, cos, pi
from matplotlib import pyplot as plt

from CONFIG.config import target_distance, target_degree, min_diff


def find_edge_2(image, save=False, edge_thickness=1, last_dist=None):
    x1 = 379
    x2 = 679
    if last_dist is not None:
        x1 = last_dist - 150
        x2 = last_dist + 150
    else:
        last_dist = 0
    y1 = -60
    line_h = Line(x1=x1, y1=image.shape[0] + y1, x2=x2, y2=image.shape[0] + y1)
    line_v1 = Line(x1=x1, y1=image.shape[0] + y1, x2=x1, y2=image.shape[0])
    line_v2 = Line(x1=x2, y1=image.shape[0] + y1, x2=x2, y2=image.shape[0])
    line_t = Line(x1=target_distance, y1=image.shape[0] + y1, x2=target_distance, y2=image.shape[0] + y1 // 2)
    image_with_area = draw_lines(image, [line_h, line_v1, line_v2, line_t])

    image_cropped = image[y1:, x1: x2]
    image_int = image_cropped.astype(int)
    if edge_thickness != 1:
        right = image_int[:, edge_thickness:]
        left = image_int[:, :- edge_thickness]
        diff = right - left
    else:
        diff = np.diff(image_int)
    # diff_normalized = normalize(diff)
    max_translation = image_int.shape[0] * 2
    new_width = diff.shape[1] + max_translation
    diff_col_sum = np.zeros((max_translation, new_width), dtype=int)

    for trans in range(max_translation):
        new_diff = np.zeros((image_int.shape[0], new_width), dtype=int)
        for row in range(image_int.shape[0]):
            trans_row = trans * (image_int.shape[0] - row) // image_int.shape[0]
            trans_row_end = trans_row + diff.shape[1]
            # new_diff[row, -trans_row_end-1: -trans_row-1] = diff[row, :]
            new_diff[row, trans_row: trans_row_end] = diff[row, :]
        # new_diff_normalized = normalize(new_diff)
        diff_col_sum[trans, :] = np.sum(new_diff, axis=0)
    # diff_col_sum_normalized = normalize(diff_col_sum)

    # 1 solution - first greater than
    max_diff = diff_col_sum[0, 0]
    maxes = np.max(diff_col_sum, axis=0)
    for max_col in maxes:
        if max_col < min_diff:
            continue
        max_diff = max_col
        break

    # 2 solution - max of all
    # max = np.amax(diff_col_sum)
    index_max = np.where(diff_col_sum == max_diff)
    trans_max = index_max[0][0]
    dst_max = index_max[1][0]
    dst_max = dst_max + x1

    line = Line(dst_max, 0, alpha=270, length=image.shape[0])
    image_with_line = draw_lines(image_with_area, [line])
    print(dst_max, trans_max, max_diff)
    # cv2.imshow("image_with_line", image_with_line)
    # cv2.waitKey(0)

    if save:
        path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
        path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') \
                    + '_tra_' + str(int(trans_max)) + '_dst_' + str(int(dst_max)) + '_max_' + str(int(max_diff))\
                    + '_last_' + str(int(last_dist)) + '.png'
        Image.fromarray(image_with_line).save(path_dist)
        path_raw = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_raw' + '.png'
        Image.fromarray(image).save(path_raw)

    if max_diff > min_diff:
        return dst_max, trans_max, max_diff, image_with_line
    else:
        return None, None, None, None


def normalize(array):
    array_normalized = array - np.amin(array)
    array_255 = array_normalized * 255
    array_normalized = array_255 // np.amax(array_normalized)
    array_normalized = array_normalized.astype(np.uint8)

    return array_normalized


def draw_lines(image_referential, lines):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    for line in lines:
        cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (255, 0, 0), 2)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    return lines_edges_skl


class Line:
    def __init__(self, x1, y1, x2=None, y2=None, alpha=None, length=None):
        self.x1 = x1
        self.y1 = y1
        if x2 is not None and y2 is not None:
            self.x2 = x2
            self.y2 = y2
        elif alpha is not None and length is not None:
            self.alpha = alpha
            self.length = length
            self.x2 = x1 + int(length * cos(pi * alpha / 180))
            self.y2 = y1 - int(length * sin(pi * alpha / 180))


class Rectangle:
    def __init__(self, line_1, line_2):
        if line_1.x1 != line_2.x1 or line_1.y1 != line_2.y1:
            raise Exception('Lines defining Rectangle must have common beginning')
        self.x1 = line_1.x1
        self.y1 = line_1.y1
        self.x2 = line_1.x2
        self.y2 = line_1.y2
        self.x3 = line_2.x2
        self.y3 = line_2.y2
        self.x4 = line_1.x2 + line_2.x2 - line_1.x1
        self.y4 = line_1.y2 + line_2.y2 - line_1.y1

        self.x_min = min(self.x1, self.x2, self.x3, self.x4)
        self.x_max = max(self.x1, self.x2, self.x3, self.x4)
        self.y_min = min(self.y1, self.y2, self.y3, self.y4)
        self.y_max = max(self.y1, self.y2, self.y3, self.y4)
        self.length = self.x_max - self.x_min
        self.width = self.y_max - self.y_min


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos'
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'image2021-01-05-18_00_24_tra_20_dst_549_max_533tis0.05' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                find_edge_2(image, edge_thickness=3, last_dist=681)
                print(f'E2: {time.time() - st}')

    pass
