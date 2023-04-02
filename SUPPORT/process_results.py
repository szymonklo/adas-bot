import datetime
import os
from typing import List

from PIL import Image


class Results:
    root = r'C:\PROGRAMOWANIE\auto_data\photos'

    def __init__(self, directory):
        self.list: List[Result] = list()
        self.path = os.path.join(Results.root, directory)
        self.max_size = 50

    def add_result(self, results):
        if results:
            if not isinstance(results, list):
                # results = list(results)
                self.list.append(results)
                return
            for result in results:
                if len(self.list) >= self.max_size:
                    self.list.pop(0)
                self.list.append(result)

    def current(self):
        return self.list[-1]

    def process(self):
        directory_path = prepare_dir(self.path)
        num = 0
        while len(self.list) > 0:
            # last_dist, last_trans, processed_image, dist, trans, diff, image_with_line, lane_borders, edge_found_status = self.list.pop(0)
            # processed_image, dist, trans, diff, image_with_line, lane_borders, edge_found_status = self.list.pop(0)
            r = self.list.pop(0)
            try:
                r.save(directory_path, num)
            except Exception as e:
                print(e)
                raise NotImplementedError(f'Result type not implemented yet for {type(r)}')
                raise NotImplementedError(f'Result type not implemented yet for tuple of length {len(r)}')
            num += 1


class Result:
    def __init__(self, processed_image):
        self.processed_image = processed_image

    def save(self, directory_path, num):
        if self.processed_image is not None:
            image_name = str(num).zfill(2) \
                         + '_raw' \
                         + '.png'
            Image.fromarray(self.processed_image).save(os.path.join(directory_path, image_name))


class Edge_results(Result):
    def __init__(self, processed_image, dist, trans, diff, image_with_line, lane_borders, edge_found_status):
        super().__init__(processed_image)
        self.dist = dist
        self.trans = trans
        self.diff = diff
        self.image_with_line = image_with_line
        self.lane_borders = lane_borders
        self.edge_found_status = edge_found_status

    # def dist(self):
    #     return self.__dist
    def save(self, directory_path, num):
        super().save(directory_path, num)

        if self.image_with_line is not None:
            image_name = str(num).zfill(2) \
                         + '_dst_' + safe_str(self.dist) \
                         + '_tra_' + safe_str(self.trans) \
                         + '_dif_' + safe_str(self.diff) \
                         + '.png'
            Image.fromarray(self.image_with_line).save(os.path.join(directory_path, image_name))


class Sign_results(Result):
    def __init__(self, processed_image, ref_digits_signs, mask, image, x, y, w, h, sign_image, rejected,
                 speed_limit_found, digit_images_list):
        # todo
        super().__init__(processed_image)
        self.ref_digits_signs = ref_digits_signs
        self.mask = mask
        self.image = image
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.sign_image = sign_image
        self.rejected = rejected
        self.speed_limit_found = speed_limit_found
        self.digit_images_list = digit_images_list

    def save(self, directory_path, num):
        super().save(directory_path, num)

        if self.sign_image is not None:
            image_name = str(num).zfill(2) \
                         + '_x_' + str(self.x) + '_y_' + str(self.y) + '_w_' + str(self.w) + '_h_' + str(self.h) \
                         + '_speed_' + str(self.speed_limit_found) \
                         + '_raw' \
                         + '.png'
            Image.fromarray(self.sign_image).save(os.path.join(directory_path, image_name))


class Plate_results(Result):
    def __init__(self, processed_image, lane_borders, plates_positions, img_with_contours_filtered, plate_distance,
                 min_plate_x, image_with_lane_and_plates):
        super().__init__(processed_image)
        self.lane_borders = lane_borders
        self.plates_positions = plates_positions
        self.img_with_contours_filtered = img_with_contours_filtered
        self.plate_distance = plate_distance
        self.min_plate_x = min_plate_x
        self.image_with_lane_and_plates = image_with_lane_and_plates

    # def dist(self):
    #     return self.__dist
    def save(self, directory_path, num):
        super().save(directory_path, num)

        if True:    # todo
            image_name = str(num).zfill(2) \
                         + 'cont' + '_y_' + str(self.plate_distance) + '_x_' + str(self.min_plate_x) \
                         + '.png'
            Image.fromarray(self.img_with_contours_filtered).save(os.path.join(directory_path, image_name))
            image_name = str(num).zfill(2) \
                         + 'plates' + '_y_' + str(self.plate_distance) + '_x_' + str(self.min_plate_x) \
                         + '.png'
            Image.fromarray(self.image_with_lane_and_plates).save(os.path.join(directory_path, image_name))


