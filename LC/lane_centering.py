import time
from math import cos, radians
import keyboard

from CONFIG.config import target_distance, keys, tolerance, min_diff, target_degree


def apply_correction(distance, degree, last_distance, simulate=False):
    if last_distance is not None:
        change_dist = distance - last_distance
    else:
        change_dist = 0
    deviation = distance - target_distance
    deviation_deg = degree - target_degree

    # # coefficients when saving images
    # dist_correction = deviation * 1 / 1000
    # degree_correction = 0#deviation_deg * 2 / 1000
    # change_correction = change_dist * 4 / 1000

    # coefficients when not saving images
    dist_correction = deviation * 0.2 / 1000
    degree_correction = 0#deviation_deg * 2 / 1000
    change_correction = change_dist * 2 / 1000

    correction = dist_correction + degree_correction + change_correction
    time_s = min(abs(correction), 0.05)

    if correction > 0:
        direction = 'right'
    else:
        direction = 'left'
    if not simulate:
        steer(direction, time_s)
    return direction, time_s, dist_correction, degree_correction, change_correction


def steer(direction, time_s):
    keyboard.press(keys[direction])
    time.sleep(time_s)
    keyboard.release(keys[direction])
