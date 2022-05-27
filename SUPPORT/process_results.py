import datetime
import os
from PIL import Image


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


def process_plates_queue(plates_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not plates_queue.empty():
        lane_borders, processed_image, plates_positions, img_with_contours_filtered, plate_distance, min_plate_x, image_with_lane_and_plates = plates_queue.get()
        image_name = str(num).zfill(2) \
                     + '_y_' + str(plate_distance) + '_x_' + str(min_plate_x) \
                     + '.png'
        Image.fromarray(img_with_contours_filtered).save(os.path.join(directory_path, image_name))
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
