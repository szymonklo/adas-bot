import time
import keyboard
import pandas as pd

from CAPTURING.capture_image import capture_image
from CAPTURING.image_processing import process_image
from CONFIG.config import window, window_lc, window_crop_margin
from IMAGE_PROCESSING.find_edge import find_edge, find_vertical_edge
from IMAGE_PROCESSING.perspective import perspective
from LC.lane_centering import apply_correction


def run():
    assist_active = False
    ts = time.time()
    while True:
        # try:  # used try so that if user pressed other than the given key error will not be shown
        if keyboard.is_pressed('q'):  # if key 'q' is pressed
            keyboard.press('c')     # constant speed
            keyboard.release('c')

            assist_active = True
            while assist_active:
                tn = time.time()
                if keyboard.is_pressed('z'):
                    assist_active = False
                    break
                if not keyboard.is_pressed('z') and assist_active:
                    if tn-ts > 1:
                        activate_assist(num=100)
                        ts = time.time()

            # break
        # except:
        #     pass


def activate_assist(num=1):
    distance = []
    degrees = []
    columns = [
        'distance',
        'degree',
        'direction',
        'time_s',
        'operation_time',
    ]
    df = pd.DataFrame(columns=columns)
    for i in range(num):
        start_time = time.time()
        captured_image = capture_image(window_lc)
        processed_image = process_image(captured_image)
        # perspective_image = perspective(processed_image)
        dist, degree = find_edge(processed_image, save=True)
        # distance.append(dist)
        # degrees.append(degree)
        # df.at[i, 'distance'] = dist

        # dist, max_diff = find_vertical_edge(perspective_image, processed_image)

        direction, time_s = apply_correction(dist, simulate=False)
        time.sleep(0.2)
        operation_time = time.time() - start_time

        row = [dist, degree, direction, time_s, operation_time]
        row_df = pd.DataFrame([row], columns=columns)
        df = df.append(row_df)

        # if operation_time < 1:
        #     time.sleep(1 - operation_time)
    pass


if __name__ == '__main__':
    run()
    print('q')
