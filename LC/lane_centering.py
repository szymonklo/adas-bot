import time
import keyboard

from CONFIG.config import target_distance, keys


def apply_correction(distance, simulate=False):
    deviation = distance - target_distance
    time_s = abs(deviation / 200)
    if deviation > 0:
        direction = 'right'
    else:
        direction = 'left'
    if not simulate:
        time_s = steer(direction, time_s)
    return direction, time_s


def steer(direction, time_s):
    keyboard.press(keys[direction])
    time.sleep(time_s)
    keyboard.release(keys[direction])

    return time_s
