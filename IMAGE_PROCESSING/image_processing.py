import os
import time

import numpy as np
import cv2
from PIL import Image


def process_image_to_array(image):
    processed_image_1 = Image.frombytes("RGB", (image.width, image.height), image.rgb)
    processed_image_2 = np.array(processed_image_1)

    return processed_image_2


def process_image_to_grayscale(image):
    processed_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # hsv = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)
    # h = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 0]
    # s = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 1]
    # v = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 2]

    # hsl = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HLS)
    # l = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HLS)[:, :, 1]
    return processed_image


def binarize(image):
    ret, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    return binary_image


def filter_image(image, debug=False):
    hsv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)

    if debug is True:
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]

    # lower_red = np.array([160, 150, 0])
    # upper_red = np.array([179, 255, 255])
    lower_red = np.array([0, 150, 0])
    upper_red = np.array([20, 255, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)

    result = cv2.bitwise_and(image, image, mask=mask)
    # result = cv2.cvtColor(np.array(result), cv2.COLOR_BGR2RGB)

    # cv2.imshow('image', image)
    # cv2.imshow('mask', mask)
    # cv2.imshow('result', result)
    mask2 = mask.copy()
    image2 = image.copy()
    # find_circles(mask2, image2)

    return mask2, image2


def filter_image2(image, lower_hsv, upper_hsv, debug=False):
    hsv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2HSV)

    if debug is True:
        h = hsv[:, :, 0]
        s = hsv[:, :, 1]
        v = hsv[:, :, 2]

    # lower_red = np.array([160, 150, 0])
    # upper_red = np.array([179, 255, 255])
    lower = np.array(lower_hsv)
    upper = np.array(upper_hsv)

    mask = cv2.inRange(hsv, lower, upper)

    height, width, depth = image.shape
    circle = np.zeros((height, width), dtype=np.uint8)
    r = int(min(width // 2, height // 2) * 0.8)
    cv2.circle(circle, (width // 2, height // 2), r, 1, thickness=-1)

    mask_with_circle = cv2.bitwise_and(mask, mask, mask=circle)

    result = cv2.bitwise_and(image, image, mask=mask)
    # result = cv2.cvtColor(np.array(result), cv2.COLOR_BGR2RGB)

    # cv2.imshow('image', image)
    # cv2.imshow('mask', mask)
    # cv2.imshow('result', result)
    mask2 = mask.copy()
    image2 = image.copy()
    # find_circles(mask2, image2)

    return mask2, image2, mask_with_circle


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\sr\2021-01-18\15_10_03'
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                # image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

                lower_hsv = np.array([0, 0, 0])
                upper_hsv = np.array([255, 255, 75])

                mask, image = filter_image2(image, lower_hsv, upper_hsv, debug=True)
                # filtered_image = filter_image(image, debug=True)
                print(f'F: {time.time() - st}')
