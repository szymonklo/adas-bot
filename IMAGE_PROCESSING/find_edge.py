import time

import cv2
import imutils
import numpy as np
from PIL import Image
from math import sin, cos, pi


def find_edge(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x_a = 400
    y_a = 40
    length = 120
    distance = 60
    alpha = 300

    line_1 = Line(x1=x_a, y1=y_a, alpha=alpha, length=length)
    line_2 = Line(x1=x_a, y1=y_a, alpha=alpha + 90, length=distance)
    image_with_lines = draw_lines(image, [line_1, line_2])
    rectangle = Rectangle(line_1, line_2)


    image_cropped = image_with_lines[rectangle.y_min: rectangle.y_max, rectangle.x_min: rectangle.x_max]
    cv2.imshow("image_cropped", image_cropped)
    cv2.waitKey(0)

    image_rotated = rotate_image(image_cropped, 270 - alpha, length, distance)

    pass


def rotate_image(image, angle, result_width, result_height):
    st = time.time()
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    print(time.time() - st)
    cv2.imshow("image_rotated_cv2", result)
    cv2.waitKey(0)

    st = time.time()
    rotated_bound = imutils.rotate_bound(image, -angle)
    print(time.time() - st)
    cv2.imshow("image_rotated_bound", rotated_bound)
    cv2.waitKey(0)

    st = time.time()
    rotated = imutils.rotate(image, angle)
    print(time.time() - st)
    cv2.imshow("image_rotated", rotated)
    cv2.waitKey(0)

    st = time.time()
    cropped = crop(rotated, result_width, result_height)
    print(time.time() - st)
    cv2.imshow("image_rotated_and_cropped", cropped)
    cv2.waitKey(0)

    return result


def crop(image, result_width, result_height):
    y_0 = int((image.shape[0] - result_width) / 2)
    y_1 = int((image.shape[0] + result_width) / 2)
    x_0 = int((image.shape[1] - result_height) / 2)
    x_1 = int((image.shape[1] + result_height) / 2)

    image_cropped = image[y_0: y_1, x_0: x_1]
    return image_cropped


# def draw_line(image_referential, x1, y1, alpha, length):
#     line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
#     cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
#     lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
#     cv2.imshow("edges_skl", lines_edges_skl)
#     cv2.waitKey(0)


def draw_lines(image_referential, lines):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    for line in lines:
        cv2.line(line_image, (line.x1, line.y1), (line.x2, line.y2), (255, 0, 0), 2)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    cv2.imshow("edges_skl", lines_edges_skl)
    cv2.waitKey(0)
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
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image3.png'
    image = cv2.imread(path)
    find_edge(image)
