import datetime
import os

import keyboard
from PIL import Image


def process_results_queue(results_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not results_queue.empty():
        processed_image, image_with_line, dist, trans, diff, dist_cor, trans_cor, change_cor, direction, time_s = results_queue.get()
        if processed_image is not None:
            image_name = str(num) \
                         + '_raw'\
                         + '.png'
            Image.fromarray(processed_image).save(os.path.join(directory_path, image_name))

        if image_with_line is not None:
            image_name = str(num) \
                         + '_dst_' + str(int(dist)) + '_tra_' + str(int(trans))  + '_dif_' + str(int(diff)) \
                         + '_dstC_' + str(int(dist_cor)) + '_traC_' + str(int(trans_cor)) + '_chaC_' + str(int(change_cor)) \
                         + '_dir_' + direction + '_tim_' + str(int(time_s))\
                         + '.png'
            Image.fromarray(image_with_line).save(os.path.join(directory_path, image_name))
        num += 1
    return processed_image


def process_signs_queue(signs_queue, path):
    directory_path = prepare_dir(path)
    num = 0
    while not signs_queue.empty():
        # keyboard.press_and_release('esc')
        x, y, w, h, sign_image, target_speed = signs_queue.get()
        if sign_image is not None:
            image_name = str(num) \
                         + '_x_' + str(x) + '_y_' + str(y) + '_w_' + str(w) + '_h_' + str(h) \
                         + '_speed_' + str(target_speed) \
                         + '_raw'\
                         + '.png'
            Image.fromarray(sign_image).save(os.path.join(directory_path, image_name))
        num += 1


def prepare_dir(path):
    directory_name = datetime.datetime.now().strftime('%Y-%m-%d')
    directory_path = os.path.join(path, directory_name)
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
    directory_name = datetime.datetime.now().strftime('%H_%M_%S')
    directory_path = os.path.join(directory_path, directory_name)
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)

    return directory_path
