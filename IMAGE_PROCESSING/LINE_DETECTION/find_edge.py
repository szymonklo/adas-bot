import os
import time
import cv2
import numpy as np
from math import sin, cos, pi
from scipy.ndimage import gaussian_filter

from CONFIG.config import min_diff, default_x1, default_x2, window_line, steps, height_step, \
    bottom_dist, min_line_search_half_width, min_x1, default_right_margin, lane_width_decrement_per_step, \
    default_lane_width, target_distance
from draw import draw_lane
from process_results import Edge_results


def find_curvy_edge(image, last_dist=None, last_trans=None, debug=False) -> Edge_results:
    # todo - add second edge as verification
    # init variables
    bottom_in_current_step = bottom_dist
    lane_width_in_current_step = default_lane_width
    first_result_index_found = False
    default_result_index = 3
    result_index = 0

    # init results arrays
    last_dist_internal = [None] * steps
    last_trans_internal = [None] * steps
    max_diff_internal = [None] * steps
    edge_found_statuses = [False] * steps
    lane_borders = [(0, 0)] * steps
    search_borders = [(0, 0)] * steps

    for i in range(steps):
        y1 = window_line['height'] - bottom_in_current_step - height_step
        y2 = window_line['height'] - bottom_in_current_step
        height = y2 - y1
        if last_dist is not None and last_trans is not None:
            if i != 0:
                last_dist -= lane_width_decrement_per_step
            half_search_width = height_step * 2.5
            if first_result_index_found is False:
                half_search_width = height_step * 6  # 4 was too low when engaging at curve
            half_search_width = max(2 * last_trans, min_line_search_half_width, half_search_width)
            x1 = min(last_dist - half_search_width - last_trans, image.shape[1] - default_right_margin)
            x2 = min(last_dist + half_search_width - last_trans, image.shape[1])
            x1 = max(min_x1, x1)
            x2 = max(x1 + half_search_width * 2, x2)
            max_translation_l = last_trans - height // 2        # todo - increase for higher curvature and higher step
            max_translation_r = last_trans + height // 2
        else:
            x1 = default_x1
            x2 = int(default_x2 - lane_width_decrement_per_step / 2 * i)
            max_translation_l = -height * 2
            max_translation_r = height * 2

        search_borders[i] = x1, x2

        find_edge_results = find_edge(image, x1, x2, y1, y2, max_translation_l, max_translation_r, debug=debug)
        last_dist_internal[i], last_trans_internal[i], max_diff_internal[i], edge_found_statuses[i] = find_edge_results
        bottom_in_current_step += height_step

        if edge_found_statuses[i]:
            last_dist = last_dist_internal[i]
            last_trans = last_trans_internal[i]
            if first_result_index_found is False:
                result_index = i
                first_result_index_found = True
            elif i <= default_result_index:
                result_index = i
            last_dist_internal[i] += lane_width_decrement_per_step * i
        else:
            lane_borders[i] = (0, 0)
        lane_borders[i] = (find_edge_results[0] - lane_width_in_current_step, find_edge_results[0])
        lane_width_in_current_step -= lane_width_decrement_per_step

    if edge_found_statuses[result_index]:
        last_dist = last_dist_internal[result_index]
        last_trans = last_trans_internal[result_index]
        max_diff = max_diff_internal[result_index]
        edge_found_status = edge_found_statuses[result_index]
    else:
        last_dist, last_trans, max_diff, edge_found_status = None, None, None, False
    if len([status for status in max_diff_internal if status > 0.8 * min_diff * height_step]) < 3:
        last_dist, last_trans, max_diff, edge_found_status = None, None, None, False
    # image_with_line = images_with_line_internal[result_index]
    image_with_lane = draw_lane(image, lane_borders, max_diff_internal=max_diff_internal,
                                edge_found_statuses=edge_found_statuses, search_borders=search_borders)

    edge_results = Edge_results(image, last_dist, last_trans, max_diff, image_with_lane, lane_borders, edge_found_status)
    return edge_results


