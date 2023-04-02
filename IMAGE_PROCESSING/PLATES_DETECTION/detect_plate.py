import copy
import datetime
import os
import cv2
from PIL import Image

from CONFIG.config import steps, height_step, bottom_dist
from SUPPORT.process_results import prepare_dir
from draw import draw_lane_and_plates
from find_edge import find_curvy_edge


def detect_plates(image):
    plates_positions = []
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
    img_with_contours_filtered = cv2.drawContours(img, contours_filtered, -1, (0, 255, 0), 1)
    # cv2.imshow('cnt', img)
    # cv2.waitKey(0)

    if len(contours_filtered) > 0:
        contour_desc = sorted(contours_filtered, key=len, reverse=True)
        for cnt in contour_desc:
            x0, x1 = min(cnt[:, 0, 0]), max(cnt[:, 0, 0])
            y0, y1 = min(cnt[:, 0, 1]), max(cnt[:, 0, 1])
            cnt_width = x1 - x0
            cnt_height = y1 - y0
            ratio = cnt_width / cnt_height
            rectangle_filling_ratio = cv2.contourArea(cnt) / (cnt_height * cnt_width)
            rectangle_perimeter_ratio = cv2.arcLength(cnt, closed=True) / (2 * (cnt_height + cnt_width))

            im_with_count = copy.deepcopy(image_color)
            im_with_count = cv2.drawContours(im_with_count, cnt, -1, (0, 255, 0), 1)
            im_with_count = cv2.rectangle(im_with_count, (x0, y0), (x1, y1), (255, 0, 0), 1)
            if rectangle_filling_ratio > 0.75:
                if 3.75 <= ratio <= 6:
                    pass
                    directory_path = prepare_dir(r'C:\PROGRAMOWANIE\auto_data\photos\plates', hour=False)
                    image_name = datetime.datetime.now().strftime('%H_%M_%S')
                    image_name_params = image_name + '_fill_ratio_' + str(round(rectangle_filling_ratio, 2))
                    image_name_params += '_W_H_ratio_' + str(round(cnt_width / cnt_height, 2))
                    image_name_params += '_per_ratio_' + str(round(rectangle_perimeter_ratio, 2))
                    image_name_params += '.png'
                    Image.fromarray(im_with_count).save(os.path.join(directory_path, image_name_params))
                    image_name += '.png'
                    Image.fromarray(image).save(os.path.join(directory_path, image_name))

                    plates_positions.append((x0, x1, y0, y1))       # todo - y0, y1 measured from top, but should be from bottom?

                    # cv2.imshow('cnt', im_with_count)
                    # cv2.waitKey(0)
    return plates_positions, img_with_contours_filtered


def judge_plates_positions(plates_positions, lane_borders, image=None):
    # if len(plates_positions) > 0:
    #     return None, None
    min_plate_y = 1000
    min_plate_x = 1000
    for plate_position in plates_positions:
        plate_x = (plate_position[0] + plate_position[1]) // 2
        plate_y = (plate_position[2] + plate_position[3]) // 2
        bottom = bottom_dist    # todo: check if ok to change that value later (shallow copy)
        for lane_border in lane_borders:
            if lane_border is not None:
                if bottom <= plate_y < bottom + height_step:
                    if lane_border[0] <= plate_x < lane_border[1]:
                        if plate_y < min_plate_y:
                            min_plate_y = plate_y
                            min_plate_x = plate_x
                bottom += height_step
    image_with_lane_and_plates = None
    if image is not None:
        image_with_lane_and_plates = draw_lane_and_plates(plates_positions, lane_borders, image, min_plate_y, min_plate_x)
    if min_plate_y != 1000:
        return min_plate_y, min_plate_x, image_with_lane_and_plates

    return None, None, image_with_lane_and_plates


if __name__ == '__main__':
    # path = r'C:\PROGRAMOWANIE\auto_data\photos\plates\2022-05-19'
    path = r'C:\PROGRAMOWANIE\auto_data\photos\lc\2022-05-19\19_44_25'

    dists = []
    dist = None
    trans = None
    for path, subdir, files in os.walk(path):
        for file in files:
            if 'raw' in file:
    # for path, subdir, files in os.walk(path):
    #     for file in files:
    #         if file.endswith('.png') and 'ratio' not in file:
                image = cv2.imread(os.path.join(path, file))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # image = image[window_plates['top']: window_plates['top'] + window_plates['height'],
                #         window_plates['left']: window_plates['left'] + window_plates['width']]
                dist, trans, diff, image_with_line, lane_borders, edge_found_status = find_curvy_edge(image,
                                                                                                      last_dist=dist,
                                                                                                      last_trans=trans)
                plates_positions, img_with_contours_filtered = detect_plates(image)
                plate_distance, min_plate_x, image_with_lane_and_plates = judge_plates_positions(plates_positions, lane_borders,
                                                                     image=img_with_contours_filtered)
                pass
