import os
import time

import cv2
import keyboard
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def find_speed_ocr(image):
    text_speed = ocr(image)
    try:
        speed = int(text_speed)
        if 10 <= speed <= 180 and speed % 10 == 0:
            return speed
        else:
            return None
    except ValueError:
        return None


def ocr(image):
    # text = pytesseract.image_to_string(image, config='--oem 1 --psm 8 digits')
    # keyboard.press_and_release('esc')
    try:
        text = pytesseract.image_to_string(image, config='-l eng --oem 1 --psm 8 digits')
    except ValueError as e:
        print(str(e))
        print(str(e))


    # keyboard.press_and_release('esc')

    return text


"""ddd
$ tesseract --help-psm
Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.ddd
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line,
       bypassing hacks that are Tesseract-specific.
       
$ tesseract --help-oem
OCR Engine modes:
  0    Legacy engine only.
  1    Neural nets LSTM engine only.
  2    Legacy + LSTM engines.
  3    Default, based on what is available.
  
text_1 = pytesseract.image_to_string(image, lang='eng', config='--psm 10 digits')
ocr_result = pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
ocr_result_2 = pytesseract.image_to_string(image, lang='eng',
                                         config='--psm 10 -c tessedit_char_whitelist=0123456789')
ocr_result_3 = pytesseract.image_to_string(image, lang='eng',
                                           config='-c tessedit_char_whitelist=0123456789')  
"""

if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\sr\2021-01-18\15_10_03'
    dists = []
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
                st = time.time()
                image = cv2.imread(os.path.join(path, file))
                # speed = pytesseract.image_to_string(os.path.join(path, file), config='--oem 1 --psm 8 digits')
                speed = find_speed_ocr(image)
                print(f'F: {time.time() - st}, speed: {speed}')