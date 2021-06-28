import datetime
import os

import cv2
import keyboard
import numpy as np
from PIL import Image


def init_speed(path):
    ref_digits = {}
    files = os.listdir(path)
    for file in files:
        image = cv2.imread(os.path.join(path, file))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # image = image.astype(np.int16)
        image = image.astype(np.uint8)
        ref_digits.update({file[:-4]: image})
    return ref_digits


def find_speed(image, ref_digits, minimum_sum=None, widths=None, axis=0):
    # if image.shape[0] != 18:
    # keyboard.press_and_release('esc')
    digit_images = find_digit_images(image, ref_digits, minimum_sum=minimum_sum, widths=widths, axis=axis)

    digits = ['']
    for digit_image in digit_images:
        digit = find_digit(digit_image, ref_digits, axis=axis)
        if digit is not None:
            if digit in '0123456789':
                digits.append(digit)

    if digits != ['']:
        spd_str = ''.join(digits)
        # if '8' in spd_str:
        #     keyboard.press_and_release('esc')
        #     d1=1
        speed = int(spd_str)
        # print(speed)

        return speed
    return None  # temp


def find_speed2(digit_images, ref_digits_signs, axis=1):

    digits = ['']
    for digit_image in digit_images:
        # keyboard.press_and_release('esc')
        digit = find_digit(digit_image, ref_digits_signs, axis=axis)
        if digit is not None:
            if digit in '0123456789':
                digits.append(digit)

    if digits != ['']:
        speed = int(''.join(digits))
        print(speed)
        # keyboard.press_and_release('esc')
        return speed
    return None  # temp


def find_digit_images(image, ref_digits, minimum_sum=None, widths=None, axis=0):
    x_sum = np.sum(image, axis=axis)
    if minimum_sum is None:
        minimum_sum = min(x_sum) + 1.05 * np.mean(x_sum - min(x_sum))*0.35
        # minimum_sum = 255*0.5*image.shape[1-axis]
    if widths is None:
        min_width = 5   # min width of single digits in pixels
        max_width = 10  # min width of single digits in pixels
        min_double_width = 12
        max_double_width = 22
    else:
        min_width, max_width, min_double_width, max_double_width = widths

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
                    if axis == 0:
                        digit_image = image[:, start: end + 1]
                    elif axis == 1:
                        digit_image = image[start: end + 1, :]
                    digit_images.append(digit_image)
                else:
                    # keyboard.press_and_release('esc')
                    d = 3
            else:
                # keyboard.press_and_release('esc')
                d = 4
    else:
        # keyboard.press_and_release('esc')
        d=2

    return digit_images


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
def find_digit(digit_image, ref_digits, axis=0):
    # todo 2021-06-27:  after debug move astype(int) outside
    diffs = {}
    minimum = ('-1', 255 * digit_image.shape[0] * digit_image.shape[1])
    mini = []
    if digit_image.shape[0] != ref_digits['0'].shape[0]:
        # digit_image = cv2.resize(digit_image, (ref_digits['0'].shape[0], int(digit_image.shape[1] * ref_digits['0'].shape[0] / digit_image.shape[0])))
        digit_image = cv2.resize(digit_image, (ref_digits['0'].shape[1], ref_digits['0'].shape[0]))
    for digit, image in ref_digits.items():
        if digit_image.shape[1] == image.shape[1]:
            print(np.sum(abs(image.astype(int) - digit_image.astype(int))))
            diffs[digit] = np.sum(abs(image.astype(int) - digit_image.astype(int)))
            if diffs[digit] < minimum[1]:
                minimum = (digit, diffs[digit])
    if minimum[1] > 2000:
        for digit, image in ref_digits.items():
            if digit_image.shape[1] + 1 == image.shape[1]:
                diffs_1 = np.sum(abs(image[:, :-1].astype(int) - digit_image.astype(int)))
                diffs_2 = np.sum(abs(image[:, 1:].astype(int) - digit_image.astype(int)))
                diffs[digit] = min(diffs_1, diffs_2)
                if diffs[digit] < minimum[1]:
                    minimum = (digit, diffs[digit])
    if minimum[1] > 2000:
        for digit, image in ref_digits.items():
            if digit_image.shape[1] - 1 == image.shape[1]:
                diffs_1 = np.sum(abs(image.astype(int) - digit_image[:, :-1].astype(int)))
                diffs_2 = np.sum(abs(image.astype(int) - digit_image[:, 1:].astype(int)))
                diffs[digit] = min(diffs_1, diffs_2)
                if diffs[digit] < minimum[1]:
                    minimum = (digit, diffs[digit])
        # keyboard.press_and_release('esc')
        d=1

    path = r'C:\PROGRAMOWANIE\auto_data\photos\sign_digits\\' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')\
           + 'sum' + str(minimum[1]) + 'dig' + minimum[0] + '.png'

    if digit_image.shape[0] != 18:#len(ref_digits) < 10:
        Image.fromarray(digit_image).save(path)
    if minimum[0] != '-1':
        return minimum[0]
    else:
        return None
