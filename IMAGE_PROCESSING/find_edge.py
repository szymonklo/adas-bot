import datetime
import os
import time

import cv2
import imutils
import numpy as np
from PIL import Image
from math import sin, cos, pi, radians

from matplotlib import pyplot as plt


def find_edge_2(image, save=False, edge_thickness=1):
    #TODO - edge width (arr - arr_translated)
    x1 = 279
    x2 = 679
    y1 = -60
    image_cropped = image[y1:, x1: x2]
    image_int = image_cropped.astype(int)
    if edge_thickness != 1:
        right = image_int[:, edge_thickness:]
        left = image_int[:, :- edge_thickness]
        diff = right - left
    else:
        diff = np.diff(image_int)
    # diff_normalized = normalize(diff)
    rec_width = 200
    # max_translation = image.shape[1] - rec_width
    max_translation = image_int.shape[0]
    new_width = diff.shape[1] + max_translation
    # new_image = np.zeros((image.shape[0], new_width), dtype=int)
    diff_col_sum = np.zeros((max_translation, new_width), dtype=int)

    for trans in range(max_translation):
        # trans_end = trans + diff.shape[1]
        new_diff = np.zeros((image_int.shape[0], new_width), dtype=int)
        for row in range(image_int.shape[0]):
            trans_row = trans * (image_int.shape[0] - row) // image_int.shape[0]
            trans_row_end = trans_row + diff.shape[1]
            # new_diff[row, -trans_row_end-1: -trans_row-1] = diff[row, :]
            new_diff[row, trans_row: trans_row_end] = diff[row, :]
        # new_diff_normalized = normalize(new_diff)
        diff_col_sum[trans, :] = np.sum(new_diff, axis=0)



    max = np.amax(diff_col_sum)
    index_max = np.where(diff_col_sum == max)
    trans_max = index_max[0][0]
    dst_max = index_max[1][0]
    dst_max = dst_max + x1# - max_translation + trans_max

    diff_col_sum_normalized = normalize(diff_col_sum)
    #
    # line = Line(dst_max, 0, 270, image.shape[0])
    # image_with_line = draw_lines(image, [line])
    # print(dst_max, max)
    # cv2.imshow("image_with_line", image_with_line)
    # cv2.waitKey(0)

    return dst_max, trans_max, max


def normalize(array):
    array_normalized = array - np.amin(array)
    array_255 = array_normalized * 255
    array_normalized = array_255 // np.amax(array_normalized)
    array_normalized = array_normalized.astype(np.uint8)

    return array_normalized


def find_vertical_edge(processed, raw):
    linear = np.mean(processed, axis=0, dtype=int)

    diffs = np.diff(linear, prepend=linear[0])

    max = np.amax(diffs[650:])
    argmax = np.argmax(diffs[650:])


    fig, axs = plt.subplots(4,1)
    plt.subplot(411), plt.imshow(raw, cmap='gray'), plt.title('Raw')
    plt.subplot(412), plt.imshow(processed, cmap='gray'), plt.title('Processed')
    axs[2].plot(linear)
    axs[2].set_xlim(0, len(linear))
    axs[3].plot(diffs)
    axs[3].set_xlim(0, len(diffs))
    # plt.show()
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
    path_fig = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_max_' + str(
        int(max)) + '_arg_max_' + str(argmax) + '.png'
    plt.savefig(path_fig)
    plt.close()

    return argmax, max


