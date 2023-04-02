import cv2
import numpy as np


def find_digits_and_speed(image, ref_digits):
    digit_images = find_digit_images(image, minimum_sum=None, widths=None, axis=0)
    speed, result_images_list = find_speed_from_digit_images(digit_images, ref_digits, minimum=0)
    return speed, result_images_list


def find_speed_from_digit_images(digit_images, ref_digits, minimum=10):
    digits = ['']
    result_images_list = []
    for i, digit_image in enumerate(digit_images):
        # todo - if 2nd of 2 digits or 3rd of 3 digits not detected -> assume 0
        digit, result_image_set = find_digit(digit_image, ref_digits)
        if result_image_set:
            result_images_list.append(result_image_set)
        if digit is not None:
            if digit in '0123456789':
                digits.append(digit)
        elif (len(digit_images) == 2 and i == 1) or (len(digit_images) == 3 and i == 2):
            digit = '0'
            digits.append(digit)

    if digits != ['']:
        spd_str = ''.join(digits)
        speed = int(spd_str)
        if speed >= minimum and (not spd_str.startswith('1') or len(spd_str) > 2):
            return speed, result_images_list
    return None, result_images_list


def find_digit_images(image, minimum_sum=None, widths=None, axis=0):
    x_sum = np.sum(image, axis=axis)
    if minimum_sum is None:  # None for cluster, specified for sign
        minimum_sum = min(x_sum) + 1.05 * np.mean(x_sum - min(x_sum)) * 0.35
        # minimum_sum = 255*0.5*image.shape[1-axis]
    if widths is None:  # None for cluster, specified for sign
        min_width = 5  # min width of single digits in pixels
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
                d = 5

    if x_sum[-1] >= minimum_sum:
        if len(starts) - len(ends) == 1:
            if len(x_sum) - starts[-1] >= min_width:
                ends.append(len(x_sum) - 1)
            elif len(starts) > 0:
                starts.pop()

    digit_images = []
    if len(starts) == len(ends):
        for start, end in zip(starts, ends):
            if end - start >= min_width:
                if end - start <= max_width:
                    if axis == 0:
                        digit_image = image[:, start: end + 1]
                    elif axis == 1:
                        digit_image = image[start: end + 1, :]
                    else:
                        raise NotImplementedError
                    digit_images.append(digit_image)
                else:
                    d = 3
            else:
                d = 4
    else:
        d = 2

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


def find_digit(digit_image, ref_digits):
    # todo 2021-06-27:  after debug move astype(int) outside
    result_image_set = set()
    height, width = digit_image.shape
    diffs = {}
    # minimum = ('-1', 255 * digit_image.shape[0] * digit_image.shape[1])
    minimum = ('-1', 10000)
    if height != ref_digits['0'].shape[0]:
        # digit_image = cv2.resize(digit_image, (ref_digits['0'].shape[0], int(digit_image.shape[1] * ref_digits['0'].shape[0] / digit_image.shape[0])))
        digit_image = cv2.resize(digit_image, (ref_digits['0'].shape[0] * width // height, ref_digits['0'].shape[0]))
    height, width = digit_image.shape
    for ref_digit, ref_image in ref_digits.items():
        if width == ref_image.shape[1]:
            # print(np.sum(abs(image.astype(int) - digit_image.astype(int))))
            diffs[ref_digit] = np.sum(abs(ref_image.astype(int) - digit_image.astype(int)))
            if diffs[ref_digit] < minimum[1]:
                minimum = (ref_digit, diffs[ref_digit])
    if minimum[1] > 2000:
        for ref_digit, ref_image in ref_digits.items():
            if width + 1 == ref_image.shape[1]:
                diffs_1 = np.sum(abs(ref_image[:, :-1].astype(int) - digit_image.astype(int)))
                diffs_2 = np.sum(abs(ref_image[:, 1:].astype(int) - digit_image.astype(int)))
                diffs[ref_digit] = min(diffs_1, diffs_2)
                if diffs[ref_digit] < minimum[1]:
                    minimum = (ref_digit, diffs[ref_digit])
    if minimum[1] > 2000:
        for ref_digit, ref_image in ref_digits.items():
            if width - 1 == ref_image.shape[1]:
                diffs_1 = np.sum(abs(ref_image.astype(int) - digit_image[:, :-1].astype(int)))
                diffs_2 = np.sum(abs(ref_image.astype(int) - digit_image[:, 1:].astype(int)))
                diffs[ref_digit] = min(diffs_1, diffs_2)
                if diffs[ref_digit] < minimum[1]:
                    minimum = (ref_digit, diffs[ref_digit])
    image_name = 'sum' + str(minimum[1]) + 'dig' + minimum[0] + '.png'
    # path = r'C:\PROGRAMOWANIE\auto_data\photos\sign_digits\\' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')\
    #        + image_name

    if height != 18:  # len(ref_digits) < 10:      #probably cluster?
        result_image_set = (image_name, digit_image)
    #     Image.fromarray(digit_image).save(path)
    if minimum[0] != '-1' and minimum[1] < 10000:
        return minimum[0], result_image_set
    else:
        return None, result_image_set
