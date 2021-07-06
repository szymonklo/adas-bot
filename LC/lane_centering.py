import time
from math import cos, radians
import keyboard

from CONFIG.config import target_distance, Keys, tolerance, min_diff, target_degree


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
    time_s = min(abs(correction), 0.08)

    if correction > 0:
        direction_key = Keys.right
    else:
        direction_key = Keys.left
    if not simulate:
        steer(direction_key, time_s)
    return direction_key, time_s, dist_correction, degree_correction, change_correction


def steer(direction_key, time_s):
    keyboard.press(direction_key)
    time.sleep(time_s)
    keyboard.release(direction_key)
