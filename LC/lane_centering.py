import time
import keyboard

from CONFIG.config import target_distance, keys, tolerance, min_diff


def apply_correction(distance, simulate=False):
    deviation = distance - target_distance
    time_s = min(abs(deviation / 1000), 0.1)
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
