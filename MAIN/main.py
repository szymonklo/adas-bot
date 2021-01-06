import datetime
import time

import keyboard
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np


from CAPTURING.capture_image import capture_image
from CAPTURING.image_processing import process_image
from CONFIG.config import window
from IMAGE_PROCESSING.find_edge import find_edge_2
from LC.lane_centering import apply_correction


def run():
    while True:
        if keyboard.is_pressed('q'):
            keyboard.press('c')
            keyboard.release('c')
            last_dist = None
            while True:
                if keyboard.is_pressed('z'):
                    break
                last_dist = activate_assist(last_dist)


def activate_assist(last_dist=None):
    captured_image = capture_image(window)
    processed_image = process_image(captured_image)
    dist, degree, step, image_with_line = find_edge_2(processed_image, save=False, last_dist=last_dist)
    if dist is not None and degree is not None:
        direction, time_s, dis, deg, cha = apply_correction(dist, degree, last_dist, simulate=False)
        # if image_with_line is not None:
        #     path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
        #     path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') \
        #                 + '_tra_' + str(int(degree)) + '_dst_' + str(int(dist)) + '_max_' + str(int(step)) \
        #                 + 'tis' + str(time_s) + '.png'
        #     Image.fromarray(image_with_line).save(path_dist)
    return dist


def activate_assist_n_times(num=1):
    columns = [
        'distance',
        'degree',
        'step',
        'direction',
        'time_s',
        'dis',
        'deg',
        'cha',
        'operation_time',
    ]
    df = pd.DataFrame(columns=columns)
    last_dist = None
    for i in range(num):
        st = time.time()
        captured_image = capture_image(window)
        processed_image = process_image(captured_image)
        dist, degree, step, image_with_line = find_edge_2(processed_image, save=False, last_dist=last_dist)
        if dist is not None and degree is not None:
            direction, time_s, dis, deg, cha = apply_correction(dist, degree, last_dist, simulate=False)
            if image_with_line is not None:
                path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
                path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') \
                            + '_tra_' + str(int(degree)) + '_dst_' + str(int(dist)) + '_max_' + str(int(step)) \
                            + 'tis' + str(time_s) + '.png'
                Image.fromarray(image_with_line).save(path_dist)

            operation_time = time.time() - st
            degree = float(degree)
            step = float(step)
            row = [float(dist), degree, step, direction, time_s, dis, deg, cha, operation_time]
            row_df = pd.DataFrame([row], columns=columns)
            df = df.append(row_df)
        last_dist = dist

    keyboard.press_and_release('esc')
    x = np.linspace(0, len(df['dis']) - 1, len(df['dis']))

    pass
    plt.plot(x, df['dis'])
    plt.plot(x, df['cha'])


if __name__ == '__main__':
    run()
