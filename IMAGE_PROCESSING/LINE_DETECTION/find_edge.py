import datetime
import os
import time
import cv2
import numpy as np
from PIL import Image
from math import sin, cos, pi

from CONFIG.config import target_distance, target_degree, min_diff, default_y1, default_x1, default_x2, window, steps, \
    height_step, bottom_dist


def find_curvy_edge(image, save=False, edge_thickness=1, last_dist=None, last_trans=None, half_search_width=150,
              right_margin=300, y1=default_y1, y2=window['height'], bottom=bottom_dist):
    photo_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-5]

    last_dist_internal = [None]*steps
    last_trans_internal = [None]*steps
    for i in range(steps):
        if last_trans is not None:
            # half_search_width = last_trans // 4
            half_search_width = height_step * 2
        last_dist_internal[i], last_trans_internal[i], max_diff, image_with_line = find_edge(image,
                                                                                             edge_thickness=edge_thickness,
                                                                                             last_dist=last_dist_internal[i-1],
                                                                                             save=save,
                                                                                             last_trans=last_trans_internal[i-1],
                                                                                             half_search_width=half_search_width,
                                                                                             y1=window['height'] - bottom - height_step,
                                                                                             y2=window['height'] - bottom,
                                                                                             step=i,
                                                                                             photo_time=photo_time)
        bottom += height_step
        if i == 0:
            last_dist = last_dist_internal[i]
            last_trans = last_trans_internal[i]

    lane_borders = [None]*steps
    lane_width = 300
    lane_width_decrement_per_step = 25
    for i in range(steps):
        if last_trans_internal[i] is not None:
            lane_borders[i] = (last_dist_internal[i] - lane_width, last_dist_internal[i])
        else:
            lane_borders[i] = (None, None)
        lane_width -= lane_width_decrement_per_step

    return last_dist, last_trans, max_diff, image_with_line, lane_borders


def find_edge(image, save=False, edge_thickness=1, last_dist=None, last_trans=None, half_search_width=150,
              right_margin=300, y1=default_y1, y2=window['height'], step='', photo_time='time'):
    if last_dist is not None:
        if last_trans is not None:
            half_search_width = 2 * last_trans
            x1 = min(last_dist - half_search_width - last_trans, image.shape[1] - right_margin)
            x2 = min(last_dist + half_search_width - last_trans, image.shape[1])
        else:
            x1 = min(last_dist - half_search_width, image.shape[1] - right_margin)
            x2 = min(last_dist + half_search_width, image.shape[1])
    else:
        last_dist = None
        x1 = default_x1
        x2 = default_x2
    # y1 = default_y1
    # y2 = image.shape[0]
    dst_max, trans_max, max_diff, image_with_line \
        = find_edge_internal(image, x1, x2, y1, y2, save=save, edge_thickness=edge_thickness, last_dist=last_dist, step=step, last_trans=last_trans, photo_time=photo_time)
    return dst_max, trans_max, max_diff, image_with_line


