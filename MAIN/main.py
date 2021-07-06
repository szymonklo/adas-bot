import datetime
import os
import time
import queue
import keyboard

from PIL import Image

from CC.cruise_control import change_speed
from IMAGE_PROCESSING.CAPTURING.capture_image import capture_image
from IMAGE_PROCESSING.PLATES_DETECTION.detect_plate import detect_plate, judge_plates_positions
from IMAGE_PROCESSING.SIGN_RECOGNITION.sign_recognition import find_circles, prepare_sign_to_digits_recognition, \
    find_speed_limit
from IMAGE_PROCESSING.SPEED_DETECTION.detect_speed import find_current_speed, init_speed, find_digit_images
from IMAGE_PROCESSING.image_processing import process_image_to_array, process_image_to_grayscale, filter_image
from CONFIG.config import window, window_speed, Keys, window_signs, RefDigitsPath, window_plates
from IMAGE_PROCESSING.LINE_DETECTION.find_edge import find_edge, find_curvy_edge
from LC.lane_centering import apply_correction
from SUPPORT.process_results import process_results_queue, process_signs_queue, prepare_dir


def run():
    target_speed = 50
    ref_digits, ref_digits_signs = init_ref_digits()
    plate_distance = None

    while True:
        if keyboard.is_pressed('q'):
            results_queue = queue.Queue(50)
            signs_queue = queue.Queue(50)
            last_dist = None
            while True:
                processed_image = None
                if keyboard.is_pressed('z'):
                    keyboard.release(Keys.up)
                    keyboard.release(Keys.down)
                    keyboard.release(Keys.left)
                    keyboard.release(Keys.right)
                    # keyboard.press_and_release('esc')
                    processed_image_deb = process_results_queue(results_queue, r'C:\PROGRAMOWANIE\auto_data\photos\lc')
                    process_signs_queue(signs_queue, r'C:\PROGRAMOWANIE\auto_data\photos\sr')
                    break
                # todo - if 'a' or 'd' pressed turn off
                # todo - if indicators pressed change line (turn off, arrow dir1 for 1 s, arrow dir2 for 1 s, turn on)

                if keyboard.is_pressed('o'):
                    # keyboard.press_and_release('esc')
                    directory_path = prepare_dir(r'C:\PROGRAMOWANIE\auto_data\photos\o', hour=False)

                    image_name = datetime.datetime.now().strftime('%H_%M_%S')
                    image_name += '.png'
                    captured_image = capture_image(window_plates)
                    processed_image = process_image_to_array(captured_image)
                    if processed_image is not None:

                        Image.fromarray(processed_image).save(os.path.join(directory_path, image_name))

                st_lc = time.time()
                action_results = activate_assist(last_dist)
                lane_borders = action_results[-1]
                last_dist = action_results[2]
                print(f'LC: {time.time() - st_lc}')

                st_cc = time.time()
                speed = activate_speed(target_speed, ref_digits, plate_distance)
                print(f'CC: {time.time() - st_cc}, speed: {speed}, target_speed: {target_speed}')

                st_acc = time.time()
                plate_distance = activate_plate(lane_borders)
                print(f'AC: {time.time() - st_acc}, plate_distance: {plate_distance}')

                if results_queue.full():
                    results_queue.get()
                results_queue.put(action_results)

                st_sr = time.time()
                signs_results = activate_signs(ref_digits_signs)
                x, y, w, h, sign_image, target_speed_found = signs_results
                if target_speed_found is not None:
                    target_speed = target_speed_found
                    if signs_queue.full():
                        signs_queue.get()
                    signs_queue.put(signs_results)
                print(f'SR: {time.time() - st_sr}, x: {x}, y: {y}, w: {w}, h: {h}, speed_limit: {target_speed_found}')


