import datetime
import os
import time

import cv2
import imutils
import numpy as np
from PIL import Image
from math import sin, cos, pi, radians

from matplotlib import pyplot as plt


def find_vertical_edge(raw, processed):
    linear = np.mean(processed, axis=0, dtype=int)

    diffs = np.diff(linear, prepend=linear[0])

    max = np.amax(diffs[650:])
    argmax = np.argmax(diffs[650:])

    return argmax, max

    # fig, axs = plt.subplots(4,1)
    # plt.subplot(411), plt.imshow(raw, cmap='gray'), plt.title('Raw')
    # plt.subplot(412), plt.imshow(processed, cmap='gray'), plt.title('Processed')
    # axs[2].plot(linear)
    # axs[2].set_xlim(0, len(linear))
    # axs[3].plot(diffs)
    # axs[3].set_xlim(0, len(diffs))
    # plt.show()

def find_edge(image, save=False):
    # st = time.time()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x_a = 390
    y_a = 110
    length = 60
    distance = 160
    alpha = 310

    line_1 = Line(x1=x_a, y1=y_a, alpha=alpha, length=length)
    line_2 = Line(x1=x_a, y1=y_a, alpha=alpha + 90, length=distance)
    image_with_lines = draw_lines(image, [line_1, line_2])
    # cv2.imshow("image_with_lines", image_with_lines)
    # cv2.waitKey(0)
    rectangle = Rectangle(line_1, line_2)

    image_cropped_with_lines = image_with_lines[rectangle.y_min: rectangle.y_max, rectangle.x_min: rectangle.x_max]
    image_cropped = image[rectangle.y_min: rectangle.y_max, rectangle.x_min: rectangle.x_max]

    # cv2.imshow("image_cropped", image_cropped)
    # cv2.waitKey(0)

    alpha_range = 20
    diffs_sum = np.zeros((alpha_range, distance - 1))
    for beta in range(0, alpha_range):
        diffs_sum[beta, :] = find_step_value(image_cropped, alpha - alpha_range/2 + beta, length, distance)

    min_step = np.amin(diffs_sum)
    min_index = np.where(diffs_sum == min_step)
    degree = alpha - alpha_range/2 + min_index[0][0]
    dist = int(min_index[1][0] + 1)

    x_e = x_a - int(dist * sin(radians(degree)))
    y_e = y_a - int(dist * cos(radians(degree)))
    edge = Line(x1=x_e, y1=y_e, alpha=degree, length=length)
    image_with_edge = draw_lines(image_with_lines, [edge])
    edge_cropped = Line(x1=x_e-x_a, y1=y_e-y_a, alpha=degree, length=length)
    image_with_edge_cropped = draw_lines(image_cropped_with_lines, [edge])

    # cv2.imshow("edge", image_with_edge)
    # cv2.waitKey(0)
    # print(time.time() - st)
    if save:
        path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
        path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_min_' + str(int(min_step)) + '_dist_' + str(dist) + '.png'
        Image.fromarray(image_with_edge).save(path_dist)
        path_raw = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') + '_raw' + '.png'
        Image.fromarray(image).save(path_raw)
    # debug
    find_step_value(image_cropped, degree, length, distance)
    return dist, degree


def find_step_value(image, alpha, length, distance):
    image_rotated = rotate_image(image, 270 - alpha, length, distance)

    # if alpha == 307:
    #     x_e = 27
    #     y_e = 0
    #     edge = Line(x1=x_e, y1=y_e, alpha=270, length=length)
    #     image_with_edge = draw_lines(image_rotated, [edge])
    #     cv2.imshow("edge", image_with_edge)
    #     cv2.waitKey(0)

    # diffs = np.diff(image_rotated, prepend=np.ndarray((image_rotated.shape[0], 1), image_rotated[:, 0]))
    diffs = np.diff(image_rotated)  #, prepend=np.expand_dims(image_rotated[:, 0], axis=1)) # todo add 1 in further calculations

    diffs_normalized = (diffs + 255) // 2
    # cv2.imshow("diffs", diffs_normalized)
    # cv2.waitKey(0)

    diffs_sum = np.sum(diffs, axis=0)
    # plt.plot(diffs_sum)
    # plt.ylabel('diffs')
    # plt.show()

    # diff_min = np.amin(diffs_sum)

    return diffs_sum


def rotate_image(image, angle, result_width, result_height):
    rotated = imutils.rotate(image, angle)
    cropped = crop(rotated, result_width, result_height)
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
            if 'raw' in file:
                image = cv2.imread(os.path.join(path, file))
                dist, deg = find_edge(image)
                dists.append(dist)
    pass
