import copy
import datetime
import os
import cv2
from PIL import Image

from CONFIG.config import window_plates
from SUPPORT.process_results import prepare_dir


def detect_plate(image):
    # # Set up the detector with default parameters.
    # detector = cv2.SimpleBlobDetector()
    # # Detect blobs.
    # keypoints = detector.detect(image)
    # # Draw detected blobs as red circles.
    # # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    # im_with_keypoints = cv2.drawKeypoints(image, keypoints, image.array([]), (0, 0, 255),
    #                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # # Show keypoints
    # cv2.imshow("Keypoints", im_with_keypoints)
    # cv2.waitKey(0)

    ret, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours_filtered = [cnt for cnt in contours if cnt.shape[0] > 30]

    image_color = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    img = copy.deepcopy(image_color)
    img = cv2.drawContours(img, contours_filtered, -1, (0, 255, 0), 1)
    # cv2.imshow('cnt', img)
    # cv2.waitKey(0)

    if len(contours_filtered) > 0:
        contour_desc = sorted(contours_filtered, key=len, reverse=True)
        for cnt in contour_desc:
            x0, x1 = min(cnt[:, 0, 0]), max(cnt[:, 0, 0])
            y0, y1 = min(cnt[:, 0, 1]), max(cnt[:, 0, 1])
            cnt_width = x1 - x0
            cnt_height = y1 - y0
            rectangle_filling_ratio = cv2.contourArea(cnt) / (cnt_height * cnt_width)

            im_with_count = copy.deepcopy(image_color)
            im_with_count = cv2.drawContours(im_with_count, cnt, -1, (0, 255, 0), 1)
            im_with_count = cv2.rectangle(im_with_count, (x0, y0), (x1, y1), (255, 0, 0), 1)
            if rectangle_filling_ratio > 0.8:
                if 3.75 <= cnt_width / cnt_height <= 5.5:
                    pass
                    directory_path = prepare_dir(r'C:\PROGRAMOWANIE\auto_data\photos\plates', hour=False)
                    image_name = datetime.datetime.now().strftime('%H_%M_%S')
                    image_name_params = image_name + '_fill_ratio_' + str(round(rectangle_filling_ratio, 2))
                    image_name_params += '_W_H_ratio_' + str(round(cnt_width / cnt_height, 2))
                    image_name_params += '.png'
                    Image.fromarray(im_with_count).save(os.path.join(directory_path, image_name_params))
                    image_name += '.png'
                    Image.fromarray(image).save(os.path.join(directory_path, image_name))

                    # cv2.imshow('cnt', im_with_count)
                    # cv2.waitKey(0)


if __name__ == '__main__':
    path = r'C:\PROGRAMOWANIE\auto_data\photos\plates\2021-06-30'
    for path, subdir, files in os.walk(path):
        for file in files:
            if file.endswith('.png') and 'ratio' not in file:
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # image = image[window_plates['top']: window_plates['top'] + window_plates['height'],
                #         window_plates['left']: window_plates['left'] + window_plates['width']]
                detect_plate(image)