def init_ref_digits():
    ref_digits = init_speed(RefDigitsPath.cluster)
    ref_digits_signs1 = init_speed(RefDigitsPath.signs)
    ref_digits_signs = {}

    for digit, ref_digits_sign1 in ref_digits_signs1.items():
        width = ref_digits_sign1.shape[0]
        if width != 15:
            widths = 9, 18, int(0.4 * width), int(0.6 * width)
            ref_digits_sign = find_digit_images(ref_digits_sign1, ref_digits={}, widths=widths, axis=1)
            ref_digits_signs[digit] = ref_digits_sign[0]
        else:
            ref_digits_signs[digit] = ref_digits_sign1

    return ref_digits, ref_digits_signs


def activate_plate(lane_borders):
    # lane width 300 (step 0)
    # lane width 150 (step 6) -> -25/step
    captured_image = capture_image(window)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    plates_positions = detect_plate(processed_image)
    plate_distance = judge_plates_positions(plates_positions, lane_borders)

    return plate_distance


def activate_assist(last_dist=None):
    captured_image = capture_image(window)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    # dist, trans, diff, image_with_line = find_edge(processed_image, save=False, last_dist=last_dist)
    dist, trans, diff, image_with_line, lane_borders = find_curvy_edge(processed_image, save=False, last_dist=last_dist)
    if dist is not None:
        direction, time_s, dist_cor, degree_cor, change_cor = apply_correction(dist, trans, last_dist, simulate=False)
    else:
        dist_cor, degree_cor, change_cor, direction, time_s = None, None, None, None, None

    return processed_image, image_with_line, dist, trans, diff, dist_cor, degree_cor, change_cor, direction, time_s, lane_borders


def activate_speed(target_speed, ref_digits, plate_distance):
    captured_image = capture_image(window_speed)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    # binary_image = binarize(processed_image)
    # keyboard.press_and_release('esc')
    current_speed = find_current_speed(processed_image, ref_digits)
    change_speed(target_speed, current_speed, plate_distance)
    return current_speed


def activate_signs(ref_digits_signs):
    captured_image = capture_image(window_signs)
    # keyboard.press_and_release('esc')
    processed_image = process_image_to_array(captured_image)
    mask, image = filter_image(processed_image)
    x, y, w, h, sign_image = find_circles(mask, image)
    # sign_image = image[y: y + h, x: x + w, :]
    # binary_image = binarize(processed_image)
    # keyboard.press_and_release('esc')
    target_speed = None
    if sign_image is not None:
        target_speed = find_speed_limit(sign_image, ref_digits_signs)
    return x, y, w, h, sign_image, target_speed


# def activate_assist_n_times(num=1):
#     columns = [
#         'distance',
#         'degree',
#         'step',
#         'direction',
#         'time_s',
#         'dis',
#         'deg',
#         'cha',
#         'operation_time',
#     ]
#     df = pd.DataFrame(columns=columns)
#     last_dist = None
#     for i in range(num):
#         st = time.time()
#         captured_image = capture_image(window)
#         processed_image = process_image_to_array(captured_image)
#         processed_image = process_image_to_grayscale(processed_image)
#         dist, degree, step, image_with_line = find_edge(processed_image, save=False, last_dist=last_dist)
#         if dist is not None and degree is not None:
#             direction, time_s, dis, deg, cha = apply_correction(dist, degree, last_dist, simulate=False)
#             if image_with_line is not None:
#                 path = r'C:\PROGRAMOWANIE\auto_data\photos\image'
#                 path_dist = path + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') \
#                             + '_tra_' + str(int(degree)) + '_dst_' + str(int(dist)) + '_max_' + str(int(step)) \
#                             + 'tis' + str(time_s) + '.png'
#                 Image.fromarray(image_with_line).save(path_dist)
#
#             operation_time = time.time() - st
#             degree = float(degree)
#             step = float(step)
#             row = [float(dist), degree, step, direction, time_s, dis, deg, cha, operation_time]
#             row_df = pd.DataFrame([row], columns=columns)
#             df = df.append(row_df)
#         last_dist = dist
#
#     # keyboard.press_and_release('esc')
#     dx = np.linspace(0, len(df['dis']) - 1, len(df['dis']))
#
#     pass
#     plt.plot(dx, df['dis'])
#     plt.plot(dx, df['cha'])


if __name__ == '__main__':
    run()

