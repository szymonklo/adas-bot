import time
from math import cos, radians

import keyboard

from CONFIG.config import target_distance, keys, tolerance, min_diff, target_degree


def apply_correction(distance, degree, simulate=False):
    deviation = distance / cos(radians(degree)) - target_distance
    deviation_deg = 0#target_degree - degree
    time_s = min(abs(deviation / 500 + deviation_deg / 250), 0.15)
    if deviation > 0:
        direction = 'right'
    else:
        direction = 'left'
    if not simulate and abs(deviation) > tolerance:
        time_s = steer(direction, time_s)
    return direction, time_s


def steer(direction, time_s):
    keyboard.press(keys[direction])
    time.sleep(time_s)
    keyboard.release(keys[direction])

    return time_s