class Line_result(Results):
    def __init__(self, directory):
        Results.__init__(self, directory)
        # Edge_results.__init__(self, )

    def current(self) -> Edge_results:
        return self.list[-1]

    def previous(self) -> (Edge_results, None):
        if len(self.list) >= 2:
            return self.list[-2]
        else:
            return None

    # def dist(self) -> int:
    #     return self.current().dist
    #
    # def trans(self) -> int:
    #     return self.current().trans


def safe_str(value):
    if value is None:
        return str(value)
    elif isinstance(value, str):
        return value
    try:
        text = str(int(float(value)))
    except TypeError as e:
        text = 'type_error'
    except ValueError as e:
        text = 'value_error'
    return text


# todo - do not create empty dir
# legacy
def process_line_queue(results_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not results_queue.empty():
        last_dist, last_trans, processed_image, dist, trans, diff, image_with_line, lane_borders, edge_found_status = results_queue.get()
        if dist is None:
            dist = 0
        if processed_image is not None:
            image_name = str(num).zfill(2) \
                         + '_raw' \
                         + '.png'
            Image.fromarray(processed_image).save(os.path.join(directory_path, image_name))

        if image_with_line is not None:
            try:
                image_name = str(num).zfill(2) \
                             + '_dst_' + safe_str(dist) \
                             + '_tra_' + safe_str(trans) \
                             + '_dif_' + safe_str(diff) \
                             + '.png'
            except TypeError as e:
                print(e)
                image_name = str(num).zfill(2) \
                             + '.png'
            Image.fromarray(image_with_line).save(os.path.join(directory_path, image_name))
        num += 1


# legacy
def process_plates_queue(plates_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not plates_queue.empty():
        lane_borders, processed_image, plates_positions, img_with_contours_filtered, plate_distance, min_plate_x, image_with_lane_and_plates = plates_queue.get()
        image_name = str(num).zfill(2) \
                     + 'count' + '_y_' + str(plate_distance) + '_x_' + str(min_plate_x) \
                     + '.png'
        Image.fromarray(img_with_contours_filtered).save(os.path.join(directory_path, image_name))
        image_name = str(num).zfill(2) \
                     + 'plates' + '_y_' + str(plate_distance) + '_x_' + str(min_plate_x) \
                     + '.png'
        Image.fromarray(image_with_lane_and_plates).save(os.path.join(directory_path, image_name))
        num += 1


def process_signs_queue(signs_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not signs_queue.empty():
        ref_digits_signs, mask, image, x, y, w, h, sign_image, rejected, speed_limit_found, digit_images_list = signs_queue.get()
        if sign_image is not None:
            image_name = str(num).zfill(2) \
                         + '_x_' + str(x) + '_y_' + str(y) + '_w_' + str(w) + '_h_' + str(h) \
                         + '_speed_' + str(speed_limit_found) \
                         + '_raw' \
                         + '.png'
            Image.fromarray(sign_image).save(os.path.join(directory_path, image_name))
        num += 1


def process_rejected_queue(rejected_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not rejected_queue.empty():
        image_name, image = rejected_queue.get()
        Image.fromarray(image).save(os.path.join(directory_path, str(num).zfill(2) + image_name))
        num += 1


def process_digits_queue(digits_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not digits_queue.empty():
        image_name, image = digits_queue.get()
        Image.fromarray(image).save(os.path.join(directory_path, str(num).zfill(2) + image_name))
        num += 1


def prepare_dir(path, hour=True):
    directory_name = datetime.datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join(path, directory_name)
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
    if hour is True:
        directory_name = datetime.datetime.now().strftime('%H_%M_%S')
        directory_path = os.path.join(directory_path, directory_name)
        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

    return directory_path
