import numpy as np
import cv2
from PIL import Image


def process_image(image):
    processed_image_1 = Image.frombytes("RGB", (image.width, image.height), image.rgb)
    processed_image_2 = np.array(processed_image_1)
    processed_image = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_RGB2GRAY)

    # hsv = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)
    # h = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 0]
    # s = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 1]
    # v = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HSV)[:, :, 2]

    # hsl = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HLS)
    # l = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_BGR2HLS)[:, :, 1]
    return processed_image


def binarize(image):
    ret, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    return binary_image



if __name__ == '__main__':
    # todo - implement
    pass