import copy
import math
import os
import time
import keyboard

import cv2
import numpy as np

from IMAGE_PROCESSING.SPEED_DETECTION.detect_speed import find_speed, find_digit_images, find_speed2
from IMAGE_PROCESSING.image_processing import filter_image2


def find_circles(mask, image):
    # todo - 1. circle vs triangle vs rectangle
    #        2. join split contours?
    # circles = cv2.HoughCircles(image=mask, method=cv2.HOUGH_GRADIENT, dp=1, minDist=1)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_filtered = [cnt for cnt in contours if cnt.shape[0] > 40]

    # img = cv2.drawContours(image, contours_filtered, -1, (0, 255, 0), 1)
    # cv2.imshow('cnt', img)
    # cv2.waitKey(0)

    if len(contours_filtered) > 0:
        contour_desc = sorted(contours_filtered, key=len, reverse=True)
        for cnt in contour_desc:
            # todo: check if min dimension reached
            im_with_count = copy.deepcopy(image)
            im_with_count = cv2.drawContours(im_with_count, cnt, -1, (0, 255, 0), 1)
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 40 and h > 40:
                perimeter = cv2.arcLength(cnt, closed=True)
                (x_mec, y_mec), radius = cv2.minEnclosingCircle(cnt)
                x_mec, y_mec, radius = int(x_mec), int(y_mec), int(radius)

                cnt_2 = cnt[:, 0, :]
                x_mec_arr = np.full(cnt_2.shape[0], x_mec)
                y_mec_arr = np.full(cnt_2.shape[0], y_mec)
                x2 = np.square(cnt_2[:, 0] - x_mec_arr)
                y2 = np.square(cnt_2[:, 1] - y_mec_arr)
                dist_from_center = np.sqrt(x2 + y2)
                deviation = (dist_from_center - radius) / radius
                avg_dev = abs(np.mean(deviation))

                if avg_dev < 0.2:

                    max_additional_length_vs_circle = 0.05
                    circle_perieter = 2 * math.pi * radius

                    circularity = abs(perimeter - circle_perieter) / circle_perieter

                    if abs(perimeter - circle_perieter) < max_additional_length_vs_circle * circle_perieter:
                        x = x_mec - radius
                        y = y_mec - radius
                        w = 2 * radius
                        h = 2 * radius

                        sign_image = image[y: y + h, x: x + w, :]
                        print(time.time())
                        # keyboard.press_and_release('esc')

                        return x, y, w, h, sign_image

    return None, None, None, None, None

    m = cv2.moments(contour_max)
    cx = int(m["m10"] / m["m00"])
    cy = int(m["m01"] / m["m00"])

    image_cm = cv2.circle(image, (cx, cy), 1, (255, 0, 0), 1)

    # cv2.imshow('center_of_mass', image_cm)
    # cv2.waitKey(0)

    (x, y), radius = cv2.minEnclosingCircle(contour_max)
    center = (int(x), int(y))
    radius = int(radius)

    dist_cm_to_cmec = int(((x-cx)**2 + (y-cy)**2)**(1/2))
    print(dist_cm_to_cmec)

    img_circle = cv2.circle(image_cm, center, radius, (0, 0, 255), 1)
    img_circle = cv2.circle(img_circle, center, 1, (0, 0, 255), 1)
    cv2.imshow('circle', img_circle)
    cv2.waitKey(0)


    pass


def prepare_sign_to_digits_recognition(image):
    lower_hsv = np.array([0, 0, 0])
    upper_hsv = np.array([255, 255, 60])

    mask, image, mask_with_circle = filter_image2(image, lower_hsv, upper_hsv, debug=True)

    return mask_with_circle


def find_speed_limit(sign_image, ref_digits_signs):
    sign_image_filtered = prepare_sign_to_digits_recognition(sign_image)
    width = sign_image_filtered.shape[1]
    widths = int(0.15 * width), int(0.35 * width), int(0.4 * width), int(0.6 * width)
    digit_images_split_h = find_digit_images(sign_image_filtered, ref_digits={}, minimum_sum=int(0.2 * width), widths=widths)
    digit_images = []
    for digit_image_h in digit_images_split_h:
        width = digit_image_h.shape[0]
        widths = int(0.2 * width), int(0.45 * width), int(0.5 * width), int(0.7 * width)
        # digit_image = find_digit_images(digit_image_h, ref_digits={}, minimum_sum=int(0.2 * width), widths=widths, axis=1)[0]
        digit_images_split_v = find_digit_images(digit_image_h, ref_digits={}, minimum_sum=int(0.2 * width), widths=widths, axis=1)
        if digit_images_split_v is not None:
            if len(digit_images_split_v) >= 1:
                digit_image = digit_images_split_v[0]
                if digit_image is not None:
                    digit_images.append(digit_image)
    target_speed = find_speed2(digit_images, ref_digits_signs=ref_digits_signs, axis=1)

    return target_speed


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\sr\2021-01-18\15_10_03'
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                # image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

                target_speed = find_speed_limit(image)
                # filtered_image = filter_image(image, debug=True)
                print(f'F: {time.time() - st}')
