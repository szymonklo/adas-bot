import datetime
import os

import cv2
import keyboard
import numpy as np
from PIL import Image

from CONFIG.config import ref_digits_path


# todo - class
def init_speed():
    ref_digits = {}
    files = os.listdir(ref_digits_path)
    for file in files:
        image = cv2.imread(os.path.join(ref_digits_path, file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image.astype(np.int16)
        ref_digits.update({file[:-4]: image})
    return ref_digits


def find_speed(image, ref_digits):
    x_sum = np.sum(image, axis=0)
    minimum_sum = 1.05 * np.mean(x_sum[:3])
    min_width = 5   # min width of single digits in pixels
    max_width = 10  # min width of single digits in pixels
    min_double_width = 12
    max_double_width = 22

    starts = []
    ends = []
    start = 0
    for index in range(1, len(x_sum)):
        if x_sum[index - 1] < minimum_sum <= x_sum[index]:
            start = index
            starts.append(start)
        if x_sum[index - 1] >= minimum_sum > x_sum[index]:
            if min_width <= index - start <= max_width:
                end = index - 1
                ends.append(end)
            elif min_double_width <= index - start <= max_double_width:
                new_minimum_index = np.argmin(x_sum[start + min_width: index - min_width]) + start + min_width
                end = new_minimum_index - 1
                ends.append(end)
                start = new_minimum_index + 1
                starts.append(start)
                end = index - 1
                ends.append(end)
                # keyboard.press_and_release('esc')
                d = 5

    if x_sum[-1] >= minimum_sum:
        if len(starts) - len(ends) == 1:
            if len(x_sum) - starts[-1] >= min_width:
                ends.append(len(x_sum) - 1)
            elif len(starts) > 0:
                starts.pop()

    digit_images = []
    digits = ['']
    if len(starts) == len(ends):
        for start, end in zip(starts, ends):
            if end - start >= min_width:
                if end - start <= max_width:
                    digit_image = image[:, start: end + 1]
                    digit_images.append(digit_image)
                    digit = find_digit(digit_image, ref_digits)
                    if digit is not None:
                        if digit in '0123456789':
                            digits.append(digit)
                else:
                    # keyboard.press_and_release('esc')
                    d = 3
            else:
                # keyboard.press_and_release('esc')
                d = 4
    else:
        # keyboard.press_and_release('esc')
        d=2

    if digits != ['']:
        speed = int(''.join(digits))
        # print(speed)
        return speed
    return None  # temp


def find_limits(x_sum, minimum_sum, min_width, first_index=1, last_index=-1):
    starts = []
    ends = []
    for index in range(1, len(x_sum)):
        if x_sum[index - 1] < minimum_sum <= x_sum[index]:
            starts.append(index)
        if x_sum[index - 1] >= minimum_sum > x_sum[index]:
            ends.append(index - 1)
    if x_sum[-1] >= minimum_sum:
        if len(starts) - len(ends) == 1:
            if len(x_sum) - starts[-1] >= min_width:
                ends.append(len(x_sum) - 1)
            elif len(starts) > 0:
                starts.pop()

    return starts, ends

# 122, 102, 92, 87(67), 86(30, 60), 85(65, 35), 84(34),
def find_digit(digit_image, ref_digits):
    diffs = {}
    minimum = ('-1', 255 * digit_image.shape[0] * digit_image.shape[1])
    mini = []
    for digit, image in ref_digits.items():
        if digit_image.shape[1] == image.shape[1]:
            diffs[digit] = np.sum(abs(image - digit_image))
            if diffs[digit] < minimum[1]:
                minimum = (digit, diffs[digit])
    if minimum[1] > 2000:
        for digit, image in ref_digits.items():
            if digit_image.shape[1] + 1 == image.shape[1]:
                diffs_1 = np.sum(abs(image[:, :-1] - digit_image))
                diffs_2 = np.sum(abs(image[:, 1:] - digit_image))
                diffs[digit] = min(diffs_1, diffs_2)
                if diffs[digit] < minimum[1]:
                    minimum = (digit, diffs[digit])
        # keyboard.press_and_release('esc')
        d=1

    path = r'C:\PROGRAMOWANIE\auto_data\photos\digits\\' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')\
           + 'sum' + str(minimum[1]) + 'dig' + minimum[0] + '.png'

    # Image.fromarray(digit_image).save(path)
    if minimum[0] != '-1':
        return minimum[0]
    else:
        return None
