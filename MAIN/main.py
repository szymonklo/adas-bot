import time
import keyboard

from CC.cruise_control import change_speed
from CONFIG.config import window_line, window_speed, Keys, window_signs
from IMAGE_PROCESSING.CAPTURING.capture_image import capture_image
from IMAGE_PROCESSING.LINE_DETECTION.find_edge import find_curvy_edge
from process_results import Edge_results
from IMAGE_PROCESSING.PLATES_DETECTION.detect_plate import detect_plates, judge_plates_positions
from IMAGE_PROCESSING.SIGN_RECOGNITION.sign_recognition import find_circles, find_speed_limit
from IMAGE_PROCESSING.SPEED_DETECTION.detect_speed import find_digits_and_speed
from IMAGE_PROCESSING.image_processing import process_image_to_array, process_image_to_grayscale, filter_image
from LC.lane_centering import steer
from SUPPORT.process_results import Results, Line_result
from ref_digits import init_ref_digits


def run():
    speed_limit = 50
    ref_digits, ref_digits_signs = init_ref_digits()
    waiting = False

    while True:
        if not waiting:
            print('ready...')
            waiting = True
        if keyboard.is_pressed('q'):
            waiting = False
            line_results = Line_result('lc')
            signs_queue = Results('sr')
            plates_queue = Results('cc')
            current_speed_queue = Results('cs')
            current_digit_queue = Results('speedometer_digits')
            rejected_queue = Results('rejected_circles')
            digit_queue = Results('sign_digits')
            last_dist = None
            last_trans = None
            last_speed = None
            while True:
                if keyboard.is_pressed('z'):
                    keyboard.release(Keys.up)
                    keyboard.release(Keys.down)
                    keyboard.release(Keys.left)
                    keyboard.release(Keys.right)
                    # keyboard.press_and_release('esc')
                    line_results.process()
                    signs_queue.process()
                    plates_queue.process()
                    current_speed_queue.process()
                    current_digit_queue.process()
                    rejected_queue.process()
                    digit_queue.process()
                    print('saving completed')
                    break
                if keyboard.is_pressed('a') or keyboard.is_pressed('d') or keyboard.is_pressed('s'):
                    break
                # todo - if indicators pressed change line (turn off, arrow dir1 for 1 s, arrow dir2 for 1 s, turn on)

                st_step = time.time()

                st_lc = time.time()
                line_results = find_lane_border(line_results, last_dist, last_trans)
                # last_dist, last_trans, processed_image_lane, dist, trans, diff, image_with_line, lane_borders, edge_found_status = lane_border_results
                print(f'-LC: {round(time.time() - st_lc, 3)}, dist: {line_results.current().dist}, trans: {line_results.current().trans}')

                st_st = time.time()
                steering_results = steer(line_results, simulate=False)
                direction, time_s, dist_cor, degree_cor, change_cor = steering_results
                print(f'--STEER: {direction} for {round(time_s, 3)} seconds, {round(time.time() - st_st, 3)}, dist_cor: {round(dist_cor, 3)}, change_cor: {round(change_cor, 3)}')

                st_acc = time.time()
                # check if it is the same
                lane_borders = line_results.current().lane_borders
                plate_results = find_target(lane_borders)
                lane_borders, processed_image_lane, plates_positions, img_with_contours_filtered, plate_distance, min_plate_x, image_with_lane_and_plates = plate_results
                print(f'-AC: {round(time.time() - st_acc, 3)}, plate_distance: {plate_distance}')

                st_cs = time.time()
                current_speed_results = find_current_speed(speed_limit, ref_digits, plate_distance)
                speed_limit, ref_digits, plate_distance, processed_image_lane, current_speed, result_images_list = current_speed_results
                print(f'-CS: {round(time.time() - st_cs, 3)}, current speed: {current_speed}, speed_limit: {speed_limit}')

                st_cc = time.time()
                speed_increase = change_speed(speed_limit, current_speed, plate_distance, last_speed=last_speed)
                print(f'--CC: {round(time.time() - st_cc, 3)}, speed_increase: {round(speed_increase, 3)}')

                st_sr = time.time()
                signs_results = find_sign(ref_digits_signs)
                ref_digits_signs, mask, image, x, y, w, h, sign_image, rejected, speed_limit_found, digit_images_list = signs_results
                print(f'-SR: {round(time.time() - st_sr, 3)}, speed_limit: {speed_limit_found}')

                last_dist = line_results.current().dist
                last_trans = line_results.current().trans

                plates_queue.add_result(plate_results)
                current_speed_queue.add_result(current_speed_results)
                current_digit_queue.add_result(result_images_list)

                if current_speed is not None:
                    last_speed = current_speed

                if speed_limit_found:
                    signs_queue.add_result(signs_results)

                rejected_queue.add_result(rejected)
                digit_queue.add_result(digit_images_list)

                print(f'STEP: {round(time.time() - st_step, 3)}')


def find_lane_border(line_results, last_dist=None, last_trans=None):
    captured_image = capture_image(window_line)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    edge_results = find_curvy_edge(processed_image, last_dist=last_dist, last_trans=last_trans)
    line_results.add_result(edge_results)
    return line_results


def find_target(lane_borders, processed_image_lane=None):
    if processed_image_lane is None:
        captured_image = capture_image(window_line)
        processed_image = process_image_to_array(captured_image)
        processed_image = process_image_to_grayscale(processed_image)
    else:
        processed_image = processed_image_lane
    plates_positions, img_with_contours_filtered = detect_plates(processed_image)
    plate_distance, min_plate_x, image_with_lane_and_plates = judge_plates_positions(plates_positions, lane_borders, image=img_with_contours_filtered)

    return lane_borders, processed_image, plates_positions, img_with_contours_filtered, plate_distance, min_plate_x, image_with_lane_and_plates


def find_current_speed(speed_limit, ref_digits, plate_distance):
    captured_image = capture_image(window_speed)
    processed_image = process_image_to_array(captured_image)
    processed_image = process_image_to_grayscale(processed_image)
    current_speed, result_images_list = find_digits_and_speed(processed_image, ref_digits)

    return speed_limit, ref_digits, plate_distance, processed_image, current_speed, result_images_list


def find_sign(ref_digits_signs):
    captured_image = capture_image(window_signs)
    processed_image = process_image_to_array(captured_image)
    mask, image = filter_image(processed_image)
    x, y, w, h, sign_image, rejected = find_circles(mask, image)
    speed_limit_found, digit_images_list = find_speed_limit(sign_image, ref_digits_signs)
    return ref_digits_signs, mask, image, x, y, w, h, sign_image, rejected, speed_limit_found, digit_images_list


if __name__ == '__main__':
    run()
