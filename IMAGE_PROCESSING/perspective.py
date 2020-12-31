import cv2
import numpy as np
from matplotlib import pyplot as plt

from CONFIG.config import points_before_transform, points_after_transform, x_size, y_size, y_min, y_max, x_min, x_max, \
    x_margin
from IMAGE_PROCESSING.find_edge import find_vertical_edge


def perspective(raw):
    pts1 = np.float32(points_before_transform)
    pts2 = np.float32(points_after_transform)

    M = cv2.getPerspectiveTransform(pts1, pts2)

    processed = cv2.warpPerspective(raw, M, (x_size + 2 * x_margin, y_size))

    # plt.subplot(121), plt.imshow(image), plt.title('Input')
    # plt.subplot(122), plt.imshow(dst), plt.title('Output')
    # plt.imshow(processed)
    # plt.show()

    return processed

    # find_vertical_edge(raw, processed)


if __name__ == '__main__':
    # image = cv2.imread(r'C:\PROGRAMOWANIE\auto_data\photos\image001.png')[:, :, 0]
    # a=np.min(image)
    # b=np.max(image)
    image = cv2.imread(r'C:\PROGRAMOWANIE\auto_data\photos\image001.png', cv2.IMREAD_GRAYSCALE)
    # c=np.min(image)
    # d=np.max(image)
    image_cropped = image[y_min: y_max,
                          x_min - x_margin: x_max + x_margin]

    perspective(image_cropped)
