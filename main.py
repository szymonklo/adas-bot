# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import cv2
from mss import mss
from PIL import Image
import keyboard


def print_hi(name):
    # mon = {'top': 160, 'left': 160, 'width': 200, 'height': 200}
    #
    # sct = mss()
    #
    # while 1:
    #     sct.get_pixels(mon)
    #     img = Image.frombytes('RGB', (sct.width, sct.height), sct.image)
    #     cv2.imshow('test', np.array(img))
    #     if cv2.waitKey(25) & 0xFF == ord('q'):
    #         cv2.destroyAllWindows()
    #         break

    window = {
        'left':   0,
        'top':    0,
        'width':  1920,
        'height': 1080
    }

    screenshot = mss().grab(window)
    img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
    img_array = np.array(img)
    # cv2.imshow('test', img_array)
    pass

    # while True:  # making a loop
    #     try:  # used try so that if user pressed other than the given key error will not be shown
    #         if keyboard.is_pressed('q'):  # if key 'q' is pressed
    #             print('You Pressed A Key!')
    #
    #             break  # finishing the loop
    #     except:
    #         break  # if user pressed a key other than the given key the loop will break
    # # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
