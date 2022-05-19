import datetime
import os
import queue
import time

import keyboard
from PIL import Image

from CC.cruise_control import change_speed
from CONFIG.config import window_line, window_speed, Keys, window_signs, window_plates
from IMAGE_PROCESSING.CAPTURING.capture_image import capture_image
from IMAGE_PROCESSING.LINE_DETECTION.find_edge import find_curvy_edge
from IMAGE_PROCESSING.PLATES_DETECTION.detect_plate import detect_plate, judge_plates_positions
from IMAGE_PROCESSING.SIGN_RECOGNITION.sign_recognition import find_circles, find_speed_limit
from IMAGE_PROCESSING.SPEED_DETECTION.detect_speed import find_current_speed
from IMAGE_PROCESSING.image_processing import process_image_to_array, process_image_to_grayscale, filter_image
from LC.lane_centering import apply_correction
from SUPPORT.process_results import process_line_queue, process_signs_queue, prepare_dir, process_plates_queue, \
    process_rejected_queue, process_digits_queue
from ref_digits import init_ref_digits


def run():
    desired_speed = 50
    ref_digits, ref_digits_signs = init_ref_digits()
    plate_distance = None

    while True:
        print('waiting for a key')
        if keyboard.is_pressed('q'):
            line_queue = queue.Queue(50)
            signs_queue = queue.Queue(50)
            plates_queue = queue.Queue(50)
            rejected_queue = queue.Queue(50)
            digit_queue = queue.Queue(50)
            last_dist = None
            last_trans = None
            while True:
                processed_image = None
                if keyboard.is_pressed('z'):
                    keyboard.release(Keys.up)
                    keyboard.release(Keys.down)
                    keyboard.release(Keys.left)
                    keyboard.release(Keys.right)
                    # keyboard.press_and_release('esc')
                    process_line_queue(line_queue, r'C:\PROGRAMOWANIE\auto_data\photos\lc')
                    process_signs_queue(signs_queue, r'C:\PROGRAMOWANIE\auto_data\photos\sr')
                    process_plates_queue(plates_queue, r'C:\PROGRAMOWANIE\auto_data\photos\cc')
                    process_rejected_queue(rejected_queue, r'C:\PROGRAMOWANIE\auto_data\photos\rejected_circles')
                    process_digits_queue(digit_queue, r'C:\PROGRAMOWANIE\auto_data\photos\sign_digits')
                    print('saving completed')
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
                steering_results = activate_steering(last_dist, last_trans)
                lane_borders = steering_results[10]
                last_dist = steering_results[2]
                last_trans = steering_results[3]
                print(f'LC: {time.time() - st_lc}')

                st_cc = time.time()
                speed = activate_speed(desired_speed, ref_digits, plate_distance)
                print(f'CC: {time.time() - st_cc}, speed: {speed}, target_speed: {desired_speed}')

                st_acc = time.time()
                plate_distance, min_plate_x, img_with_contours_filtered = activate_plate(lane_borders)
                print(f'AC: {time.time() - st_acc}, plate_distance: {plate_distance}')

                if line_queue.full():
                    line_queue.get()
                line_queue.put(steering_results)

                if plates_queue.full():
                    plates_queue.get()
                plates_queue.put((plate_distance, min_plate_x, img_with_contours_filtered))

                st_sr = time.time()
                signs_results = activate_signs(ref_digits_signs)
                x, y, w, h, sign_image, desired_speed_found, rejected, result_images_list = signs_results

                if rejected:
                    for rejected_circle in rejected:
                        if rejected_queue.full():
                            rejected_queue.get()
                        rejected_queue.put(rejected_circle)
                if result_images_list:
                    for digit_image in result_images_list:
                        if digit_queue.full():
                            digit_queue.get()
                        digit_queue.put(digit_image)
                if desired_speed_found is not None:
                    desired_speed = desired_speed_found
                    if signs_queue.full():
                        signs_queue.get()
                    signs_queue.put(signs_results[:-2])
                print(f'SR: {time.time() - st_sr}, x: {x}, y: {y}, w: {w}, h: {h}, speed_limit: {desired_speed_found}')


def activate_plate(lane_borders):
    # lane width 300 (step 0)
    # lane width 150 (step 6) -> -25/step
    captured_image = capture_image(window_line)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    plates_positions, img_with_contours_filtered = detect_plate(processed_image)
    plate_distance, min_plate_x = judge_plates_positions(plates_positions, lane_borders, image=processed_image)

    return plate_distance, min_plate_x, img_with_contours_filtered


def activate_steering(last_dist=None, last_trans=None):
    captured_image = capture_image(window_line)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    # dist, trans, diff, image_with_line = find_edge(processed_image, save=False, last_dist=last_dist)
    dist, trans, diff, image_with_line, lane_borders, edge_found_status = find_curvy_edge(processed_image, save=False,
                                                                                          last_dist=last_dist,
                                                                                          last_trans=last_trans)
    if edge_found_status:
        direction, time_s, dist_cor, degree_cor, change_cor = apply_correction(dist, trans, last_dist, simulate=False)
    else:
        direction, time_s, dist_cor, degree_cor, change_cor = None, None, None, None, None

    return processed_image, image_with_line, dist, trans, diff, dist_cor, degree_cor, change_cor, direction, time_s, lane_borders, edge_found_status


def activate_speed(target_speed, ref_digits, plate_distance):
    captured_image = capture_image(window_speed)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    # binary_image = binarize(processed_image)
    # keyboard.press_and_release('esc')
    current_speed, result_images_list = find_current_speed(processed_image, ref_digits)
    change_speed(target_speed, current_speed, plate_distance)
    return current_speed


def activate_signs(ref_digits_signs):
    captured_image = capture_image(window_signs)
    # keyboard.press_and_release('esc')
    processed_image = process_image_to_array(captured_image)
    mask, image = filter_image(processed_image)
    x, y, w, h, sign_image, rejected = find_circles(mask, image)
    # sign_image = image[y: y + h, x: x + w, :]
    # binary_image = binarize(processed_image)
    # keyboard.press_and_release('esc')
    target_speed = None
    result_images_list = []
    if sign_image is not None:
        target_speed, result_images_list = find_speed_limit(sign_image, ref_digits_signs)
    return x, y, w, h, sign_image, target_speed, rejected, result_images_list


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