def find_edge(image, save=False):
    # st = time.time()
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x_a = 455
    y_a = 210
    length = 60
    distance = 200
    alpha = 30
    margin = 20

    line_1 = Line(x1=x_a, y1=y_a, alpha=alpha + 90, length=length)
    line_2 = Line(x1=x_a, y1=y_a, alpha=alpha, length=distance)
    # image_with_lines = draw_lines(image, [line_1, line_2])
    # cv2.imshow("image_with_lines", image_with_lines)
    # cv2.waitKey(0)
    rectangle = Rectangle(line_1, line_2)

    # image_cropped_with_lines = image_with_lines[rectangle.y_min: rectangle.y_max, rectangle.x_min: rectangle.x_max]
    image_cropped = image[rectangle.y_min-margin: rectangle.y_max+margin, rectangle.x_min-margin: rectangle.x_max+margin]

    # cv2.imshow("image_cropped", image_cropped)
    # cv2.waitKey(0)

    alpha_range = 34
    diffs_sum = np.zeros((alpha_range, distance - 1))
    for beta in range(0, alpha_range):
        diffs_sum[beta, :] = find_step_value(image_cropped, alpha - alpha_range/2 + beta, length, distance)

    # max_step = np.amax(diffs_sum)
    # max_index = np.where(diffs_sum == max_step)
    # degree = alpha - alpha_range//2 + max_index[0][0]
    # dist = int(max_index[1][0] + 1)

    max_axis0 = np.amax(diffs_sum, axis=0)
    diffs_sum_min = 800
    try:
        first_index_above_limit = np.where(max_axis0 > diffs_sum_min)[0][0]
        step = max_axis0[first_index_above_limit]
        degree_first_index = alpha - alpha_range // 2 + \
                             np.where(diffs_sum[:, first_index_above_limit] == max_axis0[first_index_above_limit])[0][0]
    except (ValueError, IndexError):  # no index fulfils given criteria
        first_index_above_limit = None
        degree_first_index = None
        step=None
    dist = first_index_above_limit
    degree = degree_first_index

    if dist is not None and degree is not None:
        # x_e = x_a + int(dist * cos(radians(degree)))
        # y_e = y_a - int(dist * sin(radians(degree)))
        # edge = Line(x1=x_e, y1=y_e, alpha=degree + 90, length=length)
        # image_with_edge = draw_lines(image_with_lines, [edge])
        # edge_cropped = Line(x1=x_e-x_a, y1=y_e-y_a, alpha=degree, length=length)
        # image_with_edge_cropped = draw_lines(image_cropped_with_lines, [edge])

        # cv2.imshow("edge", image_with_edge)
        # cv2.waitKey(0)
        # print(time.time() - st)
        if save:
            path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
            # path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_deg_' + str(int(degree)) + '_dist_' + str(dist) + '_step_' + str(step) + '.png'
            # Image.fromarray(image_with_edge).save(path_dist)
            path_raw = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_raw' + '.png'
            Image.fromarray(image).save(path_raw)
        # debug
        # find_step_value(image_cropped, degree, length, distance, debug=True)

    return dist, degree, step
    # return first_index_above_limit, degree_first_index



def find_step_value(image, alpha, length, distance, debug=False):
    image_rotated = rotate_image(image, - alpha, length, distance)
    # image_rotated = crop(image_rotated, length, distance)

    # diffs = np.diff(image_rotated, prepend=np.ndarray((image_rotated.shape[0], 1), image_rotated[:, 0]))
    image_rotated_int = image_rotated.astype(int)
    diffs = np.diff(image_rotated_int)  #, prepend=np.expand_dims(image_rotated[:, 0], axis=1)) # todo add 1 in further calculations

    # diffs_normalized_int32 = (diffs + 255) // 2
    # diffs_normalized_uint8 = diffs_normalized_int32.astype('uint8')
    # cv2.imshow("diffs", diffs_normalized)
    # cv2.waitKey(0)

    diffs_sum = np.sum(diffs, axis=0)
    # plt.plot(diffs_sum)
    # plt.ylabel('diffs')
    # plt.show()

    # diff_min = np.amin(diffs_sum)
    # col_sum = np.sum(image_rotated_int, axis=0)
    # diffs_sum2 = np.diff(col_sum, prepend=col_sum[0])
    #
    # min_limit = 0.8 * max(col_sum)
    #
    # arguments = np.argwhere(col_sum > min_limit)

    # dst = (arguments[0] + arguments[-1]) // 2

    return diffs_sum


def rotate_image(image, angle, length, distance):
    rotated = imutils.rotate_bound(image, -angle)
    cropped = crop(rotated, length, distance)
    # cv2.imshow("image_rotated_and_cropped", cropped)
    # cv2.waitKey(0)

    return cropped


def crop(image, result_width, result_height):
    y_0 = int((image.shape[0] - result_width) / 2)
    y_1 = int((image.shape[0] + result_width) / 2)
    x_0 = int((image.shape[1] - result_height) / 2)
    x_1 = int((image.shape[1] + result_height) / 2)

    image_cropped = image[y_0: y_1, x_0: x_1]
    return image_cropped


def draw_lines(image_referential, lines):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    for line in lines:
        cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (255, 0, 0), 2)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    # cv2.imshow("edges_skl", lines_edges_skl)
    # cv2.waitKey(0)
    return lines_edges_skl


class Line:
    def __init__(self, x1, y1, alpha, length):
        self.x1 = x1
        self.y1 = y1
        if alpha is not None and length is not None:
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
    # path = r'C:\PROGRAMOWANIE\auto_data\photos\image3.png'
    # image = cv2.imread(path)
    # find_edge(image)
    path = r'C:\PROGRAMOWANIE\auto_data\photos'
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file and 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                dist, deg, step = find_edge(image)
                dists.append(dist)

                print(f'E1: {time.time() - st}')
                st = time.time()

                find_edge_2(image, edge_thickness=3)
                print(f'E2: {time.time() - st}')

    pass
