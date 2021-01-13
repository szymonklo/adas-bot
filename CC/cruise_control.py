import time

import keyboard

from CONFIG.config import keys, speed_tolerance_up


def change_speed(target_speed, current_speed):
    if current_speed is None:
        if keyboard.is_pressed(keys['up']):
            keyboard.release(keys['up'])
        elif keyboard.is_pressed(keys['down']):
            keyboard.release(keys['down'])
        return
    # print(current_speed)
    if current_speed <= target_speed:
        keyboard.press(keys['up'])
    elif current_speed > target_speed + speed_tolerance_up:
        keyboard.press(keys['down'])
    else:
        keyboard.release(keys['up'])
        keyboard.release(keys['down'])
