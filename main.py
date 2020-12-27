import time

import numpy as np
import cv2
from mss import mss
from PIL import Image
import keyboard


def first_trial():

    window = {
        'left':   0,
        'top':    0,
        'width':  1920,
        'height': 1080
    }
    path = r'C:\PROGRAMOWANIE\auto_data\photos\image2.png'

    while True:  # making a loop
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed

                print('You Pressed A Key!')
                screenshot = mss().grab(window)
                img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
                img.save(path)
                img_array = np.array(img)
                keyboard.press('d')
                time.sleep(1)
                keyboard.release('d')
                keyboard.press('m')
                keyboard.release('m')
                break  # finishing the loop
        except:
            break  # if user pressed a key other than the given key the loop will break

    # cv2.imshow('test', img_array)
    pass


if __name__ == '__main__':
    first_trial()
