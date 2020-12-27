import cv2
import numpy as np
from PIL import Image
from math import sin, cos, pi

def find_edge(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    draw_line(image, x1=385, y1=20, alpha=270, length=120)
    line_1 = Line(x1=385, y1=20, alpha=270, length=120)
    line_2 = Line(x1=385, y1=20, alpha=180, length=20)
    draw_lines(image, [line_1, line_2])
    pass


def draw_line(image_referential, x1, y1, alpha, length):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    # x1, y1 = 385, 20
    x2 = x1 - int(length * cos(pi * alpha / 180))
    y2 = y1 - int(length * sin(pi * alpha / 180))
    # x2, y2 = 385, 140
    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    cv2.imshow("edges_skl", lines_edges_skl)
    cv2.waitKey(0)


def draw_lines(image_referential, lines):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    # x1, y1 = 385, 20
    # x2 = x1 - int(length * cos(pi * alpha / 180))
    # y2 = y1 - int(length * sin(pi * alpha / 180))
    # x2, y2 = 385, 140
    for line in lines:
        x1 = line.x1
        y1 = line.y1
        x2 = line.x1 - int(line.length * cos(pi * line.alpha / 180))
        y2 = line.y1 - int(line.length * sin(pi * line.alpha / 180))
        cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    cv2.imshow("edges_skl", lines_edges_skl)
    cv2.waitKey(0)


class Line:
    def __init__(self, x1, y1, alpha, length):
        self.x1 = x1
        self.y1 = y1
        self.alpha = alpha
        self.length = length



if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image3.png'
    image = cv2.imread(path)
    find_edge(image)
