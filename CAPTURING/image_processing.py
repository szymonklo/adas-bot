import time

import imutils as imutils
import numpy as np
import cv2
from mss import mss
from PIL import Image
import keyboard


def process_image(image):
    processed_image_1 = Image.frombytes("RGB", (image.width, image.height), image.rgb)
    processed_image_2 = np.array(processed_image_1)
    processed_image = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_RGB2BGR)
    return processed_image

def image_processing():
    start_time = time.time()
    window = {
        'left': 0,
        'top': 0,
        'width': 1920,
        'height': 1080
    }
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image1.png'

    img = Image.open(path)
    img_array = np.array(img)
    image_RGB = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # cv2.imshow('test', img_array)
    # time.sleep(5)
    # cv2.imshow('test', image)
    # time.sleep(5)

    image_BGR = cv2.imread(path)
    # cv2.imshow('raw', image_BGR)
    # cv2.waitKey(0)


    x_center = 1920/2
    y_center = 1080/2-50
    width = 160*4
    height = 90*2

    array_cropped = image_BGR[int(y_center-height/2):int(y_center+height/2), int(x_center-width/2):int(x_center+width/2)]
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image3.png'
    # image_cropped = Image.fromarray(array_cropped, cv2.COLOR_RGB2BGR)
    image_cropped = cv2.cvtColor(array_cropped, cv2.COLOR_RGB2BGR)
    image_cropped = Image.fromarray(image_cropped)

    image_cropped.save(path)
    # cv2.imshow('cropped', image_cropped)

    image_gray = cv2.cvtColor(array_cropped, cv2.COLOR_BGR2GRAY)
    # image_auto_canny = auto_canny(image_gray)
    # cv2.imshow("Screenshot", imutils.resize(image_auto_canny, width=1000))
    # cv2.waitKey(0)

    # ls_detector = cv2.createLineSegmentDetector()
    # lines = ls_detector.detect(image_gray)
    # segments = ls_detector.drawSegments(input, lines)
    # cv2.imshow("input", segments)
    # cv2.waitKey(0)


    # hough(image_gray, image_cropped)

    find_line(image_gray, array_cropped)

    print(str(time.time() - start_time))
    pass


def find_line(image_gray, image_referential):
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on
    x1, y1 = 385, 20
    x2, y2 = 385, 140
    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)
    lines_edges_skl = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    cv2.imshow("edges_skl", lines_edges_skl)
    cv2.waitKey(0)


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged


def hough(image_gray, image_referential):
    kernel_size = 5
    blur_gray = cv2.GaussianBlur(image_gray, (kernel_size, kernel_size), 0)

    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    # cv2.imshow("canny", edges)
    # cv2.waitKey(0)

    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 180  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments
    line_image = np.copy(image_referential) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)



    print(lines)
    points = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            points.append(((x1 + 0.0, y1 + 0.0), (x2 + 0.0, y2 + 0.0)))
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)

    lines_edges = cv2.addWeighted(image_referential, 0.8, line_image, 1, 0)
    # print(lines_edges.shape)
    # cv2.imwrite('line_parking.png', lines_edges)

    # print
    # points
    # intersections = bot.isect_segments(points)
    # print
    # intersections
    #
    # for inter in intersections:
    #     a, b = inter
    #     for i in range(3):
    #         for j in range(3):
    #             lines_edges[int(b) + i, int(a) + j] = [0, 255, 0]


    cv2.imshow("edges", lines_edges)
    cv2.waitKey(0)


if __name__ == '__main__':
    image_processing()