def find_edge_internal(image, x1, x2, y1, y2, save=False, edge_thickness=1, last_dist=None, step='', last_trans=None, photo_time='time'):
    line_h1 = Line(x1=x1, y1=y1, x2=x2, y2=y1)
    line_h2 = Line(x1=x1, y1=y2, x2=x2, y2=y2)
    line_v1 = Line(x1=x1, y1=y1, x2=x1, y2=y2)
    line_v2 = Line(x1=x2, y1=y1, x2=x2, y2=y2)
    line_t = Line(x1=target_distance, y1=y1, x2=target_distance, y2=y1 + (y2 - y1) // 2)
    image_with_area = draw_lines(image, [line_h1, line_h2, line_v1, line_v2, line_t])

    image_cropped = image[y1: y2, x1: x2]
    image_int = image_cropped.astype(int)
    if edge_thickness != 1:
        right = image_int[:, edge_thickness:]
        left = image_int[:, :- edge_thickness]
        diff = right - left
    else:
        diff = np.diff(image_int)
    # diff_normalized = normalize(diff)

    height = image_int.shape[0]
    if last_trans is not None:
        max_translation_r = last_trans + height // 2
        max_translation_l = last_trans - height // 2
    else:
        max_translation_r = height*2
        max_translation_l = -height * 2
    diff_col_sum = diff_col_sum_for_trans(diff, height=height, max_translation_l=max_translation_l, max_translation_r=max_translation_r)

    # repeated for debug
    diff_col_sum_normalized = normalize(diff_col_sum)

    # 2 solution - max of all
    max_diff = np.amax(diff_col_sum)
    index_max = np.where(diff_col_sum == max_diff)
    trans_max = index_max[0][0] + max_translation_l
    # dst_max = index_max[1][0] - abs(max_translation_l)
    dst_max = index_max[1][0] + max_translation_l
    dst_max = dst_max + x1

    line = Line(dst_max, 0, alpha=270, length=image.shape[0])
    image_with_line = draw_lines(image_with_area, [line])
    # print(dst_max, trans_max, max_diff)
    # cv2.imshow("image_with_line", image_with_line)
    # cv2.waitKey(0)
    if last_dist is None:
        last_dist = 0

    if save:
        path = r'C:\PROGRAMOWANIE\auto_data\photos\find_edge_debug'
        name = photo_time \
               + '_' + str(step) \
               + '_tra_' + str(int(trans_max)) + '_dst_' + str(int(dst_max)) + '_max_' + str(int(max_diff)) \
               + '_last_' + str(int(last_dist)) + '.png'
        path_dist = os.path.join(path, name)
        # Image.fromarray(image_with_line).save(path_dist)

    if max_diff >= min_diff * height:
        return dst_max, trans_max, max_diff, image_with_line
    else:
        return None, None, None, None


def diff_col_sum_for_trans(diff, height, max_translation_l, max_translation_r):
    new_width = diff.shape[1] + abs(min(max_translation_l, 0)) + max(0, max_translation_r)
    diff_col_sum = np.zeros((max_translation_r - max_translation_l, new_width), dtype=int)

    if max_translation_l < 0:
        right = min(max_translation_r, 0)
        new_height = right - max_translation_l
        new_width = diff.shape[1] - max_translation_l
        diff_col_sum_l = np.zeros((new_height, new_width), dtype=int)
        for trans in range(max_translation_l, right):
            new_diff = np.zeros((height, new_width), dtype=int)
            for row in range(height):
                trans_row = trans * (height - row) // height
                trans_row_end = trans_row - diff.shape[1]
                new_diff[row, trans_row_end: trans_row] = diff[row, :]
            # new_diff_normalized = normalize(new_diff)
            # try:
            diff_col_sum_l[trans - right, :] = np.sum(new_diff, axis=0)
            # except IndexError as e:
            #     d4=e
        diff_col_sum[:diff_col_sum_l.shape[0], :diff_col_sum_l.shape[1]] = diff_col_sum_l

    if max_translation_r > 0:
        left = max(max_translation_l, 0)
        new_height = max_translation_r - left
        new_width = diff.shape[1] + max_translation_r
        diff_col_sum_r = np.zeros((new_height, new_width), dtype=int)
        for trans in range(left, max_translation_r):
            new_diff = np.zeros((height, new_width), dtype=int)
            for row in range(height):
                trans_row = trans * (height - row) // height
                trans_row_end = trans_row + diff.shape[1]
                # try:
                new_diff[row, trans_row: trans_row_end] = diff[row, :]
                # except ValueError as e:
                #     d2=2
            # new_diff_normalized = normalize(new_diff)
            diff_col_sum_r[trans - left, :] = np.sum(new_diff, axis=0)
        # try:
        diff_col_sum[-diff_col_sum_r.shape[0]:, -diff_col_sum_r.shape[1]:] = diff_col_sum_r
        # except ValueError as e:
        #     d3=3

    diff_col_sum_normalized = normalize(diff_col_sum)

    return diff_col_sum


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
    path = r'C:\PROGRAMOWANIE\auto_data\photos\2021-01-13\20_10_03'
    path = r'C:\PROGRAMOWANIE\auto_data\photos\lc\2021-06-30\22_37_20'
    last_dist = 500
    last_dist = None
    last_trans = None
    half_search_width = 150

    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                find_curvy_edge(image, save=True, edge_thickness=1, last_dist=None, last_trans=None,
                                half_search_width=150,
                                right_margin=300, y1=default_y1, y2=window['height'])
                print(f'E2: {time.time() - st}')

    pass
