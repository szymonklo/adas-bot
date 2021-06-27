import time

import keyboard

from CONFIG.config import keys, speed_tolerance_up


def change_speed(target_speed, current_speed):
    # keyboard.press_and_release('esc')
    # if keyboard.is_pressed(keys['up']):
    #     print('was up')
    keyboard.release(keys['up'])
    # if keyboard.is_pressed(keys['down']):
    #     print('was down')
    keyboard.release(keys['down'])
    if current_speed is None:
    #     if keyboard.is_pressed(keys['up']):
    #         keyboard.release(keys['up'])
    #     if keyboard.is_pressed(keys['down']):
    #         keyboard.release(keys['down'])
        return
    # print(current_speed)
    if current_speed <= target_speed:
        keyboard.press(keys['up'])
        print('pressed up')
    elif current_speed > target_speed + speed_tolerance_up:
        keyboard.press(keys['down'])
        print('pressed down')
    else:
        keyboard.release(keys['up'])
        keyboard.release(keys['down'])