def find_edge(image, x1, x2, y1, y2, max_translation_l, max_translation_r,
              edge_thickness=1, debug=False):
    if debug:
        line_h1 = Line(x1=x1, y1=y1, x2=x2, y2=y1)
        line_h2 = Line(x1=x1, y1=y2, x2=x2, y2=y2)
        line_v1 = Line(x1=x1, y1=y1, x2=x1, y2=y2)
        line_v2 = Line(x1=x2, y1=y1, x2=x2, y2=y2)
        line_t = Line(x1=target_distance, y1=y1, x2=target_distance, y2=y1 + (y2 - y1) // 2)
        image_with_area = draw_lines(image, [line_h1, line_h2, line_v1, line_v2, line_t])

    image_cropped_raw = image[y1: y2, x1: x2]
    image_cropped = gaussian_filter(image_cropped_raw, sigma=1)
    image_int = image_cropped.astype(int)
    if edge_thickness != 1:
        right = image_int[:, edge_thickness:]
        left = image_int[:, :- edge_thickness]
        diff_0 = right - left
    else:
        diff_0 = np.diff(image_int)
    try:
        percentile = np.percentile(diff_0, [0.5, 99.5]).astype(np.int32)
        diff_cut_1 = np.where(diff_0 > min(percentile), diff_0, min(percentile))
        diff_cut_2 = np.where(diff_cut_1 < max(percentile), diff_cut_1, max(percentile))
        diff = diff_cut_2
        # diff_normalized = normalize(diff)
    except Exception as e:
        print(f'x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}')
        print(f'diff_shape: {diff_0.shape}')
        raise e

    diff_col_sum = diff_col_sum_for_trans(diff, height=y2 - y1, max_translation_l=max_translation_l,
                                          max_translation_r=max_translation_r)

    # diff_col_sum_normalized = normalize(diff_col_sum)

    # 2 solution - max of all
    max_diff = np.amax(diff_col_sum)
    index_max = np.where(diff_col_sum == max_diff)
    trans_max = index_max[0][0] + max_translation_l
    # dst_max = index_max[1][0] - abs(max_translation_l)
    dst_max = index_max[1][0] + max_translation_l # why was + max_translation?
    dst_max = dst_max + x1

    if debug:
        line = Line(dst_max, 0, alpha=270, length=image.shape[0])
        image_with_line = draw_lines(image_with_area, [line])

    # print(dst_max, trans_max, max_diff)
    # cv2.imshow("image_with_line", image_with_line)
    # cv2.waitKey(0)
    # if last_dist is None:
    #     last_dist = 0

    # if save:
    #     path = r'C:\PROGRAMOWANIE\auto_data\photos\find_edge_debug'
    #     if file is not None:
    #         name = file + '_'
    #     else:
    #         name = ''
    #     name += photo_time \
    #            + '_' + str(step) \
    #            + '_tra_' + str(int(trans_max)) + '_dst_' + str(int(dst_max)) + '_max_' + str(int(max_diff)) \
    #            + '_last_' + str(int(last_dist)) + '.png'
    #     path_dist = os.path.join(path, name)
    #     Image.fromarray(image_with_line).save(path_dist)

    if max_diff >= min_diff * (y2 - y1):
        return dst_max, trans_max, max_diff, True
    else:
        return dst_max, trans_max, max_diff, False


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
            diff_col_sum_l[trans - right, :] = np.sum(new_diff, axis=0)
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
                new_diff[row, trans_row: trans_row_end] = diff[row, :]
            diff_col_sum_r[trans - left, :] = np.sum(new_diff, axis=0)
        diff_col_sum[-diff_col_sum_r.shape[0]:, -diff_col_sum_r.shape[1]:] = diff_col_sum_r

    # diff_col_sum_normalized = normalize(diff_col_sum)
    return diff_col_sum


def normalize(array):
    array_normalized = (array - np.amin(array)).astype(np.int32)
    array_255 = array_normalized * 255
    array_normalized = array_255 // np.amax(array_normalized)
    array_normalized = array_normalized.astype(np.uint8)

    return array_normalized


def draw_lines(image_referential, lines):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    for line in lines:
        cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (255, 0, 0), 2)
    lines_edges = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    return lines_edges


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


class Area:
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2


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

    def draw_retangle(self, image_referential):
        ...


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\lc\2022-05-28\11_47_00'

    dists = []
    dist = None
    trans = None
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                dist, trans, diff, image_with_line, lane_borders, edge_found_status = find_curvy_edge(image,
                                                                                                      last_dist=dist,
                                                                                                      last_trans=trans,
                                                                                                      debug=True
                                                                                                      )
                print(f'E2: {time.time() - st}')

    pass
