import time

import keyboard

from CONFIG.config import Keys, speed_tolerance_up, target_plate_distance


def change_speed(target_speed, current_speed, plate_distance, last_speed=None):
    if plate_distance is not None:
        if plate_distance < target_plate_distance:
            keyboard.press(Keys.down)
            return 0
    keyboard.release(Keys.up)
    keyboard.release(Keys.down)
    if current_speed is None:
        return 0
    speed_deviation = current_speed - target_speed
    speed_deviation_correction = 0.03 * abs(speed_deviation)
    acceleration_correction = 0
    if last_speed is not None:
        acceleration_correction = - 0.1 * (current_speed - last_speed)
    correction = max(0, speed_deviation_correction + acceleration_correction)

    if speed_deviation <= -10:
        keyboard.press(Keys.up)
        return 1
    elif speed_deviation <= 0:
        keyboard.press(Keys.up)
        keyboard.call_later(keyboard.release, Keys.up, correction)
        return 0.05 * abs(speed_deviation)
    elif speed_deviation > speed_tolerance_up:
        keyboard.press(Keys.down)
        return 0
    else:
        keyboard.release(Keys.up)
        keyboard.release(Keys.down)
        return 0
