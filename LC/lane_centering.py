import time
import keyboard

from CONFIG.config import target_distance, keys, tolerance, min_diff


def apply_correction(distance, max_diff, simulate=False):
    deviation = distance - target_distance
    time_s = max(abs(deviation / 5000), 0.1)
    if deviation > 0:
        direction = 'right'
    else:
        direction = 'left'
    if not simulate and abs(deviation) > tolerance and max_diff > min_diff:
        time_s = steer(direction, time_s)
    return direction, time_s


def steer(direction, time_s):
    keyboard.press(keys[direction])
    time.sleep(time_s)
    keyboard.release(keys[direction])

    return time_s
