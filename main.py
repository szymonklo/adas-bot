# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import cv2
from mss import mss
from PIL import Image
import keyboard
from pynput.keyboard import Key, Controller


def first_trial():

    window = {
        'left':   0,
        'top':    0,
        'width':  1920,
        'height': 1080
    }

    keyboard_simulated = Controller()

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed

                print('You Pressed A Key!')
                screenshot = mss().grab(window)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
                img_array = np.array(img)

                keyboard_simulated.press("a")
                keyboard_simulated.press("b")

                keyboard_simulated.release("a")
                keyboard_simulated.release("b")

                break  # finishing the loop
        except:
            break  # if user pressed a key other than the given key the loop will break

    # cv2.imshow('test', img_array)
    pass


if __name__ == '__main__':
    first_trial()
